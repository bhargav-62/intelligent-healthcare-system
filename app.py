import os
from pathlib import Path
from datetime import datetime, timezone
import re

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from flask_cors import CORS

from db import get_db_connection
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MODEL_PATH = BASE_DIR / "models" / "baseline_symptom_model.joblib"

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Local HTTP development only

CORS(app)
@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({
        "success": False,
        "message": "Request body is too large. Maximum size is 1 MB."
    }), 413

model = None
feature_names = []
model_classes = []

try:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run train_baseline.py first."
        )

    model = joblib.load(MODEL_PATH)

    if not hasattr(model, "feature_names_in_"):
        raise RuntimeError("Model feature names are missing.")

    feature_names = list(model.feature_names_in_)
    model_classes = [str(value) for value in model.classes_]

    print(f"Loaded model: {MODEL_PATH}")
    print(f"Expected symptom features: {len(feature_names)}")
    print(f"Available disease classes: {len(model_classes)}")

except Exception as exc:
    print(f"Model loading failed: {type(exc).__name__}: {exc}")


SECTION_PAGES = {
    "appointments": {
        "title": "Appointments",
        "subtitle": "Appointment management",
        "icon": "▣",
        "description": "Create and manage appointments linked to registered patients.",
        "features": ["Appointment booking", "Scheduling and status tracking"],
    },
    "records": {
        "title": "Health Records",
        "subtitle": "Patient health records",
        "icon": "▤",
        "description": "View and manage records linked to registered patients.",
        "features": ["Patient-linked records", "Record history"],
    },
    "treatments": {
        "title": "Treatments",
        "subtitle": "Treatment information",
        "icon": "✚",
        "description": "This section is an informational preview. It does not prescribe treatment.",
        "features": ["Educational information", "Future clinician-reviewed workflows"],
    },
    "medications": {
        "title": "Medications",
        "subtitle": "Medication information",
        "icon": "♧",
        "description": "This section does not recommend medicines or dosages.",
        "features": ["Medication interface preview", "Future secure medication records"],
    },
    "reports": {
        "title": "Reports",
        "subtitle": "Project reports",
        "icon": "▧",
        "description": "Reporting functionality will be connected to saved records in a later step.",
        "features": ["Record summaries", "Future export functionality"],
    },
    "analytics": {
        "title": "Analytics",
        "subtitle": "Application analytics",
        "icon": "▥",
        "description": "Live patient and appointment analytics will be connected in a later step.",
        "features": ["Patient totals", "Appointment totals"],
    },
    "alerts": {
        "title": "Alerts",
        "subtitle": "Application notifications",
        "icon": "♧",
        "description": "This prototype is not an emergency alert or patient-monitoring service.",
        "features": ["Notification interface preview"],
    },
    "messages": {
        "title": "Messages",
        "subtitle": "Messaging",
        "icon": "✉",
        "description": "Messaging is not yet connected to an email, SMS, or healthcare messaging service.",
        "features": ["Messaging interface preview"],
    },
    "settings": {
        "title": "Settings",
        "subtitle": "Application settings",
        "icon": "⚙",
        "description": "Account management and preferences are not implemented yet.",
        "features": ["Application information"],
    },
}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("home"))
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if (
        not email
        or len(email) > 255
        or not password
        or len(password) > 128
    ):
        return render_template(
            "login.html",
            error="Invalid email or password.",
        ), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, full_name, email, password_hash, role, is_active
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email,),
            )
            user = cursor.fetchone()

        if (
            not user
            or not user["is_active"]
            or not check_password_hash(user["password_hash"], password)
        ):
            return render_template(
                "login.html",
                error="Invalid email or password.",
            ), 401

        session.clear()
        session["user_id"] = user["user_id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        return redirect(url_for("home"))

    except Exception:
        app.logger.exception("Login failed due to a server error")
        return render_template(
            "login.html",
            error="Unable to sign in right now. Please try again.",
        ), 500

    finally:
        if connection:
            connection.close()


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    symptoms = [
        {
            "name": name,
            "label": name.replace("_", " ").strip().capitalize(),
        }
        for name in feature_names
    ]

    return render_template(
        "index.html",
        symptoms=symptoms,
        model_loaded=model is not None,
        today=datetime.now().strftime("%d %b %Y"),
    )


# --------------------------------------------------
# PATIENT PAGE AND API
# --------------------------------------------------

@app.route("/patients")
def patients():
    return render_template("patients.html")


def validate_patient_payload(data, partial=False):
    if not isinstance(data, dict):
        return None, "Send a JSON object."

    allowed = {
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "phone",
        "email",
        "address",
    }

    if set(data.keys()) - allowed:
        return None, "The request contains unsupported fields."

    cleaned = {}

    for field in allowed:
        value = data.get(field)

        if value is None:
            cleaned[field] = None
        elif not isinstance(value, str):
            return None, f"{field} must be text."
        else:
            value = value.strip()
            cleaned[field] = value or None

    if not partial or "first_name" in data:
        if not cleaned.get("first_name"):
            return None, "First name is required."

    if not partial or "last_name" in data:
        if not cleaned.get("last_name"):
            return None, "Last name is required."

    for field in ("first_name", "last_name"):
        value = cleaned.get(field)
        if value and len(value) > 100:
            return None, f"{field} must be at most 100 characters."

    if cleaned.get("gender") and len(cleaned["gender"]) > 30:
        return None, "Gender must be at most 30 characters."

    if cleaned.get("phone") and len(cleaned["phone"]) > 20:
        return None, "Phone must be at most 20 characters."

    if cleaned.get("email"):
        if len(cleaned["email"]) > 255 or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            cleaned["email"],
        ):
            return None, "Enter a valid email address."

    if cleaned.get("address") and len(cleaned["address"]) > 5000:
        return None, "Address is too long."

    dob = cleaned.get("date_of_birth")
    if dob:
        try:
            parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            if parsed > datetime.now().date():
                return None, "Date of birth cannot be in the future."
            cleaned["date_of_birth"] = parsed.isoformat()
        except ValueError:
            return None, "Date of birth must use YYYY-MM-DD."

    return cleaned, None


@app.route("/api/patients", methods=["GET"])
def get_patients():
    search = request.args.get("search", "").strip()

    if len(search) > 100:
        return jsonify({
            "success": False,
            "message": "Search text is too long.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            if search:
                term = f"%{search}%"
                cursor.execute(
                    """
                    SELECT patient_id, patient_code, first_name, last_name,
                           date_of_birth, gender, phone, email, address,
                           created_at, updated_at
                    FROM patients
                    WHERE first_name LIKE %s
                       OR last_name LIKE %s
                       OR phone LIKE %s
                       OR email LIKE %s
                       OR patient_code LIKE %s
                    ORDER BY patient_id DESC
                    """,
                    (term, term, term, term, term),
                )
            else:
                cursor.execute(
                    """
                    SELECT patient_id, patient_code, first_name, last_name,
                           date_of_birth, gender, phone, email, address,
                           created_at, updated_at
                    FROM patients
                    ORDER BY patient_id DESC
                    """
                )

            rows = cursor.fetchall()

        for row in rows:
            for field in ("date_of_birth", "created_at", "updated_at"):
                if row.get(field) is not None:
                    row[field] = row[field].isoformat()

        return jsonify({
            "success": True,
            "count": len(rows),
            "patients": rows,
        })

    except Exception:
        app.logger.exception("Could not retrieve patients")
        return jsonify({
            "success": False,
            "message": "Could not retrieve patients. Check the server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.get_json(silent=True)
    patient, error = validate_patient_payload(data)

    if error:
        return jsonify({"success": False, "message": error}), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO patients
                    (first_name, last_name, date_of_birth, gender,
                     phone, email, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    patient["first_name"],
                    patient["last_name"],
                    patient["date_of_birth"],
                    patient["gender"],
                    patient["phone"],
                    patient["email"],
                    patient["address"],
                ),
            )

            patient_id = cursor.lastrowid
            patient_code = f"PAT-{patient_id:06d}"

            cursor.execute(
                """
                UPDATE patients
                SET patient_code = %s
                WHERE patient_id = %s
                """,
                (patient_code, patient_id),
            )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Patient registered successfully.",
            "patient_id": patient_id,
            "patient_code": patient_code,
        }), 201

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not create patient")
        return jsonify({
            "success": False,
            "message": (
                "Could not register the patient. "
                "Check the server log for details."
            ),
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT patient_id, patient_code, first_name, last_name,
                       date_of_birth, gender, phone, email, address,
                       created_at, updated_at
                FROM patients
                WHERE patient_id = %s
                """,
                (patient_id,),
            )
            patient = cursor.fetchone()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found.",
            }), 404

        for field in ("date_of_birth", "created_at", "updated_at"):
            if patient.get(field) is not None:
                patient[field] = patient[field].isoformat()

        return jsonify({"success": True, "patient": patient})

    except Exception:
        app.logger.exception("Could not retrieve patient")
        return jsonify({
            "success": False,
            "message": "Could not retrieve patient.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.get_json(silent=True)
    patient, error = validate_patient_payload(data, partial=True)

    if error:
        return jsonify({"success": False, "message": error}), 400

    if not patient:
        return jsonify({
            "success": False,
            "message": "No patient fields were provided.",
        }), 400

    fields = [
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "phone",
        "email",
        "address",
    ]

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT patient_id FROM patients WHERE patient_id = %s",
                (patient_id,),
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Patient not found.",
                }), 404

            assignments = []
            values = []

            for field in fields:
                if field in data:
                    assignments.append(f"{field} = %s")
                    values.append(patient[field])

            if not assignments:
                return jsonify({
                    "success": False,
                    "message": "No patient fields were provided.",
                }), 400

            values.append(patient_id)

            cursor.execute(
                f"UPDATE patients SET {', '.join(assignments)} "
                "WHERE patient_id = %s",
                tuple(values),
            )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Patient updated successfully.",
        })

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not update patient")
        return jsonify({
            "success": False,
            "message": "Could not update patient.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM patients WHERE patient_id = %s",
                (patient_id,),
            )

            if cursor.rowcount == 0:
                return jsonify({
                    "success": False,
                    "message": "Patient not found.",
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Patient deleted successfully.",
        })

    except Exception as exc:
        if connection:
            connection.rollback()

        # Preserve patients referenced by appointments or records.
        if exc.__class__.__name__ == "IntegrityError":
            return jsonify({
                "success": False,
                "message": (
                    "This patient has linked appointments or health records. "
                    "Remove or archive those linked records first."
                ),
            }), 409

        app.logger.exception("Could not delete patient")
        return jsonify({
            "success": False,
            "message": "Could not delete patient.",
        }), 500

    finally:
        if connection:
            connection.close()


# --------------------------------------------------
# HEALTH RECORDS API
# --------------------------------------------------

@app.route("/api/health-records", methods=["GET"])
def get_health_records():
    search = request.args.get("search", "").strip()

    if len(search) > 100:
        return jsonify({
            "success": False,
            "message": "Search text is too long.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            query = """
                SELECT
                    h.record_id,
                    h.patient_id,
                    p.patient_code,
                    p.first_name,
                    p.last_name,
                    h.record_type,
                    h.title,
                    h.description,
                    h.recorded_at,
                    h.created_at
                FROM health_records h
                INNER JOIN patients p
                    ON p.patient_id = h.patient_id
            """

            parameters = ()

            if search:
                term = f"%{search}%"
                query += """
                    WHERE p.patient_code LIKE %s
                       OR p.first_name LIKE %s
                       OR p.last_name LIKE %s
                       OR h.record_type LIKE %s
                       OR h.title LIKE %s
                       OR h.description LIKE %s
                """
                parameters = (
                    term, term, term, term, term, term
                )

            query += """
                ORDER BY h.recorded_at DESC, h.record_id DESC
            """

            cursor.execute(query, parameters)
            rows = cursor.fetchall()

        for row in rows:
            for field in ("recorded_at", "created_at"):
                value = row.get(field)
                if value is not None and hasattr(value, "isoformat"):
                    row[field] = value.isoformat()

        return jsonify({
            "success": True,
            "count": len(rows),
            "records": rows,
        })

    except Exception:
        app.logger.exception("Could not retrieve health records")
        return jsonify({
            "success": False,
            "message": "Could not retrieve health records. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/health-records", methods=["POST"])
def create_health_record():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Send a JSON object.",
        }), 400

    allowed = {
        "patient_id", "record_type", "title",
        "description", "recorded_at",
    }

    if set(data.keys()) - allowed:
        return jsonify({
            "success": False,
            "message": "The request contains unsupported fields.",
        }), 400

    try:
        patient_id = data.get("patient_id")

        if isinstance(patient_id, bool):
            raise ValueError

        patient_id = int(patient_id)

        if patient_id < 1:
            raise ValueError

        record_type = data.get("record_type")
        title = data.get("title")
        description = data.get("description", "")

        if not isinstance(record_type, str) or not record_type.strip():
            raise ValueError("Record type is required.")

        if len(record_type.strip()) > 100:
            raise ValueError("Record type must be at most 100 characters.")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required.")

        if len(title.strip()) > 200:
            raise ValueError("Title must be at most 200 characters.")

        if description is not None and not isinstance(description, str):
            raise ValueError("Description must be text.")

        if description and len(description) > 65535:
            raise ValueError("Description is too long.")

        recorded_at = data.get("recorded_at")

        if recorded_at:
            if not isinstance(recorded_at, str):
                raise ValueError("Record date must be valid.")

            try:
                parsed = datetime.fromisoformat(recorded_at)
                recorded_at = parsed.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("Record date must be valid.")

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc) or "Select a valid patient.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT patient_id FROM patients WHERE patient_id = %s",
                (patient_id,),
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "The selected patient does not exist.",
                }), 400

            if recorded_at:
                cursor.execute(
                    """
                    INSERT INTO health_records
                        (patient_id, record_type, title, description, recorded_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        patient_id, record_type.strip(), title.strip(),
                        description or None, recorded_at,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO health_records
                        (patient_id, record_type, title, description)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        patient_id, record_type.strip(), title.strip(),
                        description or None,
                    ),
                )

            record_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Health record created successfully.",
            "record_id": record_id,
        }), 201

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not create health record")
        return jsonify({
            "success": False,
            "message": "Could not create health record. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/health-records/<int:record_id>", methods=["PUT"])
def update_health_record(record_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "success": False,
            "message": "Send a non-empty JSON object.",
        }), 400

    allowed = {
        "patient_id", "record_type", "title",
        "description", "recorded_at",
    }

    if set(data.keys()) - allowed:
        return jsonify({
            "success": False,
            "message": "The request contains unsupported fields.",
        }), 400

    fields = []
    values = []

    try:
        if "patient_id" in data:
            if isinstance(data["patient_id"], bool):
                raise ValueError("Select a valid patient.")

            patient_id = int(data["patient_id"])

            if patient_id < 1:
                raise ValueError("Select a valid patient.")

            fields.append("patient_id = %s")
            values.append(patient_id)

        if "record_type" in data:
            value = data["record_type"]

            if not isinstance(value, str) or not value.strip():
                raise ValueError("Record type is required.")

            if len(value.strip()) > 100:
                raise ValueError("Record type must be at most 100 characters.")

            fields.append("record_type = %s")
            values.append(value.strip())

        if "title" in data:
            value = data["title"]

            if not isinstance(value, str) or not value.strip():
                raise ValueError("Title is required.")

            if len(value.strip()) > 200:
                raise ValueError("Title must be at most 200 characters.")

            fields.append("title = %s")
            values.append(value.strip())

        if "description" in data:
            value = data["description"]

            if value is not None and not isinstance(value, str):
                raise ValueError("Description must be text.")

            if value and len(value) > 65535:
                raise ValueError("Description is too long.")

            fields.append("description = %s")
            values.append(value or None)

        if "recorded_at" in data:
            value = data["recorded_at"]

            if value is None or value == "":
                fields.append("recorded_at = %s")
                values.append(None)
            else:
                if not isinstance(value, str):
                    raise ValueError("Record date must be valid.")

                try:
                    parsed = datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError("Record date must be valid.")

                fields.append("recorded_at = %s")
                values.append(parsed.strftime("%Y-%m-%d %H:%M:%S"))

        if not fields:
            raise ValueError("No record fields were provided.")

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc) or "Invalid record data.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT record_id FROM health_records WHERE record_id = %s",
                (record_id,),
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Health record not found.",
                }), 404

            if "patient_id" in data:
                cursor.execute(
                    "SELECT patient_id FROM patients WHERE patient_id = %s",
                    (int(data["patient_id"]),),
                )

                if not cursor.fetchone():
                    return jsonify({
                        "success": False,
                        "message": "The selected patient does not exist.",
                    }), 400

            values.append(record_id)

            cursor.execute(
                f"UPDATE health_records SET {', '.join(fields)} "
                "WHERE record_id = %s",
                tuple(values),
            )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Health record updated successfully.",
        })

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not update health record")
        return jsonify({
            "success": False,
            "message": "Could not update health record. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/health-records/<int:record_id>", methods=["DELETE"])
def delete_health_record(record_id):
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM health_records WHERE record_id = %s",
                (record_id,),
            )

            if cursor.rowcount == 0:
                return jsonify({
                    "success": False,
                    "message": "Health record not found.",
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Health record deleted successfully.",
        })

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not delete health record")
        return jsonify({
            "success": False,
            "message": "Could not delete health record. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()

@app.route("/api/dashboard/upcoming-appointments", methods=["GET"])
def dashboard_upcoming_appointments():
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.reason,
                    a.clinician_name,
                    a.status,
                    p.patient_code,
                    p.first_name,
                    p.last_name
                FROM appointments a
                INNER JOIN patients p
                    ON p.patient_id = a.patient_id
                WHERE a.status = 'Scheduled'
                  AND TIMESTAMP(
                      a.appointment_date,
                      a.appointment_time
                  ) >= NOW()
                ORDER BY a.appointment_date, a.appointment_time
                LIMIT 5
            """)

            appointments = cursor.fetchall()

        for appointment in appointments:
            for field in ("appointment_date", "appointment_time"):
                value = appointment.get(field)
                if value is not None:
                    if hasattr(value, "total_seconds"):
                        seconds = int(value.total_seconds()) % 86400
                        hours, remainder = divmod(seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        appointment[field] = (
                            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        )
                    elif hasattr(value, "isoformat"):
                        appointment[field] = value.isoformat()

        return jsonify({
            "success": True,
            "count": len(appointments),
            "appointments": appointments,
        })

    except Exception:
        app.logger.exception("Could not retrieve upcoming appointments")
        return jsonify({
            "success": False,
            "message": "Could not retrieve upcoming appointments.",
        }), 500

    finally:
        if connection:
            connection.close()

# --------------------------------------------------
# OTHER SECTION PAGES
# --------------------------------------------------

# --------------------------------------------------
# APPOINTMENTS API
# --------------------------------------------------

APPOINTMENT_STATUSES = {"Scheduled", "Completed", "Cancelled"}


def validate_appointment_payload(data, partial=False):
    """Validate appointment data received from the frontend."""
    if not isinstance(data, dict):
        return None, "Send a JSON object."

    allowed = {
        "patient_id",
        "appointment_date",
        "appointment_time",
        "clinician_name",
        "reason",
        "status",
        "notes",
    }

    if set(data.keys()) - allowed:
        return None, "The request contains unsupported fields."

    if not data:
        return None, "No appointment fields were provided."

    cleaned = {}

    if "patient_id" in data:
        try:
            value = data["patient_id"]
            if isinstance(value, bool):
                raise ValueError
            patient_id = int(value)
            if patient_id < 1:
                raise ValueError
            cleaned["patient_id"] = patient_id
        except (TypeError, ValueError):
            return None, "Select a valid patient."

    elif not partial:
        return None, "Patient is required."

    if "appointment_date" in data:
        value = data["appointment_date"]
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            cleaned["appointment_date"] = parsed_date.isoformat()
        except (TypeError, ValueError):
            return None, "Appointment date must use YYYY-MM-DD."

    elif not partial:
        return None, "Appointment date is required."

    if "appointment_time" in data:
        value = data["appointment_time"]
        try:
            parsed_time = datetime.strptime(value, "%H:%M").time()
            cleaned["appointment_time"] = parsed_time.strftime("%H:%M:%S")
        except (TypeError, ValueError):
            try:
                parsed_time = datetime.strptime(value, "%H:%M:%S").time()
                cleaned["appointment_time"] = parsed_time.strftime("%H:%M:%S")
            except (TypeError, ValueError):
                return None, "Appointment time must use HH:MM or HH:MM:SS."

    elif not partial:
        return None, "Appointment time is required."

    for field, maximum in (
        ("clinician_name", 150),
        ("reason", 255),
        ("notes", 5000),
    ):
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, str):
                return None, f"{field} must be text."

            value = (value or "").strip()
            if len(value) > maximum:
                return None, f"{field} must be at most {maximum} characters."

            cleaned[field] = value or None

    if "status" in data:
        status = data["status"]
        if status not in APPOINTMENT_STATUSES:
            return None, "Status must be Scheduled, Completed, or Cancelled."
        cleaned["status"] = status
    elif not partial:
        cleaned["status"] = "Scheduled"

    return cleaned, None



def serialize_appointment(row):
    """Convert database date/time values into JSON-safe values."""
    from datetime import date, datetime, time, timedelta

    for field in (
        "appointment_date",
        "appointment_time",
        "created_at",
        "updated_at",
    ):
        value = row.get(field)

        if value is None:
            continue

        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds()) % (24 * 60 * 60)
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            row[field] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        elif isinstance(value, (datetime, date, time)):
            row[field] = value.isoformat()

    return row



@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    search = request.args.get("search", "").strip()

    if len(search) > 100:
        return jsonify({
            "success": False,
            "message": "Search text is too long.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            query = """
                SELECT
                    a.appointment_id,
                    a.patient_id,
                    p.patient_code,
                    p.first_name,
                    p.last_name,
                    a.appointment_date,
                    a.appointment_time,
                    a.clinician_name,
                    a.reason,
                    a.status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                INNER JOIN patients p
                    ON p.patient_id = a.patient_id
            """

            parameters = ()

            if search:
                term = f"%{search}%"
                query += """
                    WHERE p.patient_code LIKE %s
                       OR p.first_name LIKE %s
                       OR p.last_name LIKE %s
                       OR a.clinician_name LIKE %s
                       OR a.reason LIKE %s
                       OR a.status LIKE %s
                """
                parameters = (term, term, term, term, term, term)

            query += """
                ORDER BY a.appointment_date DESC,
                         a.appointment_time DESC,
                         a.appointment_id DESC
            """

            cursor.execute(query, parameters)
            rows = cursor.fetchall()

        appointments = [serialize_appointment(row) for row in rows]

        return jsonify({
            "success": True,
            "count": len(appointments),
            "appointments": appointments,
        })

    except Exception:
        app.logger.exception("Could not retrieve appointments")
        return jsonify({
            "success": False,
            "message": "Could not retrieve appointments. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json(silent=True)
    appointment, error = validate_appointment_payload(data)

    if error:
        return jsonify({
            "success": False,
            "message": error,
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT patient_id FROM patients WHERE patient_id = %s",
                (appointment["patient_id"],),
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "The selected patient does not exist.",
                }), 400

            cursor.execute(
                """
                INSERT INTO appointments (
                    patient_id,
                    appointment_date,
                    appointment_time,
                    clinician_name,
                    reason,
                    status,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    appointment["patient_id"],
                    appointment["appointment_date"],
                    appointment["appointment_time"],
                    appointment.get("clinician_name"),
                    appointment.get("reason"),
                    appointment.get("status", "Scheduled"),
                    appointment.get("notes"),
                ),
            )

            appointment_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment created successfully.",
            "appointment_id": appointment_id,
        }), 201

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not create appointment")
        return jsonify({
            "success": False,
            "message": "Could not create appointment. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    data = request.get_json(silent=True)
    appointment, error = validate_appointment_payload(data, partial=True)

    if error:
        return jsonify({
            "success": False,
            "message": error,
        }), 400

    fields = [
        "patient_id",
        "appointment_date",
        "appointment_time",
        "clinician_name",
        "reason",
        "status",
        "notes",
    ]

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT appointment_id FROM appointments WHERE appointment_id = %s",
                (appointment_id,),
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Appointment not found.",
                }), 404

            if "patient_id" in appointment:
                cursor.execute(
                    "SELECT patient_id FROM patients WHERE patient_id = %s",
                    (appointment["patient_id"],),
                )

                if not cursor.fetchone():
                    return jsonify({
                        "success": False,
                        "message": "The selected patient does not exist.",
                    }), 400

            assignments = []
            values = []

            for field in fields:
                if field in appointment:
                    assignments.append(f"{field} = %s")
                    values.append(appointment[field])

            if not assignments:
                return jsonify({
                    "success": False,
                    "message": "No appointment fields were provided.",
                }), 400

            assignments.append("updated_at = CURRENT_TIMESTAMP")
            values.append(appointment_id)

            cursor.execute(
                f"UPDATE appointments SET {', '.join(assignments)} "
                "WHERE appointment_id = %s",
                tuple(values),
            )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment updated successfully.",
        })

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not update appointment")
        return jsonify({
            "success": False,
            "message": "Could not update appointment. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()


@app.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM appointments WHERE appointment_id = %s",
                (appointment_id,),
            )

            if cursor.rowcount == 0:
                return jsonify({
                    "success": False,
                    "message": "Appointment not found.",
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment deleted successfully.",
        })

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Could not delete appointment")
        return jsonify({
            "success": False,
            "message": "Could not delete appointment. Check the Flask server log.",
        }), 500

    finally:
        if connection:
            connection.close()

@app.route("/section/<section_key>")
def section_page(section_key):
    section = SECTION_PAGES.get(section_key)

    if section is None:
        return "Section not found", 404

    return render_template(
        "section.html",
        page=section,
        active_page=section_key,
        model_loaded=model is not None,
        feature_count=len(feature_names),
    )


@app.route("/appointments")
def appointments():
    return render_template("appointments.html")

@app.route("/records")
def records():
    return render_template("health_records.html")


@app.route("/treatments")
def treatments():
    return section_page("treatments")


@app.route("/medications")
def medications():
    return section_page("medications")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/alerts")
def alerts():
    return section_page("alerts")


@app.route("/messages")
def messages():
    return section_page("messages")


@app.route("/settings")
def settings():
    return section_page("settings")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# --------------------------------------------------
# EXISTING AI SYMPTOM EXPLORER
# --------------------------------------------------

@app.route("/ai-insights")
@app.route("/explorer")
@app.route("/diagnostics")
def symptom_explorer():
    symptoms = [
        {
            "name": name,
            "label": name.replace("_", " ").strip().capitalize(),
        }
        for name in feature_names
    ]

    return render_template(
        "symptom_checker.html",
        symptoms=symptoms,
        model_loaded=model is not None,
        today=datetime.now().strftime("%d %b %Y"),
        open_explorer=True,
    )

# --------------------------------------------------
# HEALTH CHECK API
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "feature_count": len(feature_names),
        "message": (
            "Educational prototype only; "
            "not for medical diagnosis or treatment."
        ),
    }), (200 if model is not None else 503)


@app.route("/models", methods=["GET"])
def list_models():
    return jsonify({
        "available_models": (
            ["random_forest_baseline"] if model is not None else []
        ),
        "current_model": "baseline_symptom_model",
        "symptom_features": len(feature_names),
        "disease_classes": len(model_classes),
    })

# --------------------------------------------------
# LIVE DASHBOARD STATISTICS API
# --------------------------------------------------

@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM patients")
            total_patients = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COUNT(*) AS total FROM appointments"
            )
            total_appointments = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COUNT(*) AS total FROM health_records"
            )
            total_health_records = cursor.fetchone()["total"]

            cursor.execute(
                """
                SELECT patient_id, patient_code, first_name, last_name,
                       created_at
                FROM patients
                ORDER BY patient_id DESC
                LIMIT 5
                """
            )
            recent_patients = cursor.fetchall()

        for patient in recent_patients:
            if patient.get("created_at") is not None:
                patient["created_at"] = patient["created_at"].isoformat()

        return jsonify({
            "success": True,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "total_health_records": total_health_records,
            "recent_patients": recent_patients,
        })

    except Exception:
        app.logger.exception("Could not load dashboard statistics")
        return jsonify({
            "success": False,
            "message": "Could not load dashboard statistics.",
        }), 500

    finally:
        if connection:
            connection.close()
# --------------------------------------------------
# EXISTING AI PREDICTION API
# --------------------------------------------------

@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return ("", 204)

    if model is None:
        return jsonify({
            "success": False,
            "message": "The baseline model is unavailable.",
        }), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Send a JSON object containing a symptoms list.",
        }), 400

    selected = data.get("symptoms", [])

    if (
        not isinstance(selected, list)
        or not all(isinstance(s, str) for s in selected)
    ):
        return jsonify({
            "success": False,
            "message": "'symptoms' must be a list of symptom names.",
        }), 400

    if not selected:
        return jsonify({
            "success": False,
            "message": "Select at least one symptom.",
        }), 400

    selected_set = set(selected)
    unknown = sorted(selected_set - set(feature_names))

    if unknown:
        return jsonify({
            "success": False,
            "message": "One or more symptoms are not recognized.",
            "unknown_symptoms": unknown,
        }), 400

    row = {
        name: int(name in selected_set)
        for name in feature_names
    }

    input_df = pd.DataFrame([row], columns=feature_names)

    try:
        predicted_label = str(model.predict(input_df)[0])
        top_predictions = []

        if hasattr(model, "predict_proba"):
            scores = model.predict_proba(input_df)[0]
            order = scores.argsort()[::-1][:5]

            for idx in order:
                top_predictions.append({
                    "disease": str(model.classes_[idx]),
                    "score": round(float(scores[idx]) * 100, 2),
                })
        else:
            top_predictions.append({
                "disease": predicted_label,
                "score": None,
            })

        urgent_symptoms = {
            "difficulty_breathing",
            "chest_pain",
            "slurred_speech",
            "weakness_of_one_body_side",
            "coma",
        }

        return jsonify({
            "success": True,
            "educational_prediction": predicted_label,
            "model_scores": top_predictions,
            "model_used": "Random Forest baseline",
            "selected_symptoms": selected,
            "urgent_notice": bool(selected_set & urgent_symptoms),
            "disclaimer": (
                "Educational pattern-matching output only. "
                "This is not a diagnosis and must not be used "
                "to choose medicines or delay professional care."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "success": False,
            "message": "Prediction failed. Check the Flask terminal.",
        }), 500



# --------------------------------------------------
# LIVE ANALYTICS API
# --------------------------------------------------

@app.route("/api/analytics/summary", methods=["GET"])
def analytics_summary():
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM patients")
            total_patients = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT
                    COALESCE(status, 'Unspecified') AS status,
                    COUNT(*) AS total
                FROM appointments
                GROUP BY status
                ORDER BY total DESC
            """)
            appointment_status = cursor.fetchall()

            cursor.execute("""
                SELECT
                    COALESCE(record_type, 'Unspecified') AS record_type,
                    COUNT(*) AS total
                FROM health_records
                GROUP BY record_type
                ORDER BY total DESC
            """)
            record_types = cursor.fetchall()

            cursor.execute("""
                SELECT
                    DATE_FORMAT(created_at, '%Y-%m') AS month,
                    COUNT(*) AS total
                FROM patients
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 11 MONTH)
                GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                ORDER BY month
            """)
            monthly_patients = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM appointments
                WHERE appointment_date >= CURDATE()
                  AND status = 'Scheduled'
            """)
            upcoming_appointments = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM health_records
            """)
            total_records = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM appointments
            """)
            total_appointments = cursor.fetchone()["total"]

        return jsonify({
            "success": True,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "total_health_records": total_records,
            "upcoming_appointments": upcoming_appointments,
            "appointment_status": appointment_status,
            "record_types": record_types,
            "monthly_patients": monthly_patients,
        })

    except Exception:
        app.logger.exception("Could not load analytics")
        return jsonify({
            "success": False,
            "message": "Could not load analytics from MySQL.",
        }), 500

    finally:
        if connection:
            connection.close()


# --------------------------------------------------
# LIVE REPORT DATA API
# --------------------------------------------------

@app.route("/api/reports/<report_type>", methods=["GET"])
def report_data(report_type):
    # Use fixed SQL queries selected from an allowlist.
    # Never accept SQL table or column names from the browser.
    queries = {
        "patients": """
            SELECT
                patient_id,
                patient_code,
                first_name,
                last_name,
                date_of_birth,
                gender,
                phone,
                email,
                created_at
            FROM patients
            ORDER BY patient_id DESC
        """,
        "appointments": """
            SELECT
                a.appointment_id,
                p.patient_code,
                p.first_name,
                p.last_name,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.clinician_name,
                a.status
            FROM appointments a
            INNER JOIN patients p
                ON p.patient_id = a.patient_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        "health_records": """
            SELECT
                h.record_id,
                p.patient_code,
                p.first_name,
                p.last_name,
                h.record_type,
                h.title,
                h.description,
                h.recorded_at,
                h.created_at
            FROM health_records h
            INNER JOIN patients p
                ON p.patient_id = h.patient_id
            ORDER BY h.recorded_at DESC, h.record_id DESC
        """,
    }

    if report_type not in queries:
        return jsonify({
            "success": False,
            "message": "Choose patients, appointments, or health_records.",
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(queries[report_type])
            rows = cursor.fetchall()

        # Convert date/time values into JSON-compatible strings.
        for row in rows:
            for key, value in row.items():
                if value is not None and hasattr(value, "isoformat"):
                    row[key] = value.isoformat(sep=" ") if (
                        isinstance(value, datetime)
                    ) else value.isoformat()

        return jsonify({
            "success": True,
            "report_type": report_type,
            "count": len(rows),
            "rows": rows,
        })

    except Exception:
        app.logger.exception("Could not generate report: %s", report_type)
        return jsonify({
            "success": False,
            "message": "Could not retrieve report data from MySQL.",
        }), 500

    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    print("MediCare AI educational prototype")
    print("Open http://127.0.0.1:5000")

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000,
    )
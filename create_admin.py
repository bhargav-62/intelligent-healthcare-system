
import getpass
import re

from werkzeug.security import generate_password_hash
from db import get_db_connection


def main():
    print("MediCare AI — Create Administrator")
    print("----------------------------------")

    full_name = input("Full name: ").strip()
    email = input("Email: ").strip().lower()

    if not full_name or len(full_name) > 150:
        print("Error: Name must contain 1–150 characters.")
        return

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        print("Error: Enter a valid email address.")
        return

    password = getpass.getpass("New password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")

    if len(password) < 12:
        print("Error: Password must contain at least 12 characters.")
        return

    if len(password) > 128:
        print("Error: Password must not exceed 128 characters.")
        return

    if password != confirmation:
        print("Error: Passwords do not match.")
        return

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,),
            )

            if cursor.fetchone():
                print("Error: An account with this email already exists.")
                return

            password_hash = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users
                    (full_name, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (full_name, email, password_hash, "Admin", 1),
            )

            user_id = cursor.lastrowid

        connection.commit()
        print(f"Administrator created successfully. User ID: {user_id}")

    except Exception:
        if connection:
            connection.rollback()

        print("Could not create the administrator. Check the server log.")

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()

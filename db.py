
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_db_connection():
    """Create and return a connection to the MediCare MySQL database."""
    required_settings = [
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    ]

    missing = [
        key for key in required_settings
        if os.getenv(key) is None
    ]

    if missing:
        raise RuntimeError(
            "Missing database settings in .env: "
            + ", ".join(missing)
        )

    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        autocommit=False,
    )


if __name__ == "__main__":
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS database_name")
            result = cursor.fetchone()

        print("MySQL connection successful!")
        print(f"Connected database: {result['database_name']}")

    except Exception as exc:
        print(f"MySQL connection failed: {type(exc).__name__}: {exc}")

    finally:
        if connection:
            connection.close()

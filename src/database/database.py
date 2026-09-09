import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "my_database.db"
)


def get_connection():
    return sqlite3.connect(DATABASE_PATH)
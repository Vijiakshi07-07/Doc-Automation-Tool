import sqlite3
import os
from datetime import datetime


def get_db_path():
    """
    Returns the path to the database file.
    It will be created in a 'data' folder inside the project.
    """
    db_path = os.path.join("data", "glossary.db")
    return db_path


def create_connection():
    """
    Create a connection to the SQLite database.
    If the database file doesn't exist, SQLite creates it automatically.
    Think of this like opening a notebook — if it doesn't exist, you get a new one.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    return conn


def create_table():
    """
    Create the glossary table if it doesn't already exist.
    This is like drawing the columns in your notebook before writing entries.
    """
    conn = create_connection()

    # cursor is like a pen — you use it to write/read from the database
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS glossary (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            acronym     TEXT NOT NULL UNIQUE,
            expansion   TEXT NOT NULL,
            definition  TEXT,
            created_at  TEXT NOT NULL
        )
    """)

    # Always save your changes and close the connection when done
    conn.commit()
    conn.close()
    print("Database and glossary table are ready.")


def save_entry(acronym, expansion, definition):
    """
    Save one acronym entry into the database.
    If the acronym already exists, update it instead of creating a duplicate.
    """
    conn = create_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # INSERT OR REPLACE means: if acronym already exists, overwrite it
    cursor.execute("""
        INSERT OR REPLACE INTO glossary (acronym, expansion, definition, created_at)
        VALUES (?, ?, ?, ?)
    """, (acronym, expansion, definition, now))

    conn.commit()
    conn.close()
    print(f"  Saved: {acronym}({expansion})")


def get_all_entries():
    """
    Retrieve every entry from the glossary table.
    Returns a list of tuples: [(id, acronym, expansion, definition, created_at), ...]
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM glossary ORDER BY acronym")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_entry(acronym):
    """
    Look up one specific acronym in the database.
    Returns the row if found, or None if not found.
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM glossary WHERE acronym = ?", (acronym,))
    row = cursor.fetchone()

    conn.close()
    return row
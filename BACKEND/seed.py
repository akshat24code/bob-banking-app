"""
seed.py - One-time database initialisation script.

Creates banking.db and inserts demo customer accounts with hashed passwords.

Usage:
    cd BACKEND
    python seed.py

Re-running is safe - INSERT OR IGNORE skips duplicate usernames.
"""

import sqlite3
import os
from auth import hash_password

DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            full_name     TEXT    NOT NULL,
            balance       REAL    NOT NULL DEFAULT 0.0
        )
        """
    )

    demo_customers = [
        ("alice",   hash_password("password123"), "Alice Johnson",  5000.00),
        ("bob",     hash_password("securepass"),  "Bob Smith",      2500.50),
        ("charlie", hash_password("charlie99"),   "Charlie Brown",     0.00),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO customers (username, password_hash, full_name, balance) "
        "VALUES (?, ?, ?, ?)",
        demo_customers,
    )

    conn.commit()
    conn.close()
    print(f"Database initialised at: {DB_PATH}")
    print("Demo accounts:")
    print("  alice / password123  ->  $5,000.00")
    print("  bob   / securepass   ->  $2,500.50")
    print("  charlie / charlie99  ->  $0.00")


if __name__ == "__main__":
    init_db()

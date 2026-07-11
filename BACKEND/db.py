"""
db.py - Data-access layer for the Banking application.

Responsibilities:
  - Open and return an SQLite connection (rows as dicts).
  - Fetch a customer record by username.
  - Fetch a customer's current balance by customer ID.
  - Update a customer's balance by customer ID.

No business logic lives here.
"""

import sqlite3
import os

# Absolute path to the database file, always relative to this file's location
_DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")


def get_connection() -> sqlite3.Connection:
    """Open a connection to banking.db with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_customer_by_username(username: str):
    """Return the customer row for the given username, or None if not found."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id, username, password_hash, full_name, balance "
            "FROM customers WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()


def get_balance(customer_id: int):
    """Return the current balance for the given customer ID, or None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT balance FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        return float(row["balance"]) if row else None
    finally:
        conn.close()


def update_balance(customer_id: int, new_balance: float) -> None:
    """Overwrite the stored balance for the given customer ID."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE customers SET balance = ? WHERE id = ?",
            (new_balance, customer_id),
        )
        conn.commit()
    finally:
        conn.close()

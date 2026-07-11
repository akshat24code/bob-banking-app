"""
tests/test_db.py - Unit tests for BACKEND/db.py

All tests use an in-memory SQLite database via monkeypatching
so the real banking.db file is never touched.
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db
from auth import hash_password


def _make_in_memory_conn():
    """Create a fresh in-memory SQLite database with one test customer."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0.0
        )
        """
    )
    conn.execute(
        "INSERT INTO customers (username, password_hash, full_name, balance) VALUES (?, ?, ?, ?)",
        ("testuser", hash_password("pass"), "Test User", 1000.0),
    )
    conn.commit()
    return conn


def _patch_db(monkeypatch, conn):
    monkeypatch.setattr(db, "get_connection", lambda: _NonClosingWrapper(conn))


class _NonClosingWrapper:
    def __init__(self, conn): self._conn = conn
    def execute(self, *a, **kw): return self._conn.execute(*a, **kw)
    def commit(self): self._conn.commit()
    def close(self): pass


class TestGetCustomerByUsername:
    def test_existing_user_returns_row(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        result = db.get_customer_by_username("testuser")
        assert result is not None
        assert result["username"] == "testuser"
        assert result["full_name"] == "Test User"

    def test_missing_user_returns_none(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        assert db.get_customer_by_username("nobody") is None

    def test_returns_password_hash_field(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        result = db.get_customer_by_username("testuser")
        assert "password_hash" in result.keys()


class TestGetBalance:
    def test_returns_correct_balance(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        assert db.get_balance(1) == 1000.0

    def test_returns_none_for_missing_id(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        assert db.get_balance(9999) is None

    def test_balance_is_float(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        assert isinstance(db.get_balance(1), float)


class TestUpdateBalance:
    def test_balance_is_updated(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        db.update_balance(1, 2500.0)
        assert db.get_balance(1) == 2500.0

    def test_balance_can_be_set_to_zero(self, monkeypatch):
        conn = _make_in_memory_conn()
        _patch_db(monkeypatch, conn)
        db.update_balance(1, 0.0)
        assert db.get_balance(1) == 0.0

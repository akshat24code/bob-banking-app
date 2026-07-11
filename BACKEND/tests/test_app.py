"""
tests/test_app.py - Integration tests for BACKEND/app.py

Uses Flask's test client with an in-memory SQLite database.
Covers all 6 routes across success, failure, and edge-case scenarios.
"""

import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auth import hash_password


@pytest.fixture
def app_client(monkeypatch):
    import db
    import app as flask_app

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
        ("alice", hash_password("password123"), "Alice Johnson", 1000.0),
    )
    conn.commit()

    class _Wrapper:
        def __init__(self, c): self._c = c
        def execute(self, *a, **kw): return self._c.execute(*a, **kw)
        def commit(self): self._c.commit()
        def close(self): pass

    monkeypatch.setattr(db, "get_connection", lambda: _Wrapper(conn))

    flask_app.app.config["TESTING"] = True
    flask_app.app.config["SECRET_KEY"] = "test-secret"
    flask_app.app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.app.test_client() as client:
        yield client


def _login(client, username="alice", password="password123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)


class TestIndex:
    def test_root_redirects_to_login(self, app_client):
        r = app_client.get("/")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


class TestLoginGet:
    def test_renders_login_page(self, app_client):
        r = app_client.get("/login")
        assert r.status_code == 200
        assert b"Log In" in r.data


class TestLoginPost:
    def test_valid_credentials_redirect_to_dashboard(self, app_client):
        r = _login(app_client)
        assert r.status_code == 302
        assert "/dashboard" in r.headers["Location"]

    def test_wrong_password_returns_200(self, app_client):
        r = app_client.post("/login", data={"username": "alice", "password": "wrongpass"}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Invalid username or password" in r.data

    def test_unknown_user_returns_200(self, app_client):
        r = app_client.post("/login", data={"username": "nobody", "password": "whatever"}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Invalid username or password" in r.data

    def test_empty_username_shows_error(self, app_client):
        r = app_client.post("/login", data={"username": "", "password": "password123"}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Username is required" in r.data

    def test_empty_password_shows_error(self, app_client):
        r = app_client.post("/login", data={"username": "alice", "password": ""}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Password is required" in r.data


class TestDashboard:
    def test_unauthenticated_redirects_to_login(self, app_client):
        r = app_client.get("/dashboard")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_authenticated_shows_balance(self, app_client):
        _login(app_client)
        r = app_client.get("/dashboard", follow_redirects=True)
        assert r.status_code == 200
        assert b"1000.00" in r.data

    def test_authenticated_shows_customer_name(self, app_client):
        _login(app_client)
        r = app_client.get("/dashboard", follow_redirects=True)
        assert b"Alice Johnson" in r.data


class TestDeposit:
    def test_valid_deposit_redirects_to_dashboard(self, app_client):
        _login(app_client)
        r = app_client.post("/deposit", data={"amount": "500"}, follow_redirects=False)
        assert r.status_code == 302
        assert "/dashboard" in r.headers["Location"]

    def test_deposit_increases_balance(self, app_client):
        _login(app_client)
        app_client.post("/deposit", data={"amount": "500"})
        r = app_client.get("/dashboard", follow_redirects=True)
        assert b"1500.00" in r.data

    def test_empty_amount_shows_error(self, app_client):
        _login(app_client)
        r = app_client.post("/deposit", data={"amount": ""}, follow_redirects=True)
        assert b"Please enter an amount" in r.data

    def test_non_numeric_amount_shows_error(self, app_client):
        _login(app_client)
        r = app_client.post("/deposit", data={"amount": "abc"}, follow_redirects=True)
        assert b"valid number" in r.data

    def test_negative_amount_shows_error(self, app_client):
        _login(app_client)
        r = app_client.post("/deposit", data={"amount": "-100"}, follow_redirects=True)
        assert b"greater than zero" in r.data

    def test_unauthenticated_deposit_redirects(self, app_client):
        r = app_client.post("/deposit", data={"amount": "100"})
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


class TestWithdraw:
    def test_valid_withdraw_redirects_to_dashboard(self, app_client):
        _login(app_client)
        r = app_client.post("/withdraw", data={"amount": "200"}, follow_redirects=False)
        assert r.status_code == 302
        assert "/dashboard" in r.headers["Location"]

    def test_withdrawal_decreases_balance(self, app_client):
        _login(app_client)
        app_client.post("/withdraw", data={"amount": "200"})
        r = app_client.get("/dashboard", follow_redirects=True)
        assert b"800.00" in r.data

    def test_overdraft_shows_insufficient_funds(self, app_client):
        _login(app_client)
        r = app_client.post("/withdraw", data={"amount": "9999"}, follow_redirects=True)
        assert b"Insufficient funds" in r.data

    def test_empty_amount_shows_error(self, app_client):
        _login(app_client)
        r = app_client.post("/withdraw", data={"amount": ""}, follow_redirects=True)
        assert b"Please enter an amount" in r.data

    def test_unauthenticated_withdraw_redirects(self, app_client):
        r = app_client.post("/withdraw", data={"amount": "100"})
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


class TestLogout:
    def test_logout_redirects_to_login(self, app_client):
        _login(app_client)
        r = app_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_after_logout_dashboard_requires_login(self, app_client):
        _login(app_client)
        app_client.get("/logout")
        r = app_client.get("/dashboard")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_unauthenticated_logout_redirects_to_login(self, app_client):
        r = app_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

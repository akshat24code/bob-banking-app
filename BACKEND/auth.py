"""
auth.py - Authentication helpers for the Banking application.

Responsibilities:
  - Hash a plain-text password using Werkzeug's secure hashing.
  - Verify a plain-text password against a stored hash.
  - Provide a route decorator that enforces an active session.
"""

from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_text: str) -> str:
    """Hash plain_text using Werkzeug's pbkdf2:sha256. Used only in seed.py."""
    return generate_password_hash(plain_text)


def verify_password(plain_text: str, stored_hash: str) -> bool:
    """Compare plain_text against stored_hash. Returns True if they match."""
    return check_password_hash(stored_hash, plain_text)


def login_required(f):
    """
    Route decorator that ensures the caller has an active session.
    Redirects to /login if session['user_id'] is not set.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

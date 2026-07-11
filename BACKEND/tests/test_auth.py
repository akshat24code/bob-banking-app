"""
tests/test_auth.py - Unit tests for BACKEND/auth.py

Covers: hash_password and verify_password functions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auth import hash_password, verify_password


class TestHashPassword:
    def test_returns_string(self):
        assert isinstance(hash_password("mypassword"), str)

    def test_hash_differs_from_input(self):
        plain = "mypassword"
        assert hash_password(plain) != plain

    def test_hash_is_not_empty(self):
        assert len(hash_password("x")) > 0

    def test_two_hashes_of_same_input_differ(self):
        """Werkzeug uses a random salt - each hash should be unique."""
        assert hash_password("same") != hash_password("same")


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        plain = "correcthorse"
        assert verify_password(plain, hash_password(plain)) is True

    def test_wrong_password_returns_false(self):
        assert verify_password("wrong", hash_password("correct")) is False

    def test_empty_password_returns_false(self):
        assert verify_password("", hash_password("notempty")) is False

    def test_case_sensitive(self):
        assert verify_password("password", hash_password("Password")) is False

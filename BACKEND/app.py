"""
app.py - Flask application entry point for the Banking Web Application.

Registers all routes, configures the app, and ties together auth.py and db.py.
Template folder  : ../FRONTEND/templates
Static folder    : ../FRONTEND/static
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from auth import login_required, verify_password
import db

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "FRONTEND", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "FRONTEND", "static"),
)

# SECRET_KEY signs the session cookie. In production load from an env var.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")


# ---------------------------------------------------------------------------
# Helper: safe amount parser
# ---------------------------------------------------------------------------

def _parse_amount(raw: str) -> tuple:
    """
    Convert raw form string to a positive float.
    Returns (amount, None) on success or (None, error_message) on failure.
    Validates: presence -> numeric -> positive.
    """
    if not raw or not raw.strip():
        return None, "Please enter an amount."
    try:
        amount = float(raw.strip())
    except ValueError:
        return None, "Please enter a valid number."
    if amount <= 0:
        return None, "Amount must be greater than zero."
    return amount, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Root redirect - send visitors to login."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  - Render the login form. Redirect to dashboard if already logged in.
    POST - Validate credentials, set session, redirect to dashboard.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username:
            flash("Username is required.", "error")
            return render_template("login.html")
        if not password:
            flash("Password is required.", "error")
            return render_template("login.html")

        customer = db.get_customer_by_username(username)

        # Generic message prevents username enumeration
        if customer is None or not verify_password(password, customer["password_hash"]):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        session["user_id"] = customer["id"]
        session["full_name"] = customer["full_name"]
        flash(f"Welcome back, {customer['full_name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Display customer name and current balance with deposit/withdraw forms."""
    customer_id = session["user_id"]
    full_name = session["full_name"]
    balance = db.get_balance(customer_id)
    return render_template("dashboard.html", full_name=full_name, balance=balance)


@app.route("/deposit", methods=["POST"])
@login_required
def deposit():
    """
    Process a deposit. Validates amount then adds to balance.
    Post/Redirect/Get pattern prevents duplicate submissions on refresh.
    """
    raw = request.form.get("amount", "")
    amount, error = _parse_amount(raw)

    if error:
        flash(error, "error")
        return redirect(url_for("dashboard"))

    customer_id = session["user_id"]
    current_balance = db.get_balance(customer_id)
    new_balance = round(current_balance + amount, 2)
    db.update_balance(customer_id, new_balance)

    flash(f"Successfully deposited ${amount:,.2f}. New balance: ${new_balance:,.2f}", "success")
    return redirect(url_for("dashboard"))


@app.route("/withdraw", methods=["POST"])
@login_required
def withdraw():
    """
    Process a withdrawal. Validates amount and checks sufficient funds.
    """
    raw = request.form.get("amount", "")
    amount, error = _parse_amount(raw)

    if error:
        flash(error, "error")
        return redirect(url_for("dashboard"))

    customer_id = session["user_id"]
    current_balance = db.get_balance(customer_id)

    if amount > current_balance:
        flash(
            f"Insufficient funds. Your current balance is ${current_balance:,.2f}.",
            "error",
        )
        return redirect(url_for("dashboard"))

    new_balance = round(current_balance - amount, 2)
    db.update_balance(customer_id, new_balance)

    flash(f"Successfully withdrew ${amount:,.2f}. New balance: ${new_balance:,.2f}", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Custom error pages
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

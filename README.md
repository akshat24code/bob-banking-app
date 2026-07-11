# 🏦 SecureBank — Banking Web Application

A full-stack banking web application built with **Python Flask**, **SQLite**, and **Bootstrap 5**.

## Features

- Customer login with hashed passwords (pbkdf2:sha256)
- Responsive dashboard showing current account balance
- Deposit funds with full validation
- Withdraw funds with overdraft protection
- Secure logout with session invalidation
- Custom 404 and 500 error pages

## Project Structure

```
bob-banking-app/
├── FRONTEND/
│   ├── templates/       # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/
│       └── style.css    # Custom Bootstrap overrides
│
├── BACKEND/
│   ├── app.py           # Flask routes and app factory
│   ├── auth.py          # Password hashing and session guard
│   ├── db.py            # SQLite data-access layer
│   ├── seed.py          # One-time database seeder
│   ├── requirements.txt
│   └── tests/
│       ├── test_auth.py
│       ├── test_db.py
│       └── test_app.py
│
├── IMPLEMENTATION_PLAN.md
└── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
```

## Quick Start

```bash
# 1. Create and activate a virtual environment
cd BACKEND
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python seed.py

# 4. Run the application
$env:FLASK_APP = "app.py"          # Windows PowerShell
$env:FLASK_ENV = "development"     # Windows PowerShell
flask run
```

Open **http://127.0.0.1:5000** in your browser.

## Demo Accounts

| Username | Password     | Starting Balance |
|----------|--------------|------------------|
| alice    | password123  | $5,000.00        |
| bob      | securepass   | $2,500.50        |
| charlie  | charlie99    | $0.00            |

## Running Tests

```bash
cd BACKEND
.\venv\Scripts\activate
pytest tests/ -v
```

40 tests — 24 integration + 8 auth unit + 8 db unit.

## Tech Stack

| Layer    | Technology              |
|----------|-------------------------|
| Frontend | HTML5, Bootstrap 5, Jinja2 |
| Backend  | Python 3.9+, Flask 3     |
| Database | SQLite (via sqlite3)     |
| Auth     | Werkzeug password hashing |
| Tests    | pytest                   |

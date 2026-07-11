# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** This guide follows the phases and component design defined in `IMPLEMENTATION_PLAN.md`.
> Instructions are written in plain English describing *what to do* and *why* — not the exact code.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites
- Python 3.9 or higher
- pip (bundled with Python)
- A terminal with write access to the project directory

### 1.2 Create the Project Folder Structure
- `FRONTEND/templates/` — HTML page files
- `FRONTEND/static/` — CSS overrides and assets
- `BACKEND/` — Python source files and database

### 1.3 Create and Activate a Virtual Environment

```bash
cd BACKEND
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 1.4 Create the Requirements File
List packages in `BACKEND/requirements.txt`:
- **Flask** — the web framework
- **Werkzeug** — password hashing utilities
- **pytest** — test runner

### 1.5 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.6 Seed the Database
Run `seed.py` once to create `banking.db` and insert demo customer accounts with hashed passwords.

```bash
python seed.py
```

---

## 2. Backend Implementation

### 2.1 Database Layer — `db.py`

Centralise all SQLite connection and query logic:

1. **get_connection** — opens a connection to `banking.db`, configures rows as dict-like objects.
2. **get_customer_by_username** — looks up a customer record by username, returns full row or None.
3. **get_balance** — returns the current balance for a customer ID.
4. **update_balance** — overwrites the stored balance for a given customer ID.

### 2.2 Authentication Helpers — `auth.py`

1. **hash_password** — wraps `generate_password_hash`. Used only in the seed script.
2. **verify_password** — wraps `check_password_hash`. Returns True/False.
3. **login_required decorator** — checks `session['user_id']`; redirects to `/login` if missing.

### 2.3 Flask Application — `app.py`

**Initial Configuration:**
- Create the Flask instance with `template_folder` pointing to `../FRONTEND/templates` and `static_folder` to `../FRONTEND/static`.
- Set `SECRET_KEY` from an environment variable (fallback to a dev string).

**Routes:**

| Method | Route | Logic |
|--------|-------|-------|
| GET | `/` | Redirect to `/login` |
| GET | `/login` | Render login form; skip if already logged in |
| POST | `/login` | Validate fields -> lookup user -> verify hash -> set session -> redirect |
| GET | `/dashboard` | Session guard -> fetch balance -> render template |
| POST | `/deposit` | Session guard -> validate amount -> add to balance -> redirect |
| POST | `/withdraw` | Session guard -> validate amount -> check funds -> subtract -> redirect |
| GET | `/logout` | `session.clear()` -> redirect to login |

### 2.4 Session Management

- Store only `user_id` and `full_name` in the session — never balance or password hash.
- `session.clear()` on logout invalidates the session immediately.
- The `@login_required` decorator is the single guard for all protected routes.

### 2.5 Error Handling

| Scenario | Behaviour |
|---|---|
| Empty form field | Flash descriptive error; re-render page |
| Invalid login credentials | Flash generic message (prevents username enumeration) |
| Non-numeric amount | Flash "Please enter a valid number" |
| Overdraft | Flash "Insufficient funds" |
| Unauthenticated access | Silent redirect to `/login` |

---

## 3. Frontend Implementation

### 3.1 Base Layout Template (`base.html`)

- HTML head with Bootstrap 5 CDN and custom CSS link.
- Responsive navbar: brand on left, Logout button on right (shown only when logged in).
- Flash message block using `get_flashed_messages(with_categories=true)`.
- Main content block that child templates override.

### 3.2 Login Page (`login.html`)

- Centred Bootstrap card.
- Form: `method="POST"` `action="/login"`.
- Username text input.
- Password input (type="password").
- Full-width "Log In" button.

### 3.3 Dashboard Page (`dashboard.html`)

- **Section 1** — Account summary card with greeting and large balance display.
- **Section 2** — Deposit form: numeric input, green "Deposit" button.
- **Section 3** — Withdraw form: numeric input, red "Withdraw" button.
- Sections 2 and 3 are side-by-side on desktop (`col-md-6`), stacked on mobile.

### 3.4 Bootstrap Conventions

- Wrap content in `container` div.
- Use `col-*` grid for responsive layouts.
- Use Bootstrap utility classes (`mt-4`, `mb-3`) for spacing.
- Use Bootstrap `alert` component for flash messages.

---

## 4. Integration Steps

### 4.1 Flask Template/Static Folders
Pass `template_folder` and `static_folder` to the Flask constructor so it finds files in `FRONTEND/`.

### 4.2 SQLite Path
Use `os.path.dirname(__file__)` in `db.py` so the database path resolves correctly from any working directory.

### 4.3 Form Action Matching
- Login form `action="/login"` matches `@app.route('/login', methods=['POST'])`
- Deposit form `action="/deposit"` matches `@app.route('/deposit', methods=['POST'])`
- Withdraw form `action="/withdraw"` matches `@app.route('/withdraw', methods=['POST'])`

### 4.4 Jinja2 Template Variables
Pass named keyword arguments to `render_template()`. Use `{{ variable }}` in templates.

### 4.5 End-to-End Verification Checklist
1. Visit `/login` — login form renders.
2. Submit valid credentials — redirected to dashboard with balance.
3. Submit deposit — balance increases, success flash shown.
4. Submit withdrawal — balance decreases.
5. Click logout — redirected to login.
6. Navigate to `/dashboard` after logout — redirected to login.

---

## 5. Validation Rules

### 5.1 Login Validation
| Rule | Error Message |
|---|---|
| Username not empty | "Username is required." |
| Password not empty | "Password is required." |
| Username exists and password matches | "Invalid username or password." |

### 5.2 Deposit Validation
| Rule | Error Message |
|---|---|
| Amount not empty | "Please enter an amount." |
| Amount is a valid number | "Please enter a valid number." |
| Amount > 0 | "Amount must be greater than zero." |

### 5.3 Withdrawal Validation
| Rule | Error Message |
|---|---|
| Amount not empty | "Please enter an amount." |
| Amount is a valid number | "Please enter a valid number." |
| Amount > 0 | "Amount must be greater than zero." |
| Amount <= current balance | "Insufficient funds. Your current balance is $X." |

### 5.4 Validation Order
1. Presence check
2. Type check (numeric)
3. Range check (positive, within balance)
4. Database operation

Short-circuit on first failure.

---

## 6. Testing

### 6.1 Unit Tests (`tests/test_auth.py`, `tests/test_db.py`)

- `test_auth.py` — 8 tests covering hash and verify functions.
- `test_db.py` — 8 tests using an in-memory SQLite database to test all db.py functions in isolation.

### 6.2 Integration Tests (`tests/test_app.py`)

- 24 tests using Flask's test client with an in-memory database.
- Covers all 6 routes across success, validation failure, authentication, and edge cases.

### 6.3 Running Tests

```bash
cd BACKEND
.\venv\Scripts\activate
pytest tests/ -v
```

Expected: **40 passed**.

### 6.4 Manual Testing Checklist

**Authentication**
- [ ] `/dashboard` without login redirects to `/login`
- [ ] Empty username shows error
- [ ] Empty password shows error
- [ ] Wrong credentials show "Invalid username or password"
- [ ] Valid login redirects to dashboard
- [ ] Logout redirects to login; Back button does not restore session

**Deposit**
- [ ] Blank amount shows error
- [ ] Non-numeric value shows error
- [ ] Zero or negative amount shows error
- [ ] Valid amount updates balance and shows success flash
- [ ] Refresh after deposit does not re-submit (PRG pattern)

**Withdrawal**
- [ ] Blank / non-numeric / negative amount shows error
- [ ] Amount exceeding balance shows "Insufficient funds"
- [ ] Valid amount updates balance and shows success flash

**Responsive Layout**
- [ ] Login page centred on 375px mobile
- [ ] Dashboard forms stack vertically on mobile

---

## 7. Deployment

### 7.1 Run Locally

```bash
cd BACKEND
.\venv\Scripts\activate       # Windows
python seed.py                  # first run only

$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run
```

Open http://127.0.0.1:5000

### 7.2 Production Considerations

| Concern | Development | Production |
|---|---|---|
| WSGI Server | flask run | Gunicorn or Waitress |
| Secret Key | Hardcoded fallback | Environment variable only |
| Debug Mode | FLASK_ENV=development | DEBUG=False |
| HTTPS | Plain HTTP | Nginx + TLS certificate |
| Database | SQLite file | PostgreSQL for scale |
| Static Files | Served by Flask | Served by Nginx directly |

---

*End of Step-by-Step Implementation Guide*

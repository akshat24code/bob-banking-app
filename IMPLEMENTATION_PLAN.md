# Banking Web Application — Implementation Plan

---

## 1. Solution Overview

### Objective
Build a lightweight, browser-based banking web application that allows customers to securely log in, view their account balance, deposit funds, withdraw funds, and log out — all served through a Python Flask backend with an SQLite data store and a Bootstrap-powered frontend.

### Scope

| In Scope | Out of Scope |
|---|---|
| Customer login / logout | Admin portal |
| View account balance | Multi-currency support |
| Deposit funds | External payment integrations |
| Withdraw funds | Mobile native app |
| Session management | Email / SMS notifications |
| Basic input validation | Audit logging / reporting |

### Users
- **Customer** — the sole user role. A customer can authenticate, inspect their balance, and perform deposit or withdrawal transactions.

### Functional Requirements
1. A customer can log in with a username and password.
2. Upon successful login the customer is directed to a personal dashboard.
3. The dashboard displays the current account balance.
4. A customer can deposit a positive monetary amount into their account.
5. A customer can withdraw a positive monetary amount, provided sufficient funds exist.
6. A customer can log out, ending their session.
7. Unauthenticated requests to protected pages redirect to the login screen.

### Non-Functional Requirements
- **Security** — passwords must be stored as hashed values; sessions must be server-side and invalidated on logout.
- **Usability** — all pages must be responsive and accessible on desktop and mobile browsers via Bootstrap.
- **Simplicity** — SQLite is sufficient; no external database server is required.
- **Portability** — the application must run with a single `flask run` command after installing dependencies.

### Assumptions
- A small number of concurrent users (development / demo scale); SQLite is adequate.
- Each customer has exactly one account.
- Pre-seeded customer records exist in the database before first use.
- No password-reset or registration workflow is required in this iteration.
- The application runs on `localhost` during development; HTTPS is deferred.

---

## 2. High-Level Architecture

### Architecture Overview

```
Browser
  |
  |  FRONTEND (HTML + Bootstrap, Jinja2 templates)
  |
  |  HTTP (form POST / GET)
  |
BACKEND
  |  Python Flask Application
  |  Routes | Session Management | Business Logic
  |
  |  SQL queries (sqlite3)
  |
DATABASE
   SQLite file (banking.db)
```

### Frontend to Backend to Database Interaction

```
Browser
  |
  +- GET  /login          -> Flask renders login page
  +- POST /login          -> Flask validates credentials against DB -> sets session -> redirect /dashboard
  +- GET  /dashboard      -> Flask reads balance from DB -> renders dashboard
  +- POST /deposit        -> Flask updates balance in DB -> redirect /dashboard
  +- POST /withdraw       -> Flask checks & updates balance in DB -> redirect /dashboard
  +- GET  /logout         -> Flask clears session -> redirect /login
```

### Request Lifecycle
1. Browser sends an HTTP request (GET or form POST).
2. Flask router matches the URL to the appropriate view function.
3. The view function checks session state; unauthenticated requests are redirected to `/login`.
4. Authenticated requests call the relevant service/helper to read or write to the SQLite database.
5. Flask renders a Jinja2 template (located in `FRONTEND/templates/`) and returns the HTML response.
6. Bootstrap styles and any static assets are served from `FRONTEND/static/`.

---

## 3. Component Design

### Frontend Responsibilities
- Render HTML pages using Jinja2 templates embedded inside Flask's template engine.
- Apply layout, responsiveness, and styling via Bootstrap CSS.
- Display server-side flash messages (success, error, info) to the user.
- Collect user input through HTML forms and submit via HTTP POST.
- Provide navigation elements (dashboard link, logout button).

**Pages required:**
| Page | Route | Purpose |
|---|---|---|
| Login | `/login` | Username / password form |
| Dashboard | `/dashboard` | Balance display + deposit/withdraw forms |

### Backend Responsibilities
- Define and handle all HTTP routes via Flask view functions.
- Authenticate users by verifying hashed passwords.
- Manage server-side user sessions (login state, logged-in user identity).
- Enforce authorisation — all non-login routes require an active session.
- Execute business logic for deposit and withdrawal (validation, balance update).
- Interact with the SQLite database through a data-access layer.
- Return rendered templates or HTTP redirects as appropriate.

**Route map:**
| Method | Route | Handler |
|---|---|---|
| GET | `/login` | Show login form |
| POST | `/login` | Process login |
| GET | `/dashboard` | Show dashboard |
| POST | `/deposit` | Process deposit |
| POST | `/withdraw` | Process withdrawal |
| GET | `/logout` | End session |

### Database Responsibilities
- Persist customer account data (identity + credentials + balance) in an SQLite file.
- Provide reliable read/write access for balance queries and transaction updates.
- Remain self-contained — no separate database server process.

---

## 4. Folder Structure

```
bob-banking-app/
|
+-- FRONTEND/
|   +-- templates/    # Jinja2 HTML templates
|   +-- static/       # CSS overrides, images
|
+-- BACKEND/
|   +-- app.py        # Flask app factory, route definitions
|   +-- auth.py       # Authentication helpers
|   +-- db.py         # Database connection and query helpers
|   +-- seed.py       # Database seeder
|   +-- requirements.txt
|   +-- tests/
|
+-- IMPLEMENTATION_PLAN.md
+-- STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
```

---

## 5. Module Breakdown

### 5.1 Authentication Module
**Scope:** Login and logout flows; session lifecycle.

- Accepts username and password from the login form.
- Looks up the customer record by username.
- Compares the submitted password against the stored hash using a secure hashing library.
- On success, stores the customer identifier in the Flask session cookie.
- On failure, re-renders the login page with an error flash message.
- Logout clears the session and redirects to the login page.

### 5.2 Dashboard Module
**Scope:** Post-login landing page; balance display.

- Requires an active session; unauthenticated access redirects to `/login`.
- Retrieves the current account balance for the logged-in customer from the database.
- Renders the dashboard template with the balance and transaction forms.

### 5.3 Account Management Module
**Scope:** Reading and displaying account state.

- Encapsulates the logic for fetching a customer's account balance.
- Acts as the data-retrieval layer called by both the dashboard and transaction handlers.

### 5.4 Transaction Module
**Scope:** Deposit and withdrawal operations.

- **Deposit:** Validates that the submitted amount is a positive number, then increments the account balance.
- **Withdraw:** Validates that the submitted amount is a positive number and does not exceed the current balance; decrements balance on success.
- Post/Redirect/Get pattern prevents duplicate form submissions on refresh.

---

## 6. Implementation Roadmap

### Phase 1 — Project Scaffolding
Set up folder structure, Flask app skeleton, Bootstrap integration, and SQLite connection.

### Phase 2 — Authentication
Build login and logout with session management and password hashing.

### Phase 3 — Dashboard and Balance View
Render the authenticated landing page with current balance.

### Phase 4 — Transactions (Deposit and Withdraw)
Add deposit and withdrawal forms and handlers.

### Phase 5 — Integration and Validation
End-to-end testing and polish.

---

*End of Implementation Plan*

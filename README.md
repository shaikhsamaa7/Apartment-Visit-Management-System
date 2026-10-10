# Apartment Visit Management System (AVMS)

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask%203.1.3-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](https://pytest.org/)
[![Security](https://img.shields.io/badge/security-CSRF%20%7C%20Parameterized%20SQL%20%7C%20PBKDF2-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-purple.svg)]()

A secure, enterprise-grade, server-rendered **Apartment Visit Management System (AVMS)** engineered for gated communities, residential societies, and facility management offices. 

Originally built as a legacy PHP microproject with raw SQL queries and MD5 hashing, this codebase has been systematically upgraded into a secure, robust Python/Flask application with 100% database schema preservation, dual SQLite/MySQL support, full test coverage, and a modern property-management design system.

---

## Table of Contents

1. [Project Overview & Problem Statement](#project-overview--problem-statement)
2. [Objectives & Key Upgrades](#objectives--key-upgrades)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Database Design & Schema Parity](#database-design--schema-parity)
6. [Key Features & Workflows](#key-features--workflows)
7. [Security Hardening](#security-hardening)
8. [Setup & Installation](#setup--installation)
9. [Running the Application](#running-the-application)
10. [Test Suite & Verification](#test-suite--verification)
11. [Screenshots](#screenshots)
12. [Preservation of Original PHP Code](#preservation-of-original-php-code)
13. [Limitations & Future Roadmap](#limitations--future-roadmap)

---

## Project Overview & Problem Statement

Residential complexes and gated apartment communities experience constant influxes of visitors: delivery couriers, maintenance contractors, daily domestic staff (maids, cooks, drivers, cleaners), and personal guests. 

Manual paper registers lead to:
- Missing entry/exit timestamps.
- Zero searchability or audit capabilities during security incidents.
- No visibility into how many non-residents are currently inside the premises.
- Inability to verify authorized daily staff passes without manual physical inspections.

**AVMS** provides building administrators and gate security teams with an automated, responsive digital log to check in visitors, issue recurring or term visitor passes with printable badge cards, track departures in real time, and generate filtered compliance reports.

---

## Objectives & Key Upgrades

| Aspect | Legacy PHP Microproject | Upgraded Python / Flask Implementation |
|---|---|---|
| **Language & Engine** | Procedural PHP (error-suppressed) | Python 3.13+ with Flask application factory |
| **SQL Safety** | Vulnerable raw string interpolation | 100% Parameterized queries across SQLite and MySQL |
| **Password Storage** | Weak, unsalted MD5 hashes | Modern PBKDF2:SHA256 with transparent legacy MD5 upgrade on login |
| **CSRF Defense** | Completely missing; GET-based deletions | Cryptographic per-session CSRF tokens on all mutating requests |
| **State Mutability** | Destructive actions via `GET ?pid=1` | Safe POST requests with CSRF validation & confirmation dialogues |
| **Database Support** | Hardcoded XAMPP MySQL root connection | Dual-engine: Zero-config SQLite default + MySQL MariaDB enterprise support |
| **Session Security** | Insecure session fixation vulnerable | Session regeneration on login, `HttpOnly`, `SameSite=Lax` cookies |
| **UI / UX** | Deprecated Bootstrap 4 + heavy jQuery theme | Modern Inter typography, custom property-dashboard design system |
| **Testing** | Zero automated tests | Comprehensive PyTest suite with 28 automated tests (100% passing) |

---

## Technology Stack

- **Backend**: Python 3.10+, Flask 3.1.3, Werkzeug 3.1.8, Jinja2 3.1.6
- **Database**: SQLite 3 (default out-of-the-box) or MySQL 5.7+ / MariaDB 10.4+ (PyMySQL 1.2.3)
- **Frontend**: Semantic HTML5, Vanilla Modern CSS Design System (no heavy bloated frameworks), Vanilla JavaScript (no jQuery dependency)
- **Security**: Cryptographic CSRF tokens, PBKDF2 password hashing, HTTP Security Headers (`nosniff`, `SAMEORIGIN`, `1; mode=block`, `strict-origin-when-cross-origin`)
- **Testing**: Pytest 9.1.1, temporary isolated test database fixtures

---

## System Architecture

The project follows a clean, modular Flask architectural pattern:

```text
AVMS-Project/
├── app.py                     # Application factory (create_app), error handlers, security hooks
├── config.py                  # Environment-specific configuration classes
├── security.py                # CSRF protection, security headers, password hashing & upgrade logic
├── requirements.txt           # Production and development dependencies
├── .env.example               # Configuration template with placeholder values
├── .gitignore                 # Exclusion rules for virtual environments, databases, secrets
├── README.md                  # Comprehensive architectural and user documentation
├── database/
│   ├── db.py                  # Database abstraction layer (parameterized execution, connection pooling)
│   ├── schema_sqlite.sql      # SQLite schema preserving exact table and column names
│   ├── schema_mysql.sql       # MySQL/MariaDB schema matching original avmsdb.sql
│   └── seed_data.py           # Synthetic seed data generator
├── routes/
│   ├── auth_routes.py         # Login, logout, profile, password reset & change
│   ├── dashboard_routes.py    # Executive metrics, activity feeds, category distribution
│   ├── visitor_routes.py      # Registration, check-in, check-out remarking, search, CSV export
│   ├── pass_routes.py         # Term pass creation, validity checks, printable badge, CSV export
│   ├── category_routes.py     # Classification management, usage metrics, safe deletion
│   └── report_routes.py       # Between-dates visitor and pass reports with CSV downloads
├── templates/
│   ├── base.html              # Responsive layout with accessible sidebar, topbar, toast alerts
│   ├── auth/                  # Authentication & recovery templates
│   ├── dashboard/             # Executive property-management dashboard
│   ├── visitors/              # Visitor form, manage table, detail/checkout, search
│   ├── passes/                # Pass creator, manage table, printable pass card
│   ├── categories/            # Category management interface
│   ├── reports/               # Date-range visitor and pass report tables
│   └── errors/                # 400, 404, and 500 error pages
├── static/
│   ├── css/style.css          # Design system stylesheet, color tokens, print layout
│   └── js/main.js             # Mobile drawer toggle, alert dismissal, print triggers
├── tests/
│   ├── conftest.py            # Test fixtures (temporary isolated SQLite database, test client)
│   ├── test_auth.py           # Authentication, session fixation, password recovery tests
│   ├── test_visitors.py       # Visitor registration, checkout, search, export tests
│   ├── test_passes.py         # Pass issuance, date validation, deletion, print view tests
│   ├── test_categories.py     # Category creation, duplicate prevention, deletion tests
│   ├── test_reports.py        # Date-range query and CSV export tests
│   └── test_security.py       # CSRF rejection, SQL injection resilience, headers tests
└── _backup_original_php/      # Verbatim preservation of legacy PHP application & SQL dump
```

---

## Database Design & Schema Parity

The application preserves 100% schema parity with the original `avmsdb.sql` database:

### 1. `tbladmin`
- `ID`: Primary key, auto-increment integer.
- `AdminName`: Administrator full name (`VARCHAR(45)`).
- `UserName`: Unique administrator login username (`VARCHAR(45)`).
- `MobileNumber`: Contact phone number (`BIGINT(11)`).
- `Email`: Administrator notification email (`VARCHAR(120)`).
- `Password`: Password hash (`VARCHAR(120)`).
- `AdminRegdate`: Registration timestamp.

### 2. `tblcategory`
- `id`: Primary key, auto-increment integer.
- `categoryName`: Unique category label (e.g. `Maid`, `Cook`, `Driver`, `Delivery`, `Guest`) (`VARCHAR(120)`).
- `creationDate`: Creation timestamp.

### 3. `tblvisitor`
- `ID`: Primary key, auto-increment integer.
- `categoryName`: Classification label (`VARCHAR(120)`).
- `VisitorName`: Full visitor name (`VARCHAR(120)`).
- `MobileNumber`: Numeric contact number (`BIGINT(11)`).
- `Address`: Origin address (`VARCHAR(250)`).
- `Apartment`: Target apartment/flat (`VARCHAR(120)`).
- `Floor`: Apartment floor level (`VARCHAR(120)`).
- `WhomtoMeet`: Resident name (`VARCHAR(120)`).
- `ReasontoMeet`: Purpose of visit (`VARCHAR(120)`).
- `EnterDate`: Arrival timestamp.
- `remark`: Departure/exit remark recorded by security (`VARCHAR(255)`).
- `outtime`: Exit timestamp.

### 4. `tblvisitorpass`
- `ID`: Primary key, auto-increment integer.
- `passnumber`: Unique 8-digit randomized pass number (`BIGINT(20)`).
- `categoryName`: Staff/visitor category (`VARCHAR(120)`).
- `VisitorName`: Authorized individual (`VARCHAR(120)`).
- `MobileNumber`: Contact phone (`BIGINT(11)`).
- `Address`: Agency or residential address (`VARCHAR(250)`).
- `Apartment`: Authorized apartment (`VARCHAR(120)`).
- `Floor`: Floor number (`VARCHAR(120)`).
- `passDetails`: Purpose/job scope (`VARCHAR(120)`).
- `creationDate`: Issuance timestamp.
- `fromDate`: Validity start date (`DATE`).
- `toDate`: Validity expiration date (`DATE`).

---

## Key Features & Workflows

### 1. Executive Dashboard
- **Real-Time KPIs**: Today's visits, yesterday's visits, trailing 7-day volume, total lifetime visits, currently inside headcount, active passes, total passes, and listed categories.
- **Activity Streams**: Most recent check-ins with immediate checkout links, recent passes with active/expired badges, and visitor category distribution.

### 2. Visitor Management
- **Check-In**: Form validating name, category, phone number, destination apartment, floor, resident, purpose, and address.
- **Departure Check-Out**: Real-time recording of security exit notes and out-time timestamp.
- **Search**: Multi-column substring matching across name, mobile number, apartment, and resident.
- **Export**: One-click full CSV registry download.

### 3. Visitor Pass Generation
- **Pass Issuance**: Auto-generates unique 8-digit pass numbers (`#94395972`) with date interval validation.
- **Printable Pass Badge**: Specialized card with security signature block, apartment details, and dedicated `@media print` CSS layout for clean printer and PDF output.
- **Pass Deletion**: Protected by CSRF-verified POST requests and confirmation modals.

### 4. Classification & Categories
- Custom classification of domestic staff and guests.
- Tracks active visitor counts and pass counts per category.
- Duplicate name rejection.

### 5. Between-Dates Reporting
- Select custom date ranges for visitors and passes.
- Instant calculation of total volume, completed visits, and active passes in period.
- Filtered CSV downloads with custom date-stamped filenames.

---

## Security Hardening

1. **SQL Injection Elimination**: Replaced all string concatenation queries with parameterized query execution across SQLite and MySQL.
2. **Transparent Password Upgrade**: 
   - Supports authenticating against legacy unsalted MD5 hashes (`f925916e2754e5e03f75dd58a5733251`).
   - Automatically upgrades the database record to secure PBKDF2:SHA256 on the first successful login.
3. **Cross-Site Request Forgery (CSRF)**:
   - All state-changing routes (`POST`, `PUT`, `DELETE`) require a cryptographically random, per-session CSRF token.
   - Deletions are strictly rejected over `GET`.
4. **Session Fixation Prevention**:
   - Sessions are cleared and regenerated upon login.
   - Session cookies configured with `HttpOnly` and `SameSite=Lax`.
5. **Information Leak Prevention**:
   - Raw database errors are caught and logged server-side rather than rendered to end users.
   - Sensitive credentials extracted to `.env`.

---

## Setup & Installation

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git (optional)
- MySQL / MariaDB (optional; SQLite works out-of-the-box with zero setup)

### Step 1: Clone or Navigate to the Project Root
```bash
cd "path/to/AVMS-Project-PHP (Microproject)"
```

### Step 2: Create and Activate a Virtual Environment
**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

By default, the application runs on SQLite (`instance/avms.db`) with zero external database setup required.

To connect to an existing MySQL / XAMPP database instead, update `.env`:
```env
DB_ENGINE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=avmsdb
```

---

## Running the Application

Start the development server:
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

### Default Credentials
- **Username**: `admin`
- **Password**: `Test@123`

*(On first login, the legacy MD5 password hash is automatically and transparently upgraded to a secure PBKDF2 hash in the database).*

---

## Test Suite & Verification

The project includes an automated test suite verifying all critical workflows:

Run the full test suite with verbose reporting:
```bash
python -m pytest -v
```

### Test Coverage Summary:
- **`test_auth.py`**:
  - `test_login_success_and_legacy_md5_upgrade`: Validates sign-in and password hash re-hashing.
  - `test_login_failure_invalid_password`: Validates rejection of bad passwords.
  - `test_login_failure_nonexistent_user`: Validates rejection of unknown accounts.
  - `test_logout`: Validates session termination.
  - `test_protected_routes_unauthenticated_redirect`: Validates that all administrative endpoints require authentication.
  - `test_forgot_password_and_reset`: End-to-end account recovery flow.
  - `test_change_password`: Authenticated password updates.
  - `test_profile_update`: Profile details persistence.
- **`test_visitors.py`**:
  - `test_visitor_registration`: Visitor check-in persistence.
  - `test_visitor_registration_validation`: Field validation logic.
  - `test_visitor_checkout_recording`: Outing remark and exit timestamp.
  - `test_visitor_search`: Search queries across name, mobile, and apartment.
  - `test_visitor_csv_export`: Full visitor registry CSV export.
- **`test_passes.py`**:
  - `test_pass_creation`: Pass generation and 8-digit random ID generation.
  - `test_pass_date_validation`: Rejection of inverted date ranges.
  - `test_pass_detail_printable_view`: Printable badge rendering.
  - `test_pass_deletion_csrf_safe`: Safe deletion via POST.
  - `test_passes_csv_export`: Pass registry CSV export.
- **`test_categories.py`**:
  - `test_category_creation_and_listing`: Category persistence.
  - `test_duplicate_category_rejection`: Unique category enforcement.
  - `test_category_deletion`: Category removal.
- **`test_reports.py`**:
  - `test_visitor_between_dates_report`: Date range visitor aggregation.
  - `test_pass_between_dates_report`: Date range pass aggregation.
  - `test_report_csv_export`: Custom date-range CSV downloads.
- **`test_security.py`**:
  - `test_security_headers`: Verification of standard HTTP security headers.
  - `test_sql_injection_resilience_in_login`: Resistance against authentication bypass payloads.
  - `test_sql_injection_resilience_in_search`: Resistance against UNION-based injection payloads.
  - `test_csrf_protection_enabled_in_app`: Strict 400 rejection on requests lacking CSRF tokens.

**Result**: 28 passed in ~24s with 100% success rate.

---

## Preservation of Original PHP Code

In strict accordance with project protection requirements:
- The verbatim legacy PHP codebase, original database dumps, and historical documentation are preserved in:
  ```text
  _backup_original_php/
  ├── avms/                # Original PHP scripts, CSS, fonts, vendor libraries
  ├── SQL File/            # Original avmsdb.sql MariaDB dump
  └── Readme.txt           # Historical setup notes
  ```
- This backup ensures historical reference and disaster recovery without leaving conflicting, duplicate applications mixed together in the active portfolio root.

---

## Limitations & Future Roadmap

### Current Limitations:
- Single administrator role (no fine-grained RBAC separating Gate Guards from Property Managers).
- Visitor photos currently use styled initials rather than live camera snapshot capture.

### Future Improvements:
- **Guard vs. Manager RBAC**: Distinct views for Gate Guards (check-in/out only) and Property Managers (reporting, billing, analytics).
- **Resident WhatsApp / SMS Notifications**: Automated webhooks notifying apartment owners when a guest arrives at the gate.
- **QR Code Scanning**: QR codes printed on physical passes for instant optical barcode scanning at the guardhouse.

---

## License
Distributed under the MIT License. See `LICENSE` for more information.

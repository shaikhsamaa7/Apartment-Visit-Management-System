"""
Database abstraction layer for Apartment Visit Management System (AVMS).
Provides unified, parameterized query execution across SQLite (default) and MySQL.
"""

import os
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from flask import g, current_app

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


def get_db():
    """Retrieve or create the database connection for the current application context."""
    if 'db' not in g:
        db_engine = current_app.config.get('DB_ENGINE', 'sqlite').lower()

        if db_engine == 'mysql' and PYMYSQL_AVAILABLE:
            mysql_host = current_app.config.get('MYSQL_HOST', 'localhost')
            mysql_user = current_app.config.get('MYSQL_USER', 'root')
            mysql_password = current_app.config.get('MYSQL_PASSWORD', '')
            mysql_db = current_app.config.get('MYSQL_DB', 'avmsdb')
            mysql_port = current_app.config.get('MYSQL_PORT', 3306)

            conn = pymysql.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                database=mysql_db,
                port=mysql_port,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            g.db = conn
            g.db_type = 'mysql'
        else:
            db_path = current_app.config.get('DATABASE_PATH')
            if not db_path:
                db_path = os.path.join(current_app.instance_path, 'avms.db')
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = conn
            g.db_type = 'sqlite'

    return g.db


def close_db(e=None):
    """Close the database connection on request teardown."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def _format_query(query):
    """Convert %s parameter placeholders to ? if using SQLite."""
    db_type = getattr(g, 'db_type', 'sqlite')
    if db_type == 'sqlite':
        return query.replace('%s', '?')
    return query


def query_db(query, args=(), one=False):
    """
    Execute a parameterized SQL query and return results as dictionaries.
    Guards completely against SQL injection.
    """
    db = get_db()
    db_type = getattr(g, 'db_type', 'sqlite')
    formatted_query = _format_query(query)

    if db_type == 'sqlite':
        cur = db.execute(formatted_query, args)
        rows = cur.fetchall()
        cur.close()
        results = [dict(row) for row in rows]
    else:
        with db.cursor() as cur:
            cur.execute(formatted_query, args)
            results = cur.fetchall()

    if one:
        return results[0] if results else None
    return results


def execute_db(query, args=(), commit=True):
    """
    Execute an INSERT, UPDATE, or DELETE query with parameter binding.
    Returns (lastrowid, rowcount).
    """
    db = get_db()
    db_type = getattr(g, 'db_type', 'sqlite')
    formatted_query = _format_query(query)

    if db_type == 'sqlite':
        cur = db.cursor()
        cur.execute(formatted_query, args)
        lastrowid = cur.lastrowid
        rowcount = cur.rowcount
        cur.close()
        if commit:
            db.commit()
        return lastrowid, rowcount
    else:
        with db.cursor() as cur:
            cur.execute(formatted_query, args)
            lastrowid = cur.lastrowid
            rowcount = cur.rowcount
        if commit:
            db.commit()
        return lastrowid, rowcount


def init_db(app):
    """Initialize database tables and default seed data if needed."""
    with app.app_context():
        db = get_db()
        db_type = getattr(g, 'db_type', 'sqlite')

        if db_type == 'sqlite':
            schema_path = os.path.join(app.root_path, 'database', 'schema_sqlite.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    db.executescript(f.read())
                db.commit()
        
        # Check if tbladmin has any records; if not, seed default admin
        admin = query_db("SELECT ID FROM tbladmin LIMIT 1", one=True)
        if not admin:
            # Default admin credentials: username 'admin', password 'Test@123'
            # Store legacy MD5 hash for backward-compatibility with original seed,
            # which will be upgraded seamlessly to Werkzeug PBKDF2 hash on login.
            legacy_md5 = hashlib.md5("Test@123".encode('utf-8')).hexdigest()
            execute_db(
                """INSERT INTO tbladmin (AdminName, UserName, MobileNumber, Email, Password, AdminRegdate)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                ("Admin user", "admin", 7898799797, "admin@gmail.com", legacy_md5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

        # Seed categories if empty
        cat_count = query_db("SELECT COUNT(*) as count FROM tblcategory", one=True)
        if not cat_count or cat_count['count'] == 0:
            default_categories = [
                'Maid', 'NewsPaper', 'Cook', 'Milkman', 'Driver',
                'Gardener', 'Car Cleaner', 'Guest', 'Maintenance', 'Delivery / Courier', 'Other'
            ]
            for cat in default_categories:
                execute_db("INSERT INTO tblcategory (categoryName) VALUES (%s)", (cat,))

        # Seed initial synthetic demonstration visitor if empty
        vis_count = query_db("SELECT COUNT(*) as count FROM tblvisitor", one=True)
        if not vis_count or vis_count['count'] == 0:
            execute_db(
                """INSERT INTO tblvisitor (categoryName, VisitorName, MobileNumber, Address, Apartment, Floor, WhomtoMeet, ReasontoMeet, EnterDate, remark, outtime)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                ("Guest", "Amit Kumar", 9876543210, "Tower B, Sector 62", "B-402", "4", "Rohan Sharma", "Personal Visit",
                 (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "Visit completed smoothly",
                 (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
            )
            execute_db(
                """INSERT INTO tblvisitor (categoryName, VisitorName, MobileNumber, Address, Apartment, Floor, WhomtoMeet, ReasontoMeet, EnterDate, remark, outtime)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                ("Delivery / Courier", "Rahul Verma", 9811223344, "Logistics Hub", "A-101", "1", "Priya Singh", "Parcel Delivery",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, None)
            )

        # Seed initial synthetic demonstration pass if empty
        pass_count = query_db("SELECT COUNT(*) as count FROM tblvisitorpass", one=True)
        if not pass_count or pass_count['count'] == 0:
            today_str = date.today().isoformat()
            next_month_str = (date.today() + timedelta(days=30)).isoformat()
            execute_db(
                """INSERT INTO tblvisitorpass (passnumber, categoryName, VisitorName, MobileNumber, Address, Apartment, Floor, passDetails, fromDate, toDate, creationDate)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (94395972, "Maid", "Savita Devi", 9123456780, "Green Valley Society", "A-101", "1", "Daily Housekeeping",
                 today_str, next_month_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

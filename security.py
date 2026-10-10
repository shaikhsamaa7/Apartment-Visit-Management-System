"""
Security middleware, CSRF protection, and cryptographic helpers for AVMS.
"""

import os
import secrets
import hashlib
from functools import wraps
from flask import session, request, abort, redirect, url_for, flash, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash


def generate_csrf_token():
    """Generate or retrieve a per-session CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf_token():
    """Verify incoming CSRF token on mutating HTTP requests."""
    # Skip CSRF check in testing if disabled
    if current_app.config.get('TESTING') and not current_app.config.get('WTF_CSRF_ENABLED', True):
        return

    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
        session_token = session.get('_csrf_token')
        if not token or not session_token or not secrets.compare_digest(token, session_token):
            flash("Security check failed (invalid or expired CSRF token). Please try submitting again.", "danger")
            abort(400, description="Invalid CSRF token")


def login_required(f):
    """Ensure that the administrator is authenticated before accessing view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def hash_password(password: str) -> str:
    """Generate secure password hash using PBKDF2/scrypt."""
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password_and_check_upgrade(stored_hash: str, provided_password: str):
    """
    Verify password against stored hash.
    Supports both legacy MD5 hashes (for seamless migration from original DB)
    and modern Werkzeug hashes.
    Returns (is_valid: bool, needs_upgrade: bool).
    """
    if not stored_hash:
        return False, False

    # Check modern Werkzeug hash format (e.g., 'pbkdf2:sha256:...' or 'scrypt:...')
    if stored_hash.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        is_valid = check_password_hash(stored_hash, provided_password)
        return is_valid, False

    # Legacy MD5 verification
    md5_attempt = hashlib.md5(provided_password.encode('utf-8')).hexdigest()
    if secrets.compare_digest(stored_hash.lower(), md5_attempt.lower()):
        return True, True  # Valid, but needs upgrade to secure modern hash

    return False, False


def add_security_headers(response):
    """Apply strict HTTP security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

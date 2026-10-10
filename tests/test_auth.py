"""
Tests for authentication, session management, and password security.
"""

from database.db import query_db


def test_login_success_and_legacy_md5_upgrade(app, client):
    """Test successful login with default credentials and verify automatic password hash upgrade."""
    with app.app_context():
        admin_before = query_db("SELECT Password FROM tbladmin WHERE UserName = 'admin'", one=True)
        # Check that initial seed has legacy 32-char MD5 hash
        assert len(admin_before['Password']) == 32

    # Perform login
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'Test@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back" in response.data or b"Dashboard" in response.data

    # Verify that the password hash in the database was automatically upgraded to modern secure PBKDF2 hash
    with app.app_context():
        admin_after = query_db("SELECT Password FROM tbladmin WHERE UserName = 'admin'", one=True)
        assert admin_after['Password'].startswith('pbkdf2:sha256:')
        assert len(admin_after['Password']) > 50


def test_login_failure_invalid_password(client):
    """Test login rejection when password does not match."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'WrongPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid Username or Password" in response.data


def test_login_failure_nonexistent_user(client):
    """Test login rejection when username does not exist."""
    response = client.post('/login', data={
        'username': 'nonexistent_user',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid Username or Password" in response.data


def test_logout(authenticated_client):
    """Test logout clears session and redirects to sign in."""
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"securely logged out" in response.data or b"Sign In" in response.data

    # Ensure subsequent visit to dashboard redirects to login
    dash_resp = authenticated_client.get('/dashboard')
    assert dash_resp.status_code == 302
    assert '/login' in dash_resp.headers['Location']


def test_protected_routes_unauthenticated_redirect(client):
    """Verify that unauthenticated access to protected endpoints redirects to login."""
    endpoints = [
        '/',
        '/dashboard',
        '/visitors/add',
        '/visitors/manage',
        '/visitors/search',
        '/passes/create',
        '/passes/manage',
        '/categories/',
        '/reports/visitors',
        '/reports/passes',
        '/profile',
        '/change-password'
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 302, f"Endpoint {ep} allowed unauthenticated access"
        assert '/login' in resp.headers['Location']


def test_forgot_password_and_reset(app, client):
    """Test end-to-end password recovery flow."""
    # 1. Provide matching email and phone
    verify_resp = client.post('/forgot-password', data={
        'email': 'admin@gmail.com',
        'contactno': '7898799797'
    }, follow_redirects=True)

    assert verify_resp.status_code == 200
    assert b"Set New Password" in verify_resp.data

    # 2. Reset password
    reset_resp = client.post('/reset-password', data={
        'newpassword': 'NewSecurePassword!987',
        'confirmpassword': 'NewSecurePassword!987'
    }, follow_redirects=True)

    assert reset_resp.status_code == 200
    assert b"successfully reset" in reset_resp.data

    # 3. Test login with newly set password
    login_resp = client.post('/login', data={
        'username': 'admin',
        'password': 'NewSecurePassword!987'
    }, follow_redirects=True)

    assert login_resp.status_code == 200
    assert b"Dashboard" in login_resp.data


def test_change_password(authenticated_client):
    """Test change password from authenticated session."""
    resp = authenticated_client.post('/change-password', data={
        'currentpassword': 'Test@123',
        'newpassword': 'UpdatedPassword@456',
        'confirmpassword': 'UpdatedPassword@456'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Password successfully changed" in resp.data


def test_profile_update(authenticated_client):
    """Test updating admin profile details."""
    resp = authenticated_client.post('/profile', data={
        'adminname': 'Super Administrator',
        'mobilenumber': '9988776655',
        'email': 'superadmin@example.com'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Admin profile successfully updated" in resp.data
    assert b"Super Administrator" in resp.data

"""
Tests for application security, HTTP headers, SQL injection resilience, and CSRF protection.
"""

from app import create_app


def test_security_headers(client):
    """Verify presence of security headers on all responses."""
    resp = client.get('/login')
    assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
    assert resp.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert resp.headers.get('X-XSS-Protection') == '1; mode=block'
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'


def test_sql_injection_resilience_in_login(client):
    """Verify that classical SQL injection attempts in login fail safely."""
    malicious_payloads = [
        "' OR '1'='1",
        "admin' --",
        "' OR 1=1 --",
        "admin' /*",
        "' UNION SELECT 1, 'admin', 'admin', 1, 'a@a.com', 'pwd', '2022' --"
    ]

    for payload in malicious_payloads:
        resp = client.post('/login', data={
            'username': payload,
            'password': 'any_password'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Invalid Username or Password" in resp.data


def test_sql_injection_resilience_in_search(authenticated_client):
    """Verify that SQL injection in visitor search is handled safely by query parameter binding."""
    malicious_query = "' UNION SELECT 1, 'hacked', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 --"
    resp = authenticated_client.get(f'/visitors/search?q={malicious_query}')
    assert resp.status_code == 200
    assert b"500 Internal" not in resp.data


def test_csrf_protection_enabled_in_app():
    """Verify CSRF token rejection on mutating requests when CSRF enforcement is enabled."""
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = True
    test_client = app.test_client()

    # Request without CSRF token
    resp = test_client.post('/login', data={'username': 'admin', 'password': 'password'})
    assert resp.status_code == 400

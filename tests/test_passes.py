"""
Tests for visitor pass creation, management, printing, and CSV export.
"""

from datetime import date, timedelta
from database.db import query_db


def test_pass_creation(authenticated_client, app):
    """Test generating a visitor pass and verifying 8-digit random pass number."""
    today_str = date.today().isoformat()
    future_str = (date.today() + timedelta(days=60)).isoformat()

    pass_data = {
        'category': 'Car Cleaner',
        'visname': 'Ramesh Kumar',
        'mobilenumber': '9414253625',
        'address': 'Sector 62, Noida',
        'apartment': 'A-512',
        'floor': '5',
        'passdescription': 'Car Cleaning Service',
        'fromdate': today_str,
        'todate': future_str
    }

    response = authenticated_client.post('/passes/create', data=pass_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ramesh Kumar" in response.data
    assert b"Car Cleaning Service" in response.data

    with app.app_context():
        vpass = query_db("SELECT * FROM tblvisitorpass WHERE VisitorName = 'Ramesh Kumar'", one=True)
        assert vpass is not None
        assert 10000000 <= vpass['passnumber'] <= 99999999
        assert vpass['Apartment'] == 'A-512'


def test_pass_date_validation(authenticated_client):
    """Test that From Date cannot be later than To Date."""
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    pass_data = {
        'category': 'Maid',
        'visname': 'Test Validation',
        'mobilenumber': '9123456789',
        'address': 'Test',
        'apartment': 'T-100',
        'floor': '1',
        'passdescription': 'Cleaning',
        'fromdate': today_str,
        'todate': yesterday_str
    }

    response = authenticated_client.post('/passes/create', data=pass_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"From Date cannot be later than To Date" in response.data


def test_pass_detail_printable_view(authenticated_client, app):
    """Test viewing a pass formatted as printable badge."""
    with app.app_context():
        p = query_db("SELECT ID FROM tblvisitorpass LIMIT 1", one=True)
        pass_id = p['ID']

    resp = authenticated_client.get(f'/passes/{pass_id}')
    assert resp.status_code == 200
    assert b"Print Pass Badge" in resp.data
    assert b"APARTMENT RESIDENTIAL COMPLEX" in resp.data


def test_pass_deletion_csrf_safe(authenticated_client, app):
    """Test safely deleting a pass using POST request."""
    # Create pass to delete
    today_str = date.today().isoformat()
    authenticated_client.post('/passes/create', data={
        'category': 'Other',
        'visname': 'To Be Deleted',
        'mobilenumber': '9000000000',
        'address': 'Temp',
        'apartment': 'Z-999',
        'floor': '9',
        'passdescription': 'Temporary',
        'fromdate': today_str,
        'todate': today_str
    }, follow_redirects=True)

    with app.app_context():
        p = query_db("SELECT ID, passnumber FROM tblvisitorpass WHERE VisitorName = 'To Be Deleted'", one=True)
        assert p is not None
        pass_id = p['ID']

    # Delete via POST
    del_resp = authenticated_client.post(f'/passes/{pass_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app.app_context():
        check_p = query_db("SELECT ID FROM tblvisitorpass WHERE ID = %s", (pass_id,), one=True)
        assert check_p is None


def test_passes_csv_export(authenticated_client):
    """Test exporting pass registry to CSV."""
    resp = authenticated_client.get('/passes/export')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/csv'
    assert b"Pass Number,Visitor Name,Category" in resp.data

"""
Tests for visitor registration, checkout, search, and CSV export.
"""

from database.db import query_db


def test_visitor_registration(authenticated_client, app):
    """Test registering a new visitor and checking database persistence."""
    data = {
        'category': 'Guest',
        'visname': 'Johnathan Doe',
        'mobilenumber': '9876543210',
        'address': 'Sector 18, Noida',
        'apartment': 'C-302',
        'floor': '3',
        'whomtomeet': 'Rajesh Sharma',
        'reasontomeet': 'Family Visit'
    }

    response = authenticated_client.post('/visitors/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Johnathan Doe" in response.data

    with app.app_context():
        vis = query_db("SELECT * FROM tblvisitor WHERE VisitorName = 'Johnathan Doe'", one=True)
        assert vis is not None
        assert vis['Apartment'] == 'C-302'
        assert vis['WhomtoMeet'] == 'Rajesh Sharma'
        assert vis['MobileNumber'] == 9876543210
        assert vis['remark'] is None


def test_visitor_registration_validation(authenticated_client):
    """Test that missing required fields displays validation error messages."""
    data = {
        'category': '',
        'visname': '',
        'mobilenumber': 'abc',
        'apartment': '',
        'floor': '',
        'whomtomeet': ''
    }

    response = authenticated_client.post('/visitors/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please select a visitor category" in response.data
    assert b"Visitor name is required" in response.data


def test_visitor_checkout_recording(authenticated_client, app):
    """Test recording an outing remark and exit timestamp upon visitor departure."""
    # Register visitor
    authenticated_client.post('/visitors/add', data={
        'category': 'Cook',
        'visname': 'Meera Devi',
        'mobilenumber': '9123456780',
        'address': 'Local Area',
        'apartment': 'B-101',
        'floor': '1',
        'whomtomeet': 'Pooja Gupta',
        'reasontomeet': 'Cooking'
    }, follow_redirects=True)

    with app.app_context():
        vis = query_db("SELECT ID FROM tblvisitor WHERE VisitorName = 'Meera Devi'", one=True)
        vis_id = vis['ID']

    # Submit checkout remark
    checkout_resp = authenticated_client.post(f'/visitors/{vis_id}', data={
        'remark': 'Cook has completed duties and exited the premises'
    }, follow_redirects=True)

    assert checkout_resp.status_code == 200
    assert b"check-out time and remark recorded" in checkout_resp.data

    with app.app_context():
        updated_vis = query_db("SELECT remark, outtime FROM tblvisitor WHERE ID = %s", (vis_id,), one=True)
        assert updated_vis['remark'] == 'Cook has completed duties and exited the premises'
        assert updated_vis['outtime'] is not None


def test_visitor_search(authenticated_client):
    """Test searching visitor records by name or mobile keyword."""
    # Register specific visitor
    authenticated_client.post('/visitors/add', data={
        'category': 'Driver',
        'visname': 'Gurpreet Singh',
        'mobilenumber': '9988112233',
        'address': 'Chandigarh',
        'apartment': 'D-505',
        'floor': '5',
        'whomtomeet': 'Vikram Seth',
        'reasontomeet': 'Driver Duty'
    }, follow_redirects=True)

    # Search by name
    res1 = authenticated_client.get('/visitors/search?q=Gurpreet')
    assert res1.status_code == 200
    assert b"Gurpreet Singh" in res1.data
    assert b"D-505" in res1.data

    # Search by phone
    res2 = authenticated_client.get('/visitors/search?q=9988112233')
    assert res2.status_code == 200
    assert b"Gurpreet Singh" in res2.data


def test_visitor_csv_export(authenticated_client):
    """Test exporting visitor records to CSV."""
    resp = authenticated_client.get('/visitors/export')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/csv'
    assert 'attachment;' in resp.headers['Content-Disposition']
    assert b"Visitor Name,Category,Mobile Number" in resp.data

"""
Tests for category management.
"""

from database.db import query_db


def test_category_creation_and_listing(authenticated_client, app):
    """Test creating a new category and verifying it appears in category list."""
    response = authenticated_client.post('/categories/', data={
        'categoryname': 'Plumbing Specialist'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Plumbing Specialist" in response.data

    with app.app_context():
        cat = query_db("SELECT * FROM tblcategory WHERE categoryName = 'Plumbing Specialist'", one=True)
        assert cat is not None


def test_duplicate_category_rejection(authenticated_client):
    """Test that creating a category with an existing name is rejected."""
    # Try adding 'Maid' which already exists in seed data
    response = authenticated_client.post('/categories/', data={
        'categoryname': 'Maid'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already exists" in response.data


def test_category_deletion(authenticated_client, app):
    """Test deleting category via safe POST action."""
    # Create category to delete
    authenticated_client.post('/categories/', data={'categoryname': 'TempCat'}, follow_redirects=True)
    with app.app_context():
        c = query_db("SELECT id FROM tblcategory WHERE categoryName = 'TempCat'", one=True)
        cat_id = c['id']

    del_resp = authenticated_client.post(f'/categories/{cat_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app.app_context():
        check_c = query_db("SELECT id FROM tblcategory WHERE id = %s", (cat_id,), one=True)
        assert check_c is None

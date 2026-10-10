"""
Pytest configuration and fixtures for AVMS.
"""

import os
import tempfile
import pytest
from app import create_app
from database.db import get_db, init_db, execute_db


@pytest.fixture
def app():
    """Create and configure a clean test application instance with temporary database."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Override config for testing
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-39281'
    })

    with app.app_context():
        init_db(app)

    yield app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """A test client with an active authenticated administrator session."""
    client.post('/login', data={
        'username': 'admin',
        'password': 'Test@123'
    }, follow_redirects=True)
    return client

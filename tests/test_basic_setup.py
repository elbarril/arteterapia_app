"""
Simple smoke tests to verify test infrastructure is working.
"""
import pytest
from app.models.user import User
from app.models.workshop import Workshop


class TestBasicSetup:
    """Basic tests to verify database and fixtures work."""
    
    def test_app_context(self, app):
        """Should have valid app context."""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_database_connection(self, app, db):
        """Should connect to test database."""
        with app.app_context():
            # Database should be accessible
            assert db is not None
    
    def test_admin_user_exists(self, app, admin_user):
        """Admin user should exist in test database."""
        with app.app_context():
            assert admin_user is not None
            assert admin_user.username == 'admin'
            assert admin_user.email == 'admin@test.com'
    
    def test_editor_user_exists(self, app, editor_user):
        """Editor user should exist in test database."""
        with app.app_context():
            assert editor_user is not None
            assert editor_user.username == 'editor'
            assert editor_user.email == 'editor@test.com'
    
    def test_admin_has_admin_role(self, app, admin_user):
        """Admin should have admin role."""
        with app.app_context():
            assert admin_user.is_admin() is True
    
    def test_sample_workshop_fixture(self, app, db, sample_workshop):
        """Sample workshop fixture should create workshop."""
        with app.app_context():
            workshop = Workshop.query.get(sample_workshop)
            assert workshop is not None
            assert workshop.id == sample_workshop

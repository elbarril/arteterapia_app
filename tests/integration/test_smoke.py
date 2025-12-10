"""
Basic smoke tests to verify the application and test infrastructure work.
"""
import pytest


@pytest.mark.integration
class TestApplicationSmoke:
    """Basic smoke tests for the application."""
    
    def test_app_exists(self, app):
        """Test that the Flask application instance is created."""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_database_tables_created(self, app, db_session):
        """Test that database tables are created."""
        from app import db
        assert len(db.metadata.tables) > 0
        # Check key tables exist
        assert 'user' in db.metadata.tables
        assert 'roles' in db.metadata.tables
        assert 'workshops' in db.metadata.tables
        assert 'participants' in db.metadata.tables
        assert 'sessions' in db.metadata.tables
        assert 'observational_records' in db.metadata.tables
    
    def test_client_works(self, client):
        """Test that the test client is functional."""
        response = client.get('/auth/login')
        assert response.status_code == 200
    
    def test_admin_user_fixture(self, admin_user):
        """Test that admin user fixture creates a user."""
        assert admin_user is not None
        assert admin_user.username == 'testadmin'
        assert admin_user.is_admin() is True
    
    def test_workshop_fixture(self, workshop):
        """Test that workshop fixture creates a workshop."""
        assert workshop is not None
        assert workshop.name == 'Test Workshop'

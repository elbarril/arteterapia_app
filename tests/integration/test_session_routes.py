"""
Integration tests for session routes.
Tests session CRUD operations within workshops.
"""
import pytest
from app.models.session import Session


@pytest.mark.integration
class TestSessionRoutes:
    """Test session routes integration."""
    
    def test_create_session(self, authenticated_client, workshop, db_session):
        """Test creating a session via AJAX."""
        response = authenticated_client.post(
            f'/workshop/{workshop.id}/session/create',
            json={
                'prompt': 'Test prompt',
                'motivation': 'Test motivation',
                'materials': 'paper, pencils'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify database
        session = Session.query.filter_by(prompt='Test prompt').first()
        assert session is not None
        assert session.workshop_id == workshop.id
        assert session.motivation == 'Test motivation'
        assert 'paper' in session.materials
    
    def test_update_session(self, authenticated_client, session_obj, db_session):
        """Test updating a session."""
        response = authenticated_client.post(
            f'/session/{session_obj.id}/update',
            json={
                'prompt': 'Updated prompt',
                'motivation': 'Updated motivation',
                'materials': 'canvas, paints'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify database
        session = Session.query.get(session_obj.id)
        assert session.prompt == 'Updated prompt'
        assert session.motivation == 'Updated motivation'
        assert 'canvas' in session.materials
    
    def test_delete_session(self, authenticated_client, session_obj, db_session):
        """Test deleting a session."""
        session_id = session_obj.id
        response = authenticated_client.post(
            f'/session/{session_id}/delete',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify database
        session = Session.query.get(session_id)
        assert session is None
    
    def test_create_session_requires_auth(self, client, workshop):
        """Test that creating session requires authentication."""
        response = client.post(
            f'/workshop/{workshop.id}/session/create',
            json={'prompt': 'Unauthorized session'},
            content_type='application/json'
        )
        assert response.status_code == 302  # Redirect to login

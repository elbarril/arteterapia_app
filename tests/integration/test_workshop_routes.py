"""
Integration tests for workshop routes.
Tests the complete request/response cycle for workshop CRUD operations.
"""
import pytest
from app.models.workshop import Workshop


@pytest.mark.integration
class TestWorkshopRoutes:
    """Test workshop routes integration."""
    
    def test_list_workshops_requires_auth(self, client):
        """Test that workshop list requires authentication."""
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
        assert b'/auth/login' in response.data or 'login' in response.location
    
    def test_list_workshops_authenticated(self, authenticated_client, workshop):
        """Test listing workshops when authenticated."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Test Workshop' in response.data
    
    def test_create_workshop(self, authenticated_client, db_session):
        """Test creating a new workshop."""
        response = authenticated_client.post('/workshop/create', data={
            'name': 'New Workshop'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        workshop = Workshop.query.filter_by(name='New Workshop').first()
        assert workshop is not None
        assert workshop.name == 'New Workshop'
    
    def test_workshop_detail(self, authenticated_client, workshop):
        """Test viewing workshop detail page."""
        response = authenticated_client.get(f'/workshop/{workshop.id}')
        assert response.status_code == 200
        assert b'Test Workshop' in response.data
        assert b'Participantes' in response.data
        assert b'Sesiones' in response.data
    
    def test_update_workshop_objective(self, authenticated_client, workshop):
        """Test updating workshop objective via AJAX."""
        response = authenticated_client.post(
            f'/workshop/{workshop.id}/objective',
            json={'objective': 'Updated objective'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify database was updated
        workshop = Workshop.query.get(workshop.id)
        assert workshop.objective == 'Updated objective'
    
    def test_delete_workshop(self, authenticated_client, workshop, db_session):
        """Test deleting a workshop."""
        workshop_id = workshop.id
        response = authenticated_client.post(
            f'/workshop/{workshop_id}/delete',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # Workshop should be deleted
        workshop = Workshop.query.get(workshop_id)
        assert workshop is None
    
    def test_create_workshop_requires_auth(self, client):
        """Test that creating workshop requires authentication."""
        response = client.post('/workshop/create', data={
            'name': 'Unauthorized Workshop'
        })
        assert response.status_code == 302  # Redirect to login
    
    def test_workshop_detail_requires_auth(self, client, workshop):
        """Test that workshop detail requires authentication."""
        response = client.get(f'/workshop/{workshop.id}')
        assert response.status_code == 302  # Redirect to login

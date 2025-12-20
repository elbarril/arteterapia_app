"""
Tests for session routes.

Tests all session routes including create, update, and delete operations.
"""
import pytest
from app.models.session import Session


class TestSessionCreate:
    """Tests for session creation route."""
    
    def test_create_requires_login(self, client, sample_workshop):
        """Test that session creation requires authentication."""
        response = client.post(f'/workshop/{sample_workshop}/session/create',
                             json={'prompt': 'Test prompt'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_create_session_success(self, client, db, admin_user, sample_workshop):
        """Test successful session creation."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/workshop/{sample_workshop}/session/create',
                             json={
                                 'prompt': 'New Session Prompt',
                                 'motivation': 'Test motivation',
                                 'materials': 'paint, canvas'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['session']['prompt'] == 'New Session Prompt'
        
        # Verify in database
        session = Session.query.filter_by(prompt='New Session Prompt').first()
        assert session is not None
        assert session.workshop_id == sample_workshop
    
    def test_create_session_empty_prompt(self, client, admin_user, sample_workshop):
        """Test session creation with empty prompt."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/workshop/{sample_workshop}/session/create',
                             json={'prompt': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_session_workshop_not_found(self, client, admin_user):
        """Test session creation with non-existent workshop."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/workshop/99999/session/create',
                             json={'prompt': 'Test'})
        
        assert response.status_code == 404
    
    def test_create_session_optional_fields(self, client, db, admin_user, sample_workshop):
        """Test session creation with only required fields."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/workshop/{sample_workshop}/session/create',
                             json={'prompt': 'Minimal Session'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestSessionUpdate:
    """Tests for session update route."""
    
    def test_update_requires_login(self, client, sample_session):
        """Test that session update requires authentication."""
        response = client.post(f'/session/{sample_session}/update',
                             json={'prompt': 'Updated Prompt'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_update_session_success(self, client, db, admin_user, sample_session):
        """Test successful session update."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/session/{sample_session}/update',
                             json={
                                 'prompt': 'Updated Prompt',
                                 'motivation': 'Updated motivation',
                                 'materials': 'new materials'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['session']['prompt'] == 'Updated Prompt'
        
        # Verify in database
        session = Session.query.get(sample_session)
        assert session.prompt == 'Updated Prompt'
    
    def test_update_session_empty_prompt(self, client, admin_user, sample_session):
        """Test session update with empty prompt."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/session/{sample_session}/update',
                             json={'prompt': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_session_not_found(self, client, admin_user):
        """Test session update with non-existent session."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/session/99999/update',
                             json={'prompt': 'Test'})
        
        assert response.status_code == 404
    
    def test_update_session_put_method(self, client, db, admin_user, sample_session):
        """Test session update using PUT method."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.put(f'/session/{sample_session}/update',
                            json={'prompt': 'PUT Updated'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestSessionDelete:
    """Tests for session deletion route."""
    
    def test_delete_requires_login(self, client, sample_session):
        """Test that session deletion requires authentication."""
        response = client.post(f'/session/{sample_session}/delete',
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_delete_session_success(self, client, db, admin_user, sample_session):
        """Test successful session deletion."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/session/{sample_session}/delete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify session was deleted
        session = Session.query.get(sample_session)
        assert session is None
    
    def test_delete_session_not_found(self, client, admin_user):
        """Test session deletion with non-existent session."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/session/99999/delete')
        
        assert response.status_code == 404
    
    def test_delete_session_delete_method(self, client, db, admin_user, sample_session):
        """Test session deletion using DELETE method."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.delete(f'/session/{sample_session}/delete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

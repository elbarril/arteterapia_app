"""
Tests for participant routes.

Tests all participant routes including create, update, and delete operations.
"""
import pytest
from app.models.participant import Participant


class TestParticipantCreate:
    """Tests for participant creation route."""
    
    def test_create_requires_login(self, client, sample_workshop):
        """Test that participant creation requires authentication."""
        response = client.post(f'/workshop/{sample_workshop}/participant/create',
                             json={'name': 'Test Participant'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_create_participant_success(self, client, db, admin_user, sample_workshop):
        """Test successful participant creation."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/workshop/{sample_workshop}/participant/create',
                             json={'name': 'New Participant'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['participant']['name'] == 'New Participant'
        
        # Verify in database
        participant = Participant.query.filter_by(name='New Participant').first()
        assert participant is not None
        assert participant.workshop_id == sample_workshop
    
    def test_create_participant_empty_name(self, client, admin_user, sample_workshop):
        """Test participant creation with empty name."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/workshop/{sample_workshop}/participant/create',
                             json={'name': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_participant_workshop_not_found(self, client, admin_user):
        """Test participant creation with non-existent workshop."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/workshop/99999/participant/create',
                             json={'name': 'Test'})
        
        assert response.status_code == 404


class TestParticipantUpdate:
    """Tests for participant update route."""
    
    def test_update_requires_login(self, client, sample_participant):
        """Test that participant update requires authentication."""
        response = client.post(f'/participant/{sample_participant}/update',
                             json={'name': 'Updated Name'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_update_participant_success(self, client, db, admin_user, sample_participant):
        """Test successful participant update."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/participant/{sample_participant}/update',
                             json={'name': 'Updated Participant'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['participant']['name'] == 'Updated Participant'
        
        # Verify in database
        participant = Participant.query.get(sample_participant)
        assert participant.name == 'Updated Participant'
    
    def test_update_participant_empty_name(self, client, admin_user, sample_participant):
        """Test participant update with empty name."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/participant/{sample_participant}/update',
                             json={'name': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_participant_not_found(self, client, admin_user):
        """Test participant update with non-existent participant."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/participant/99999/update',
                             json={'name': 'Test'})
        
        assert response.status_code == 404
    
    def test_update_participant_put_method(self, client, db, admin_user, sample_participant):
        """Test participant update using PUT method."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.put(f'/participant/{sample_participant}/update',
                            json={'name': 'PUT Updated'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestParticipantDelete:
    """Tests for participant deletion route."""
    
    def test_delete_requires_login(self, client, sample_participant):
        """Test that participant deletion requires authentication."""
        response = client.post(f'/participant/{sample_participant}/delete',
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_delete_participant_success(self, client, db, admin_user, sample_participant):
        """Test successful participant deletion."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/participant/{sample_participant}/delete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify participant was deleted
        participant = Participant.query.get(sample_participant)
        assert participant is None
    
    def test_delete_participant_not_found(self, client, admin_user):
        """Test participant deletion with non-existent participant."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/participant/99999/delete')
        
        assert response.status_code == 404
    
    def test_delete_participant_delete_method(self, client, db, admin_user, sample_participant):
        """Test participant deletion using DELETE method."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.delete(f'/participant/{sample_participant}/delete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

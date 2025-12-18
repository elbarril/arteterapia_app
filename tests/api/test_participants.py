"""
Tests for participant API endpoints.
"""
import pytest


class TestParticipantList:
    """Tests for GET /api/v1/participants/workshop/{id}"""
    
    def test_list_participants_success(self, client, admin_headers, sample_workshop, sample_participant):
        """Test listing participants for a workshop."""
        response = client.get(f'/api/v1/participants/workshop/{sample_workshop}',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p['id'] == sample_participant for p in data)
    
    def test_list_participants_workshop_not_found(self, client, admin_headers):
        """Test listing participants for non-existent workshop."""
        response = client.get('/api/v1/participants/workshop/99999',
                            headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_list_participants_without_auth(self, client, sample_workshop):
        """Test listing participants without authentication."""
        response = client.get(f'/api/v1/participants/workshop/{sample_workshop}')
        
        assert response.status_code == 401


class TestParticipantCreate:
    """Tests for POST /api/v1/participants"""
    
    def test_create_participant_success(self, client, admin_headers, sample_workshop):
        """Test creating a participant successfully."""
        response = client.post('/api/v1/participants',
                              headers=admin_headers,
                              json={
                                  'workshop_id': sample_workshop,
                                  'name': 'New Test Participant',
                                  'extra_data': {'age': 25}
                              })
        
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'New Test Participant'
        assert data['workshop_id'] == sample_workshop
        assert 'id' in data
    
    def test_create_participant_without_name(self, client, admin_headers, sample_workshop):
        """Test creating participant without name (required field)."""
        response = client.post('/api/v1/participants',
                              headers=admin_headers,
                              json={'workshop_id': sample_workshop})
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_create_participant_without_workshop_id(self, client, admin_headers):
        """Test creating participant without workshop_id."""
        response = client.post('/api/v1/participants',
                              headers=admin_headers,
                              json={'name': 'Test Participant'})
        
        assert response.status_code == 400
    
    def test_create_participant_invalid_workshop(self, client, admin_headers):
        """Test creating participant for non-existent workshop."""
        response = client.post('/api/v1/participants',
                              headers=admin_headers,
                              json={
                                  'workshop_id': 99999,
                                  'name': 'Test Participant'
                              })
        
        assert response.status_code == 404


class TestParticipantGet:
    """Tests for GET /api/v1/participants/{id}"""
    
    def test_get_participant_success(self, client, admin_headers, sample_participant):
        """Test getting participant details."""
        response = client.get(f'/api/v1/participants/{sample_participant}',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_participant
        assert data['name'] == 'Test Participant'
    
    def test_get_participant_not_found(self, client, admin_headers):
        """Test getting non-existent participant."""
        response = client.get('/api/v1/participants/99999',
                            headers=admin_headers)
        
        assert response.status_code == 404


class TestParticipantUpdate:
    """Tests for PATCH /api/v1/participants/{id}"""
    
    def test_update_participant_name(self, client, admin_headers, sample_participant):
        """Test updating participant name."""
        response = client.patch(f'/api/v1/participants/{sample_participant}',
                               headers=admin_headers,
                               json={'name': 'Updated Participant Name'})
        
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'Updated Participant Name'
    
    def test_update_participant_extra_data(self, client, admin_headers, sample_participant):
        """Test updating participant extra data."""
        response = client.patch(f'/api/v1/participants/{sample_participant}',
                               headers=admin_headers,
                               json={'extra_data': {'age': 30, 'notes': 'Test'}})
        
        assert response.status_code == 200
        assert response.json['extra_data']['age'] == 30
    
    def test_update_participant_not_found(self, client, admin_headers):
        """Test updating non-existent participant."""
        response = client.patch('/api/v1/participants/99999',
                               headers=admin_headers,
                               json={'name': 'Does not exist'})
        
        assert response.status_code == 404


class TestParticipantDelete:
    """Tests for DELETE /api/v1/participants/{id}"""
    
    def test_delete_participant_success(self, client, admin_headers, sample_participant):
        """Test deleting a participant."""
        response = client.delete(f'/api/v1/participants/{sample_participant}',
                                headers=admin_headers)
        
        assert response.status_code == 200
        assert 'message' in response.json
        
        # Verify it's deleted
        get_response = client.get(f'/api/v1/participants/{sample_participant}',
                                  headers=admin_headers)
        assert get_response.status_code == 404
    
    def test_delete_participant_not_found(self, client, admin_headers):
        """Test deleting non-existent participant."""
        response = client.delete('/api/v1/participants/99999',
                                headers=admin_headers)
        
        assert response.status_code == 404

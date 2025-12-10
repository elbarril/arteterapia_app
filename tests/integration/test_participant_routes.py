"""
Integration tests for participant routes.
Tests participant CRUD operations within workshops.
"""
import pytest
from app.models.participant import Participant


@pytest.mark.integration
class TestParticipantRoutes:
    """Test participant routes integration."""
    
    def test_create_participant(self, authenticated_client, workshop, db_session):
        """Test creating a participant via AJAX."""
        response = authenticated_client.post(
            f'/workshop/{workshop.id}/participant/create',
            json={'name': 'New Participant'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['participant']['name'] == 'New Participant'
        
        # Verify database
        participant = Participant.query.filter_by(name='New Participant').first()
        assert participant is not None
        assert participant.workshop_id == workshop.id
    
    def test_update_participant(self, authenticated_client, participant, db_session):
        """Test updating a participant name."""
        response = authenticated_client.post(
            f'/participant/{participant.id}/update',
            json={'name': 'Updated Name'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['participant']['name'] == 'Updated Name'
        
        # Verify database
        participant = Participant.query.get(participant.id)
        assert participant.name == 'Updated Name'
    
    def test_delete_participant(self, authenticated_client, participant, workshop, db_session):
        """Test deleting a participant."""
        participant_id = participant.id
        response = authenticated_client.post(
            f'/participant/{participant_id}/delete',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify database
        participant = Participant.query.get(participant_id)
        assert participant is None
    
    def test_create_participant_requires_auth(self, client, workshop):
        """Test that creating participant requires authentication."""
        response = client.post(
            f'/workshop/{workshop.id}/participant/create',
            json={'name': 'Unauthorized Participant'},
            content_type='application/json'
        )
        assert response.status_code == 302  # Redirect to login

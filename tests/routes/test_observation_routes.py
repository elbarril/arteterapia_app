"""
Tests for observation routes.

Tests all observation routes including start, process answer,
complete, and view observations.
"""
import pytest
from app.models.observation import ObservationalRecord


class TestObservationStart:
    """Tests for starting observation route."""
    
    def test_start_requires_login(self, client, sample_session, sample_participant):
        """Test that starting observation requires authentication."""
        response = client.get(f'/session/{sample_session}/observe/{sample_participant}',
                            follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_start_observation_success(self, client, db, admin_user, sample_session, sample_participant):
        """Test successful observation start."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/session/{sample_session}/observe/{sample_participant}')
        
        assert response.status_code == 200
        # Should show observation form
        assert b'pregunta' in response.data.lower() or b'question' in response.data.lower()
    
    def test_start_observation_session_not_found(self, client, admin_user, sample_participant):
        """Test starting observation with non-existent session."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/session/99999/observe/{sample_participant}',
                            follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_start_observation_participant_not_found(self, client, admin_user, sample_session):
        """Test starting observation with non-existent participant."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/session/{sample_session}/observe/99999',
                            follow_redirects=False)
        
        assert response.status_code == 302


class TestObservationProcessAnswer:
    """Tests for processing observation answers."""
    
    def test_process_answer_requires_login(self, client):
        """Test that processing answer requires authentication."""
        response = client.post('/observation/answer',
                             json={'answer': 'yes', 'question_id': 'test'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_process_answer_no_session_data(self, client, admin_user):
        """Test processing answer without session data."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/observation/answer',
                             json={'answer': 'yes', 'question_id': 'test'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestObservationComplete:
    """Tests for completing observation."""
    
    def test_complete_requires_login(self, client):
        """Test that completing observation requires authentication."""
        response = client.post('/observation/complete',
                             json={'freeform_notes': 'Test notes'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_complete_no_session_data(self, client, admin_user):
        """Test completing observation without session data."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/observation/complete',
                             json={'freeform_notes': 'Test notes'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestObservationView:
    """Tests for viewing observations."""
    
    def test_view_requires_login(self, client, sample_workshop):
        """Test that viewing observations requires authentication."""
        response = client.get(f'/workshop/{sample_workshop}/observations',
                            follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_view_observations_success(self, client, db, admin_user, sample_workshop):
        """Test successful observation view."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/workshop/{sample_workshop}/observations')
        
        assert response.status_code == 200
        # Should show observations table
        assert b'observ' in response.data.lower()
    
    def test_view_observations_workshop_not_found(self, client, admin_user):
        """Test viewing observations with non-existent workshop."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/workshop/99999/observations',
                            follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_view_observations_with_data(self, client, db, admin_user, sample_observation):
        """Test viewing observations with existing observation data."""
        # Get the observation to find its workshop
        observation = ObservationalRecord.query.get(sample_observation)
        workshop_id = observation.session.workshop_id
        
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/workshop/{workshop_id}/observations')
        
        assert response.status_code == 200
        assert b'Test observation notes' in response.data or b'observ' in response.data.lower()

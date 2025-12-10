"""
Integration tests for observation routes.
Tests the observation recording flow.
"""
import pytest
from app.models.observation import ObservationalRecord
from app.models.observation_questions import get_all_questions


@pytest.mark.integration
class TestObservationRoutes:
    """Test observation routes integration."""
    
    def test_start_observation(self, authenticated_client, session_obj, participant):
        """Test starting an observation flow."""
        response = authenticated_client.get(
            f'/session/{session_obj.id}/observe/{participant.id}'
        )
        
        assert response.status_code == 200
        assert b'Pregunta' in response.data
        # Should show first question
        questions = get_all_questions()
        first_question_text = questions[0]['text'].encode('utf-8')
        assert first_question_text in response.data
    
    def test_process_answer(self, authenticated_client, session_obj, participant, db_session):
        """Test submitting an answer via AJAX."""
        questions = get_all_questions()
        first_question_id = questions[0]['id']
        
        # Start observation first
        authenticated_client.get(
            f'/session/{session_obj.id}/observe/{participant.id}'
        )
        
        # Submit answer
        response = authenticated_client.post(
            '/observation/process-answer',
            json={
                'question_id': first_question_id,
                'answer': 'yes'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['has_more'] is True  # Should have more questions
        assert 'next_question' in data
    
    def test_complete_observation(self, authenticated_client, session_obj, participant, db_session):
        """Test completing an observation with notes."""
        # Start observation
        authenticated_client.get(
            f'/session/{session_obj.id}/observe/{participant.id}'
        )
        
        # Answer all questions (simulate)
        questions = get_all_questions()
        for question in questions:
            authenticated_client.post(
                '/observation/process-answer',
                json={
                    'question_id': question['id'],
                    'answer': 'yes'
                },
                content_type='application/json'
            )
        
        # Complete observation
        response = authenticated_client.post(
            '/observation/complete',
            json={'freeform_notes': 'Test notes'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'redirect_url' in data
        
        # Verify database
        observation = ObservationalRecord.query.filter_by(
            session_id=session_obj.id,
            participant_id=participant.id
        ).first()
        assert observation is not None
        assert observation.notes == 'Test notes'
    
    def test_view_observations(self, authenticated_client, workshop):
        """Test viewing all observations for a workshop."""
        response = authenticated_client.get(
            f'/observation/view/{workshop.id}'
        )
        
        assert response.status_code == 200
        assert b'Registros' in response.data or b'Observaciones' in response.data
    
    def test_observation_requires_auth(self, client, session_obj, participant):
        """Test that observation requires authentication."""
        response = client.get(
            f'/session/{session_obj.id}/observe/{participant.id}'
        )
        assert response.status_code == 302  # Redirect to login

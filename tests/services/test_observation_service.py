"""
Tests for ObservationService.

Tests observation workflow, answer processing, and permission checks.
"""
import pytest
from app.services.observation_service import ObservationService
from app.models.observation import ObservationalRecord
from app.models.user import User


class TestObservationServiceValidation:
    """Tests for observation context validation."""
    
    def test_validate_context_success(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should validate matching session and participant."""
        with app.app_context():
            session, participant, error = ObservationService.validate_observation_context(
                session_id=sample_session,
                participant_id=sample_participant,
                user_id=admin_user.id
            )
            
            assert session is not None
            assert participant is not None
            assert error is None
    
    def test_validate_context_participant_session_mismatch(self, app, db, admin_user, sample_workshop, sample_session):
        """Should reject participant not in session's workshop."""
        with app.app_context():
            # Create different workshop and participant
            from app.services.workshop_service import WorkshopService
            from app.services.participant_service import ParticipantService
            
            different_workshop = WorkshopService.create_workshop(
                user_id=admin_user.id,
                name='Different Workshop'
            )
            different_participant = ParticipantService.create_participant(
                workshop_id=different_workshop.id,
                user_id=admin_user.id,
                name='Different Participant'
            )
            
            session, participant, error = ObservationService.validate_observation_context(
                session_id=sample_session,
                participant_id=different_participant.id,
                user_id=admin_user.id
            )
            
            assert session is None
            assert participant is None
            assert error is not None
    
    def test_validate_context_no_permission(self, app, db, admin_user, editor_user, sample_workshop, sample_participant, sample_session):
        """Should reject unauthorized user."""
        with app.app_context():
            session, participant, error = ObservationService.validate_observation_context(
                session_id=sample_session,
                participant_id=sample_participant,
                user_id=editor_user.id
            )
            
            if admin_user.id != editor_user.id:
                assert session is None
                assert participant is None
                assert error is not None


class TestObservationServiceInitialize:
    """Tests for initializing observation."""
    
    def test_initialize_observation_first_time(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should initialize observation for first time."""
        with app.app_context():
            obs_data, error = ObservationService.initialize_observation(
                session_id=sample_session,
                participant_id=sample_participant,
                user_id=admin_user.id
            )
            
            assert obs_data is not None
            assert error is None
            assert obs_data['session_id'] == sample_session
            assert obs_data['participant_id'] == sample_participant
            assert obs_data['answers'] == {}
            assert obs_data['previous_version'] == 0
    
    def test_initialize_observation_with_previous(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should pre-fill from previous observation."""
        with app.app_context():
            # Create previous observation
            previous_obs = ObservationalRecord(
                session_id=sample_session,
                participant_id=sample_participant,
                answers={'entry_on_time': 'yes', 'motivation_interest': 'yes'},
                version=1
            )
            db.session.add(previous_obs)
            db.session.commit()
            
            # Initialize new observation
            obs_data, error = ObservationService.initialize_observation(
                session_id=sample_session,
                participant_id=sample_participant,
                user_id=admin_user.id
            )
            
            assert obs_data is not None
            assert error is None
            assert obs_data['answers'] == {'entry_on_time': 'yes', 'motivation_interest': 'yes'}
            assert obs_data['previous_version'] == 1


class TestObservationServiceProcessAnswer:
    """Tests for  processing answers."""
    
    def test_process_answer(self):
        """Should update answers in observation data."""
        obs_data = {
            'session_id': 1,
            'participant_id': 1,
            'answers': {},
            'current_index': 0
        }
        
        updated = ObservationService.process_answer(
            obs_data,
            'entry_on_time',
            'yes'
        )
        
        assert updated['answers']['entry_on_time'] == 'yes'
        assert updated['current_index'] == 1
    
    def test_process_multiple_answers(self):
        """Should accumulate multiple answers."""
        obs_data = {
            'session_id': 1,
            'participant_id': 1,
            'answers': {},
            'current_index': 0
        }
        
        obs_data = ObservationService.process_answer(obs_data, 'q1', 'yes')
        obs_data = ObservationService.process_answer(obs_data, 'q2', 'no')
        
        assert obs_data['answers']['q1'] == 'yes'
        assert obs_data['answers']['q2'] == 'no'
        assert obs_data['current_index'] == 2


class TestObservationServiceSave:
    """Tests for saving observations."""
    
    def test_save_observation_success(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should save observation successfully."""
        with app.app_context():
            obs_data = {
                'session_id': sample_session,
                'participant_id': sample_participant,
                'answers': {'entry_on_time': 'yes'},
                'previous_version': 0
            }
            
            record, error = ObservationService.save_observation(
                observation_data=obs_data,
                freeform_notes='Test notes',
                user_id=admin_user.id
            )
            
            assert record is not None
            assert error is None
            assert record.answers == {'entry_on_time': 'yes'}
            assert record.freeform_notes == 'Test notes'
            assert record.version == 1
    
    def test_save_observation_versioning(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should increment version correctly."""
        with app.app_context():
            # Save first observation
            obs_data1 = {
                'session_id': sample_session,
                'participant_id': sample_participant,
                'answers': {'q1': 'yes'},
                'previous_version': 0
            }
            record1, _ = ObservationService.save_observation(obs_data1, '', admin_user.id)
            
            # Save second observation
            obs_data2 = {
                'session_id': sample_session,
                'participant_id': sample_participant,
                'answers': {'q1': 'no'},
                'previous_version': 1
            }
            record2, _ = ObservationService.save_observation(obs_data2, '', admin_user.id)
            
            assert record1.version == 1
            assert record2.version == 2


class TestObservationServiceGet:
    """Tests for getting observations."""
    
    def test_get_workshop_observations(self, app, db, admin_user, sample_workshop, sample_observation):
        """Should get workshop observations."""
        with app.app_context():
            observations, error = ObservationService.get_workshop_observations(
                workshop_id=sample_workshop,
                user_id=admin_user.id
            )
            
            assert observations is not None
            assert error is None
            assert len(observations) >= 1
    
    def test_get_workshop_observations_no_permission(self, app, db, admin_user, editor_user, sample_workshop):
        """Should reject unauthorized access."""
        with app.app_context():
            observations, error = ObservationService.get_workshop_observations(
                workshop_id=sample_workshop,
                user_id=editor_user.id
            )
            
            if admin_user.id != editor_user.id:
                assert observations is None
                assert error is not None
    
    def test_get_observation_count(self, app, db, admin_user, sample_workshop, sample_participant, sample_session):
        """Should count observations correctly."""
        with app.app_context():
            # Create observations
            for i in range(3):
                obs_data = {
                    'session_id': sample_session,
                    'participant_id': sample_participant,
                    'answers': {'q': 'yes'},
                    'previous_version': i
                }
                ObservationService.save_observation(obs_data, '', admin_user.id)
            
            count = ObservationService.get_observation_count(
                sample_session,
                sample_participant
            )
            
            assert count >= 3


class TestObservationServiceDelete:
    """Tests for deleting observations."""
    
    def test_delete_observation_success(self, app, db, admin_user, sample_workshop, sample_observation):
        """Should delete observation successfully."""
        with app.app_context():
            success, error = ObservationService.delete_observation(
                observation_id=sample_observation,
                user_id=admin_user.id
            )
            
            assert success is True
            assert error is None
            
            # Verify deletion
            deleted = ObservationalRecord.query.get(sample_observation)
            assert deleted is None
    
    def test_delete_observation_no_permission(self, app, db, admin_user, editor_user, sample_workshop, sample_observation):
        """Should reject unauthorized deletion."""
        with app.app_context():
            success, error = ObservationService.delete_observation(
                observation_id=sample_observation,
                user_id=editor_user.id
            )
            
            if admin_user.id != editor_user.id:
                assert success is False
                assert error is not None

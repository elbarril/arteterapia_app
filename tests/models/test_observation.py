"""Tests for ObservationalRecord model."""
import pytest
from app.models.observation import ObservationalRecord
from app.models.participant import Participant
from app.models.session import Session
from app.models.workshop import Workshop


class TestObservationalRecordModel:
    """Tests for ObservationalRecord model basic functionality."""
    
    def test_create_observation(self, db, sample_session, sample_participant):
        """Test creating a new observational record."""
        answers = {
            'entry_on_time': 'yes',
            'entry_resistance': 'no',
            'motivation_interest': 'yes'
        }
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers=answers,
            freeform_notes='Test notes'
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.id is not None
        assert observation.session_id == sample_session
        assert observation.participant_id == sample_participant
        assert observation.version == 1
        assert observation.answers == answers
        assert observation.freeform_notes == 'Test notes'
        assert observation.created_at is not None
    
    def test_observation_repr(self, db, sample_session, sample_participant):
        """Test observation string representation."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        expected = f'<ObservationalRecord {observation.id} - Session {sample_session}, Participant {sample_participant}, v1>'
        assert repr(observation) == expected
    
    def test_observation_default_version(self, db, sample_session, sample_participant):
        """Test that version defaults to 1."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.version == 1
    
    def test_observation_without_notes(self, db, sample_session, sample_participant):
        """Test creating observation without freeform notes."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.freeform_notes is None


class TestObservationalRecordAnswers:
    """Tests for ObservationalRecord answers functionality."""
    
    def test_get_answer_existing(self, db, sample_session, sample_participant):
        """Test getting an existing answer."""
        answers = {'entry_on_time': 'yes', 'entry_resistance': 'no'}
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers=answers
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.get_answer('entry_on_time') == 'yes'
        assert observation.get_answer('entry_resistance') == 'no'
    
    def test_get_answer_nonexistent(self, db, sample_session, sample_participant):
        """Test getting a non-existent answer."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'entry_on_time': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.get_answer('nonexistent_question') is None
    
    def test_get_answer_empty_answers(self, db, sample_session, sample_participant):
        """Test getting answer when answers is empty."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.get_answer('any_question') is None
    
    def test_answers_json_storage(self, db, sample_session, sample_participant):
        """Test that answers are properly stored as JSON."""
        complex_answers = {
            'question1': 'yes',
            'question2': 'no',
            'question3': 'not_sure',
            'question4': 'not_applicable'
        }
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers=complex_answers
        )
        db.session.add(observation)
        db.session.commit()
        
        # Retrieve from database
        retrieved = ObservationalRecord.query.get(observation.id)
        assert retrieved.answers == complex_answers


class TestObservationalRecordVersioning:
    """Tests for ObservationalRecord versioning functionality."""
    
    def test_get_latest_version_no_observations(self, db, sample_session, sample_participant):
        """Test get_latest_version when no observations exist."""
        version = ObservationalRecord.get_latest_version(
            sample_session,
            sample_participant
        )
        assert version == 0
    
    def test_get_latest_version_single(self, db, sample_session, sample_participant):
        """Test get_latest_version with single observation."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        version = ObservationalRecord.get_latest_version(
            sample_session,
            sample_participant
        )
        assert version == 1
    
    def test_get_latest_version_multiple(self, db, sample_session, sample_participant):
        """Test get_latest_version with multiple versions."""
        obs1 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers={}
        )
        obs2 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=2,
            answers={}
        )
        obs3 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=3,
            answers={}
        )
        db.session.add_all([obs1, obs2, obs3])
        db.session.commit()
        
        version = ObservationalRecord.get_latest_version(
            sample_session,
            sample_participant
        )
        assert version == 3
    
    def test_multiple_participants_separate_versions(self, db, sample_session, sample_workshop):
        """Test that versions are tracked separately per participant."""
        workshop = Workshop.query.get(sample_workshop)
        
        # Create two participants
        p1 = Participant(name='Participant 1', workshop_id=workshop.id)
        p2 = Participant(name='Participant 2', workshop_id=workshop.id)
        db.session.add_all([p1, p2])
        db.session.commit()
        
        # Create observations for each
        obs1 = ObservationalRecord(
            session_id=sample_session,
            participant_id=p1.id,
            version=1,
            answers={}
        )
        obs2 = ObservationalRecord(
            session_id=sample_session,
            participant_id=p2.id,
            version=1,
            answers={}
        )
        obs3 = ObservationalRecord(
            session_id=sample_session,
            participant_id=p2.id,
            version=2,
            answers={}
        )
        db.session.add_all([obs1, obs2, obs3])
        db.session.commit()
        
        # Check versions are separate
        v1 = ObservationalRecord.get_latest_version(sample_session, p1.id)
        v2 = ObservationalRecord.get_latest_version(sample_session, p2.id)
        
        assert v1 == 1
        assert v2 == 2


class TestObservationalRecordHasObservation:
    """Tests for ObservationalRecord has_observation static method."""
    
    def test_has_observation_false(self, db, sample_session, sample_participant):
        """Test has_observation when no observation exists."""
        result = ObservationalRecord.has_observation(
            sample_session,
            sample_participant
        )
        assert result is False
    
    def test_has_observation_true(self, db, sample_session, sample_participant):
        """Test has_observation when observation exists."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        result = ObservationalRecord.has_observation(
            sample_session,
            sample_participant
        )
        assert result is True
    
    def test_has_observation_different_session(self, db, sample_session, sample_participant, sample_workshop):
        """Test has_observation for different session."""
        workshop = Workshop.query.get(sample_workshop)
        
        # Create observation for sample_session
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        # Create different session
        other_session = Session(workshop_id=workshop.id, prompt='Other')
        db.session.add(other_session)
        db.session.commit()
        
        # Check for observation in different session
        result = ObservationalRecord.has_observation(
            other_session.id,
            sample_participant
        )
        assert result is False


class TestObservationalRecordRelationships:
    """Tests for ObservationalRecord relationships."""
    
    def test_observation_session_relationship(self, db, sample_session, sample_participant):
        """Test observation-session relationship."""
        session = Session.query.get(sample_session)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.session == session
    
    def test_observation_participant_relationship(self, db, sample_session, sample_participant):
        """Test observation-participant relationship."""
        participant = Participant.query.get(sample_participant)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation.participant == participant


class TestObservationalRecordConstraints:
    """Tests for ObservationalRecord constraints."""
    
    def test_observation_requires_session_id(self, db, sample_participant):
        """Test that observation requires a session_id."""
        observation = ObservationalRecord(
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_observation_requires_participant_id(self, db, sample_session):
        """Test that observation requires a participant_id."""
        observation = ObservationalRecord(
            session_id=sample_session,
            answers={}
        )
        db.session.add(observation)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite allows NULL by default, answers field has default=dict")
    def test_observation_requires_answers(self, db, sample_session, sample_participant):
        """Test that observation requires answers field."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant
        )
        db.session.add(observation)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
    def test_observation_invalid_session_id(self, db, sample_participant):
        """Test that observation requires valid session_id."""
        observation = ObservationalRecord(
            session_id=99999,
            participant_id=sample_participant,
            answers={}
        )
        db.session.add(observation)
        
        with pytest.raises(Exception):  # IntegrityError (foreign key)
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
    def test_observation_invalid_participant_id(self, db, sample_session):
        """Test that observation requires valid participant_id."""
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=99999,
            answers={}
        )
        db.session.add(observation)
        
        with pytest.raises(Exception):  # IntegrityError (foreign key)
            db.session.commit()

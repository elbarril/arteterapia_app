"""Tests for Session model."""
import pytest
from app.models.session import Session
from app.models.workshop import Workshop
from app.models.observation import ObservationalRecord


class TestSessionModel:
    """Tests for Session model basic functionality."""
    
    def test_create_session(self, db, sample_workshop):
        """Test creating a new session."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(
            workshop_id=workshop.id,
            prompt='Test prompt',
            motivation='Test motivation',
            materials=['paint', 'canvas']
        )
        db.session.add(session)
        db.session.commit()
        
        assert session.id is not None
        assert session.workshop_id == workshop.id
        assert session.prompt == 'Test prompt'
        assert session.motivation == 'Test motivation'
        assert session.materials == ['paint', 'canvas']
        assert session.created_at is not None
    
    def test_session_repr(self, db, sample_session):
        """Test session string representation."""
        session = Session.query.get(sample_session)
        expected = f'<Session {session.id} - {session.prompt[:30]}>'
        assert repr(session) == expected
    
    def test_session_without_optional_fields(self, db, sample_workshop):
        """Test creating session without optional fields."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(
            workshop_id=workshop.id,
            prompt='Minimal session'
        )
        db.session.add(session)
        db.session.commit()
        
        assert session.motivation is None
        assert session.materials is None


class TestSessionProperties:
    """Tests for Session computed properties."""
    
    def test_has_observations_false(self, db, sample_workshop):
        """Test has_observations for session with no observations."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(workshop_id=workshop.id, prompt='Test')
        db.session.add(session)
        db.session.commit()
        
        assert session.has_observations is False
    
    def test_has_observations_true(self, db, sample_session, sample_participant):
        """Test has_observations for session with observations."""
        session = Session.query.get(sample_session)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert session.has_observations is True
    
    def test_observation_count_zero(self, db, sample_workshop):
        """Test observation count for session with no observations."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(workshop_id=workshop.id, prompt='Test')
        db.session.add(session)
        db.session.commit()
        
        assert session.observation_count == 0
    
    def test_observation_count_multiple(self, db, sample_session, sample_participant):
        """Test observation count with multiple observations."""
        session = Session.query.get(sample_session)
        # Create multiple observations (different versions)
        obs1 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers={'test': 'yes'}
        )
        obs2 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=2,
            answers={'test': 'no'}
        )
        db.session.add_all([obs1, obs2])
        db.session.commit()
        
        assert session.observation_count == 2


class TestSessionMethods:
    """Tests for Session instance methods."""
    
    def test_has_observation_for_true(self, db, sample_session, sample_participant):
        """Test has_observation_for when observation exists."""
        session = Session.query.get(sample_session)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert session.has_observation_for(sample_participant) is True
    
    def test_has_observation_for_false(self, db, sample_session, sample_participant):
        """Test has_observation_for when observation doesn't exist."""
        session = Session.query.get(sample_session)
        assert session.has_observation_for(sample_participant) is False
    
    def test_get_observation_count_for_zero(self, db, sample_session, sample_participant):
        """Test get_observation_count_for with no observations."""
        session = Session.query.get(sample_session)
        count = session.get_observation_count_for(sample_participant)
        assert count == 0
    
    def test_get_observation_count_for_multiple(self, db, sample_session, sample_participant):
        """Test get_observation_count_for with multiple versions."""
        session = Session.query.get(sample_session)
        # Create multiple versions for same participant
        obs1 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=1,
            answers={'test': 'yes'}
        )
        obs2 = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            version=2,
            answers={'test': 'no'}
        )
        db.session.add_all([obs1, obs2])
        db.session.commit()
        
        count = session.get_observation_count_for(sample_participant)
        assert count == 2


class TestSessionToDict:
    """Tests for Session to_dict method."""
    
    def test_to_dict_basic(self, db, sample_session):
        """Test converting session to dictionary."""
        session = Session.query.get(sample_session)
        data = session.to_dict()
        
        assert data['id'] == session.id
        assert data['workshop_id'] == session.workshop_id
        assert data['prompt'] == session.prompt
        assert 'motivation' in data
        assert 'materials' in data
        assert 'created_at' in data
        assert 'has_observations' in data
        assert 'observation_count' in data
    
    def test_to_dict_materials_default(self, db, sample_workshop):
        """Test to_dict with None materials returns empty list."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(workshop_id=workshop.id, prompt='Test')
        db.session.add(session)
        db.session.commit()
        
        data = session.to_dict()
        assert data['materials'] == []
    
    def test_to_dict_with_materials(self, db, sample_workshop):
        """Test to_dict with materials list."""
        workshop = Workshop.query.get(sample_workshop)
        materials = ['paint', 'brushes', 'canvas']
        session = Session(
            workshop_id=workshop.id,
            prompt='Test',
            materials=materials
        )
        db.session.add(session)
        db.session.commit()
        
        data = session.to_dict()
        assert data['materials'] == materials


class TestSessionRelationships:
    """Tests for Session relationships."""
    
    def test_session_workshop_relationship(self, db, sample_session, sample_workshop):
        """Test session-workshop relationship."""
        session = Session.query.get(sample_session)
        workshop = Workshop.query.get(sample_workshop)
        assert session.workshop == workshop
    
    def test_session_observations_relationship(self, db, sample_session, sample_participant):
        """Test session-observations relationship."""
        session = Session.query.get(sample_session)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation in session.observations.all()
    
    def test_delete_session_cascades_to_observations(self, db, sample_session, sample_participant):
        """Test that deleting session deletes observations."""
        session = Session.query.get(sample_session)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        session_id = session.id
        observation_id = observation.id
        
        db.session.delete(session)
        db.session.commit()
        
        assert Session.query.get(session_id) is None
        assert ObservationalRecord.query.get(observation_id) is None


class TestSessionConstraints:
    """Tests for Session constraints."""
    
    def test_session_requires_prompt(self, db, sample_workshop):
        """Test that session requires a prompt."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session(workshop_id=workshop.id)
        db.session.add(session)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_session_requires_workshop_id(self, db):
        """Test that session requires a workshop_id."""
        session = Session(prompt='Test prompt')
        db.session.add(session)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
    def test_session_invalid_workshop_id(self, db):
        """Test that session requires valid workshop_id."""
        session = Session(prompt='Test', workshop_id=99999)
        db.session.add(session)
        
        with pytest.raises(Exception):  # IntegrityError (foreign key)
            db.session.commit()

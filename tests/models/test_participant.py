"""Tests for Participant model."""
import pytest
from app.models.participant import Participant
from app.models.observation import ObservationalRecord


class TestParticipantModel:
    """Tests for Participant model basic functionality."""
    
    def test_create_participant(self, db, sample_workshop):
        """Test creating a new participant."""
        participant = Participant(
            name='Test Participant',
            workshop_id=sample_workshop
        )
        db.session.add(participant)
        db.session.commit()
        
        assert participant.id is not None
        assert participant.name == 'Test Participant'
        assert participant.workshop_id == sample_workshop
        assert participant.created_at is not None
        assert participant.extra_data is None
    
    def test_participant_repr(self, db, sample_participant):
        """Test participant string representation."""
        participant = Participant.query.get(sample_participant)
        assert repr(participant) == f'<Participant {participant.name}>'
    
    def test_participant_with_extra_data(self, db, sample_workshop):
        """Test creating participant with extra data."""
        extra = {'age': 25, 'notes': 'Test notes'}
        participant = Participant(
            name='Test Participant',
            workshop_id=sample_workshop,
            extra_data=extra
        )
        db.session.add(participant)
        db.session.commit()
        
        assert participant.extra_data == extra
        assert participant.extra_data['age'] == 25


class TestParticipantToDict:
    """Tests for Participant to_dict method."""
    
    def test_to_dict_basic(self, db, sample_participant):
        """Test converting participant to dictionary."""
        participant = Participant.query.get(sample_participant)
        data = participant.to_dict()
        
        assert data['id'] == participant.id
        assert data['name'] == participant.name
        assert data['workshop_id'] == participant.workshop_id
        assert 'created_at' in data
        assert 'extra_data' in data
    
    def test_to_dict_with_extra_data(self, db, sample_workshop):
        """Test to_dict with extra data."""
        extra = {'age': 30, 'contact': 'test@example.com'}
        participant = Participant(
            name='Test',
            workshop_id=sample_workshop,
            extra_data=extra
        )
        db.session.add(participant)
        db.session.commit()
        
        data = participant.to_dict()
        assert data['extra_data'] == extra
    
    def test_to_dict_without_extra_data(self, db, sample_participant):
        """Test to_dict when extra_data is None."""
        participant = Participant.query.get(sample_participant)
        participant.extra_data = None
        db.session.commit()
        
        data = participant.to_dict()
        assert data['extra_data'] == {}


class TestParticipantRelationships:
    """Tests for Participant relationships."""
    
    def test_participant_workshop_relationship(self, db, sample_participant, sample_workshop):
        """Test participant-workshop relationship."""
        participant = Participant.query.get(sample_participant)
        workshop = Workshop.query.get(sample_workshop)
        assert participant.workshop == workshop
    
    def test_participant_observations_relationship(self, db, sample_participant, sample_session):
        """Test participant-observations relationship."""
        participant = Participant.query.get(sample_participant)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        assert observation in participant.observations.all()
    
    def test_delete_participant_cascades_to_observations(self, db, sample_participant, sample_session):
        """Test that deleting participant deletes observations."""
        participant = Participant.query.get(sample_participant)
        observation = ObservationalRecord(
            session_id=sample_session,
            participant_id=sample_participant,
            answers={'test': 'yes'}
        )
        db.session.add(observation)
        db.session.commit()
        
        participant_id = participant.id
        observation_id = observation.id
        
        db.session.delete(participant)
        db.session.commit()
        
        assert Participant.query.get(participant_id) is None
        assert ObservationalRecord.query.get(observation_id) is None


class TestParticipantConstraints:
    """Tests for Participant constraints."""
    
    def test_participant_requires_name(self, db, sample_workshop):
        """Test that participant requires a name."""
        participant = Participant(workshop_id=sample_workshop)
        db.session.add(participant)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_participant_requires_workshop_id(self, db):
        """Test that participant requires a workshop_id."""
        participant = Participant(name='Test Participant')
        db.session.add(participant)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
    def test_participant_invalid_workshop_id(self, db):
        """Test that participant requires valid workshop_id."""
        participant = Participant(name='Test', workshop_id=99999)
        db.session.add(participant)
        
        with pytest.raises(Exception):  # IntegrityError (foreign key)
            db.session.commit()

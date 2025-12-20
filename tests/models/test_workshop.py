"""Tests for Workshop model."""
import pytest
from app.models.workshop import Workshop
from app.models.participant import Participant
from app.models.session import Session


class TestWorkshopModel:
    """Tests for Workshop model basic functionality."""
    
    def test_create_workshop(self, db, admin_user):
        """Test creating a new workshop."""
        workshop = Workshop(
            name='Test Workshop',
            objective='Test objective',
            user_id=admin_user.id
        )
        db.session.add(workshop)
        db.session.commit()
        
        assert workshop.id is not None
        assert workshop.name == 'Test Workshop'
        assert workshop.objective == 'Test objective'
        assert workshop.user_id == admin_user.id
        assert workshop.created_at is not None
    
    def test_workshop_repr(self, db, sample_workshop):
        """Test workshop string representation."""
        workshop = Workshop.query.get(sample_workshop)
        assert repr(workshop) == f'<Workshop {workshop.name}>'
    
    def test_workshop_without_objective(self, db, admin_user):
        """Test creating workshop without objective."""
        workshop = Workshop(name='Minimal Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        
        assert workshop.objective is None


class TestWorkshopProperties:
    """Tests for Workshop computed properties."""
    
    def test_participant_count_zero(self, db, admin_user):
        """Test participant count for workshop with no participants."""
        workshop = Workshop(name='Empty Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        
        assert workshop.participant_count == 0
    
    def test_participant_count_multiple(self, db, sample_workshop):
        """Test participant count with multiple participants."""
        workshop = Workshop.query.get(sample_workshop)
        # sample_workshop already has one participant from fixture
        initial_count = workshop.participant_count
        
        # Add more participants
        p2 = Participant(name='Participant 2', workshop_id=workshop.id)
        p3 = Participant(name='Participant 3', workshop_id=workshop.id)
        db.session.add_all([p2, p3])
        db.session.commit()
        
        assert workshop.participant_count == initial_count + 2
    
    def test_session_count_zero(self, db, admin_user):
        """Test session count for workshop with no sessions."""
        workshop = Workshop(name='Empty Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        
        assert workshop.session_count == 0
    
    def test_session_count_multiple(self, db, sample_workshop):
        """Test session count with multiple sessions."""
        workshop = Workshop.query.get(sample_workshop)
        # sample_workshop already has one session from fixture
        initial_count = workshop.session_count
        
        # Add more sessions
        s2 = Session(workshop_id=workshop.id, prompt='Session 2')
        s3 = Session(workshop_id=workshop.id, prompt='Session 3')
        db.session.add_all([s2, s3])
        db.session.commit()
        
        assert workshop.session_count == initial_count + 2


class TestWorkshopToDict:
    """Tests for Workshop to_dict method."""
    
    def test_to_dict_basic(self, db, sample_workshop):
        """Test converting workshop to dictionary without relations."""
        workshop = Workshop.query.get(sample_workshop)
        data = workshop.to_dict(include_relations=False)
        
        assert data['id'] == workshop.id
        assert data['name'] == workshop.name
        assert data['objective'] == workshop.objective
        assert data['user_id'] == workshop.user_id
        assert 'created_at' in data
        assert 'participant_count' in data
        assert 'session_count' in data
    
    def test_to_dict_without_relations(self, db, sample_workshop):
        """Test that relations are not included by default."""
        workshop = Workshop.query.get(sample_workshop)
        data = workshop.to_dict()
        
        assert 'participants' not in data
        assert 'sessions' not in data
    
    def test_to_dict_with_relations(self, db, sample_workshop, sample_participant, sample_session):
        """Test converting workshop to dictionary with relations."""
        workshop = Workshop.query.get(sample_workshop)
        data = workshop.to_dict(include_relations=True)
        
        assert 'participants' in data
        assert 'sessions' in data
        assert isinstance(data['participants'], list)
        assert isinstance(data['sessions'], list)
        assert len(data['participants']) > 0
        assert len(data['sessions']) > 0


class TestWorkshopRelationships:
    """Tests for Workshop relationships."""
    
    def test_workshop_owner_relationship(self, db, sample_workshop, admin_user):
        """Test workshop-owner relationship."""
        workshop = Workshop.query.get(sample_workshop)
        assert workshop.owner == admin_user
    
    def test_workshop_participants_relationship(self, db, sample_workshop, sample_participant):
        """Test workshop-participants relationship."""
        workshop = Workshop.query.get(sample_workshop)
        participant = Participant.query.get(sample_participant)
        assert participant in workshop.participants.all()
    
    def test_workshop_sessions_relationship(self, db, sample_workshop, sample_session):
        """Test workshop-sessions relationship."""
        workshop = Workshop.query.get(sample_workshop)
        session = Session.query.get(sample_session)
        assert session in workshop.sessions.all()
    
    def test_delete_workshop_cascades_to_participants(self, db, sample_workshop, sample_participant):
        """Test that deleting workshop deletes participants."""
        workshop = Workshop.query.get(sample_workshop)
        workshop_id = workshop.id
        participant_id = sample_participant
        
        db.session.delete(workshop)
        db.session.commit()
        
        assert Workshop.query.get(workshop_id) is None
        assert Participant.query.get(participant_id) is None
    
    def test_delete_workshop_cascades_to_sessions(self, db, sample_workshop, sample_session):
        """Test that deleting workshop deletes sessions."""
        workshop = Workshop.query.get(sample_workshop)
        workshop_id = workshop.id
        session_id = sample_session
        
        db.session.delete(workshop)
        db.session.commit()
        
        assert Workshop.query.get(workshop_id) is None
        assert Session.query.get(session_id) is None


class TestWorkshopConstraints:
    """Tests for Workshop constraints."""
    
    def test_workshop_requires_user_id(self, db):
        """Test that workshop requires a user_id."""
        workshop = Workshop(name='Test Workshop')
        db.session.add(workshop)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_workshop_requires_name(self, db, admin_user):
        """Test that workshop requires a name."""
        workshop = Workshop(user_id=admin_user.id)
        db.session.add(workshop)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()

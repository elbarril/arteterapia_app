"""
Pytest configuration and fixtures for API tests.
"""
import pytest
from app import create_app, db as _db_instance
from app.models.user import User
from app.models.role import Role
from app.models.workshop import Workshop
from app.models.participant import Participant
from app.models.session import Session


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('default')
    
    # Override config for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    return app


@pytest.fixture(scope='function', autouse=True)
def db(app):
    """Create database for each test function."""
    with app.app_context():
        _db_instance.create_all()
        
        # Create roles
        admin_role = Role(name='admin', description='Administrator')
        editor_role = Role(name='editor', description='Editor')
        _db_instance.session.add(admin_role)
        _db_instance.session.add(editor_role)
        _db_instance.session.commit()
        
        # Create test users
        admin_user = User(
            username='admin',
            email='admin@test.com',
            active=True,
            email_verified=True
        )
        admin_user.set_password('admin123')
        admin_user.roles.append(admin_role)
        
        editor_user = User(
            username='editor',
            email='editor@test.com',
            active=True,
            email_verified=True
        )
        editor_user.set_password('editor123')
        editor_user.roles.append(editor_role)
        
        _db_instance.session.add(admin_user)
        _db_instance.session.add(editor_user)
        _db_instance.session.commit()
        
        yield _db_instance
        
        # Clean up after each test
        _db_instance.session.remove()
        _db_instance.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_token(client):
    """Get JWT token for admin user."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    return response.json['access_token']


@pytest.fixture(scope='function')
def editor_token(client):
    """Get JWT token for editor user."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'editor',
        'password': 'editor123'
    })
    assert response.status_code == 200
    return response.json['access_token']


@pytest.fixture(scope='function')
def admin_headers(admin_token):
    """Get authorization headers for admin."""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture(scope='function')
def editor_headers(editor_token):
    """Get authorization headers for editor."""
    return {'Authorization': f'Bearer {editor_token}'}


@pytest.fixture(scope='function')
def sample_workshop(app, db):
    """Create a sample workshop for testing."""
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        workshop = Workshop(
            name='Test Workshop',
            objective='Testing objectives',
            user_id=admin_user.id
        )
        db.session.add(workshop)
        db.session.commit()
        
        workshop_id = workshop.id
        
        yield workshop_id


@pytest.fixture(scope='function')
def sample_participant(app, db, sample_workshop):
    """Create a sample participant for testing."""
    with app.app_context():
        participant = Participant(
            name='Test Participant',
            workshop_id=sample_workshop
        )
        db.session.add(participant)
        db.session.commit()
        
        participant_id = participant.id
        
        yield participant_id


@pytest.fixture(scope='function')
def sample_session(app, db, sample_workshop):
    """Create a sample session for testing."""
    with app.app_context():
        session = Session(
            workshop_id=sample_workshop,
            prompt='Test prompt',
            motivation='Test motivation',
            materials=['paint', 'canvas']
        )
        db.session.add(session)
        db.session.commit()
        
        session_id = session.id
        
        yield session_id

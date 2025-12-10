"""
Pytest configuration and fixtures for Arteterapia tests.
"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.workshop import Workshop
from app.models.participant import Participant
from app.models.session import Session
from app.models.observation import ObservationalRecord


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application instance."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory database for tests
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,  # Don't send emails during tests
    })
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create roles only if they don't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)
        
        editor_role = Role.query.filter_by(name='editor').first()
        if not editor_role:
            editor_role = Role(name='editor', description='Editor role')
            db.session.add(editor_role)
        
        db.session.commit()
        
        yield app
        
        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        # Clear all tables except roles before each test
        for table in reversed(db.metadata.sorted_tables):
            if table.name != 'roles' and table.name != 'user_roles':
                db.session.execute(table.delete())
        # Clear user_roles
        db.session.execute(db.metadata.tables['user_roles'].delete())
        # Clear users (but not roles)
        db.session.execute(db.metadata.tables['users'].delete())
        db.session.commit()
        
        yield db.session
        
        # Rollback any uncommitted changes
        db.session.rollback()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    admin_role = Role.query.filter_by(name='admin').first()
    user = User(
        username='testadmin',
        email='admin@test.com',
        email_verified=True
    )
    user.set_password('testpass123')
    user.roles.append(admin_role)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def editor_user(db_session):
    """Create an editor user for testing."""
    editor_role = Role.query.filter_by(name='editor').first()
    user = User(
        username='testeditor',
        email='editor@test.com',
        email_verified=True
    )
    user.set_password('testpass123')
    user.roles.append(editor_role)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def workshop(db_session, admin_user):
    """Create a test workshop."""
    workshop = Workshop(
        name='Test Workshop',
        objective='Test objective',
        user_id=admin_user.id
    )
    db.session.add(workshop)
    db.session.commit()
    return workshop


@pytest.fixture
def participant(db_session, workshop):
    """Create a test participant."""
    participant = Participant(name='Test Participant', workshop_id=workshop.id)
    db.session.add(participant)
    db.session.commit()
    return participant


@pytest.fixture
def session_obj(db_session, workshop):
    """Create a test session."""
    session = Session(
        workshop_id=workshop.id,
        prompt='Test prompt',
        motivation='Test motivation',
        materials=['paper', 'pencils']
    )
    db.session.add(session)
    db.session.commit()
    return session


@pytest.fixture
def authenticated_client(client, admin_user):
    """Create an authenticated client with admin user logged in."""
    with client:
        client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def editor_client(client, editor_user):
    """Create an authenticated client with editor user logged in."""
    with client:
        client.post('/auth/login', data={
            'username': 'testeditor',
            'password': 'testpass123'
        }, follow_redirects=True)
        yield client

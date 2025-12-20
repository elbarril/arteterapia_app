"""Tests for User model."""
import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.role import Role


class TestUserModel:
    """Tests for User model basic functionality."""
    
    def test_create_user(self, db):
        """Test creating a new user."""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.password_hash is not None
        assert user.active is True
        assert user.email_verified is False
        assert user.created_at is not None
    
    def test_user_repr(self, db):
        """Test user string representation."""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        assert repr(user) == '<User testuser>'
    
    def test_unique_username_constraint(self, db, admin_user):
        """Test that usernames must be unique."""
        user = User(
            username=admin_user.username,  # Duplicate username
            email='different@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_unique_email_constraint(self, db, admin_user):
        """Test that emails must be unique."""
        user = User(
            username='differentuser',
            email=admin_user.email  # Duplicate email
        )
        user.set_password('password')
        db.session.add(user)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()


class TestUserPassword:
    """Tests for User password functionality."""
    
    def test_set_password(self, db):
        """Test password hashing."""
        user = User(username='testuser', email='test@example.com')
        user.set_password('mypassword')
        
        assert user.password_hash is not None
        assert user.password_hash != 'mypassword'
        assert 'pbkdf2:sha256' in user.password_hash
    
    def test_check_password_correct(self, db, admin_user):
        """Test password verification with correct password."""
        assert admin_user.check_password('admin123') is True
    
    def test_check_password_incorrect(self, db, admin_user):
        """Test password verification with incorrect password."""
        assert admin_user.check_password('wrongpassword') is False
    
    def test_password_not_stored_plaintext(self, db):
        """Test that passwords are not stored in plaintext."""
        user = User(username='testuser', email='test@example.com')
        password = 'supersecret'
        user.set_password(password)
        
        assert user.password_hash != password
        assert password not in user.password_hash


class TestUserEmailVerification:
    """Tests for User email verification functionality."""
    
    def test_generate_verification_token(self, db, admin_user):
        """Test generating email verification token."""
        token = admin_user.generate_verification_token()
        
        assert token is not None
        assert len(token) > 20  # URL-safe tokens are reasonably long
        assert admin_user.verification_token == token
    
    def test_verification_token_is_unique(self, db, admin_user):
        """Test that verification tokens are unique."""
        token1 = admin_user.generate_verification_token()
        db.session.commit()
        
        # Create another user
        user2 = User(username='user2', email='user2@example.com')
        user2.set_password('password')
        db.session.add(user2)
        token2 = user2.generate_verification_token()
        db.session.commit()
        
        assert token1 != token2
    
    def test_verify_email(self, db, admin_user):
        """Test email verification."""
        admin_user.generate_verification_token()
        admin_user.verify_email()
        db.session.commit()
        
        assert admin_user.email_verified is True
        assert admin_user.verification_token is None


class TestUserPasswordReset:
    """Tests for User password reset functionality."""
    
    def test_generate_reset_token(self, db, admin_user):
        """Test generating password reset token."""
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        assert token is not None
        assert len(token) > 20
        assert admin_user.reset_token == token
        assert admin_user.reset_token_expiry is not None
    
    def test_reset_token_expiry_default(self, db, admin_user):
        """Test that reset token has default 24-hour expiry."""
        before = datetime.now(timezone.utc)
        admin_user.generate_reset_token()
        after = datetime.now(timezone.utc)
        
        # Make expiry timezone-aware if needed
        expiry = admin_user.reset_token_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        
        expected_min = before + timedelta(hours=24)
        expected_max = after + timedelta(hours=24)
        
        assert expected_min <= expiry <= expected_max
    
    def test_reset_token_custom_expiry(self, db, admin_user):
        """Test reset token with custom expiry hours."""
        before = datetime.now(timezone.utc)
        admin_user.generate_reset_token(expiry_hours=48)
        after = datetime.now(timezone.utc)
        
        # Make expiry timezone-aware if needed
        expiry = admin_user.reset_token_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        
        expected_min = before + timedelta(hours=48)
        expected_max = after + timedelta(hours=48)
        
        assert expected_min <= expiry <= expected_max
    
    def test_verify_reset_token_valid(self, db, admin_user):
        """Test verifying a valid reset token."""
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        assert admin_user.verify_reset_token(token) is True
    
    def test_verify_reset_token_invalid(self, db, admin_user):
        """Test verifying an invalid reset token."""
        admin_user.generate_reset_token()
        db.session.commit()
        
        assert admin_user.verify_reset_token('wrongtoken') is False
    
    def test_verify_reset_token_expired(self, db, admin_user):
        """Test verifying an expired reset token."""
        admin_user.generate_reset_token(expiry_hours=0)
        # Manually set expiry to past
        admin_user.reset_token_expiry = datetime.now(timezone.utc) - timedelta(hours=1)
        db.session.commit()
        
        assert admin_user.verify_reset_token(admin_user.reset_token) is False
    
    def test_verify_reset_token_no_token(self, db, admin_user):
        """Test verifying when no token exists."""
        admin_user.reset_token = None
        admin_user.reset_token_expiry = None
        db.session.commit()
        
        assert admin_user.verify_reset_token('anytoken') is False
    
    def test_clear_reset_token(self, db, admin_user):
        """Test clearing reset token."""
        admin_user.generate_reset_token()
        db.session.commit()
        
        admin_user.clear_reset_token()
        db.session.commit()
        
        assert admin_user.reset_token is None
        assert admin_user.reset_token_expiry is None


class TestUserRoles:
    """Tests for User role functionality."""
    
    def test_has_role_true(self, db, admin_user):
        """Test checking for a role the user has."""
        assert admin_user.has_role('admin') is True
    
    def test_has_role_false(self, db, admin_user):
        """Test checking for a role the user doesn't have."""
        assert admin_user.has_role('nonexistent') is False
    
    def test_is_admin_true(self, db, admin_user):
        """Test is_admin for admin user."""
        assert admin_user.is_admin() is True
    
    def test_is_admin_false(self, db, editor_user):
        """Test is_admin for non-admin user."""
        assert editor_user.is_admin() is False
    
    def test_add_role(self, db, editor_user):
        """Test adding a role to a user."""
        admin_role = Role.query.filter_by(name='admin').first()
        editor_user.roles.append(admin_role)
        db.session.commit()
        
        assert editor_user.has_role('admin') is True
        assert editor_user.has_role('editor') is True
    
    def test_multiple_roles(self, db):
        """Test user with multiple roles."""
        user = User(username='multiuser', email='multi@example.com')
        user.set_password('password')
        
        admin_role = Role.query.filter_by(name='admin').first()
        editor_role = Role.query.filter_by(name='editor').first()
        
        user.roles.append(admin_role)
        user.roles.append(editor_role)
        db.session.add(user)
        db.session.commit()
        
        assert user.has_role('admin') is True
        assert user.has_role('editor') is True


class TestUserActive:
    """Tests for User active status."""
    
    def test_is_active_default(self, db):
        """Test that users are active by default."""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        assert user.is_active is True
    
    def test_is_active_false(self, db):
        """Test inactive user."""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        user.active = False
        db.session.add(user)
        db.session.commit()
        
        assert user.is_active is False


class TestUserToDict:
    """Tests for User to_dict method."""
    
    def test_to_dict_basic(self, db, admin_user):
        """Test converting user to dictionary."""
        data = admin_user.to_dict()
        
        assert data['id'] == admin_user.id
        assert data['username'] == admin_user.username
        assert data['email'] == admin_user.email
        assert data['active'] == admin_user.active
        assert data['email_verified'] == admin_user.email_verified
        assert 'created_at' in data
        assert 'roles' in data
    
    def test_to_dict_roles(self, db, admin_user):
        """Test that roles are included in dictionary."""
        data = admin_user.to_dict()
        
        assert isinstance(data['roles'], list)
        assert 'admin' in data['roles']
    
    def test_to_dict_no_password(self, db, admin_user):
        """Test that password is not included in dictionary."""
        data = admin_user.to_dict()
        
        assert 'password' not in data
        assert 'password_hash' not in data
    
    def test_to_dict_no_tokens(self, db, admin_user):
        """Test that tokens are not included in dictionary."""
        admin_user.generate_verification_token()
        admin_user.generate_reset_token()
        db.session.commit()
        
        data = admin_user.to_dict()
        
        assert 'verification_token' not in data
        assert 'reset_token' not in data
        assert 'reset_token_expiry' not in data


class TestUserRelationships:
    """Tests for User relationships."""
    
    def test_user_workshops_relationship(self, db, admin_user, sample_workshop):
        """Test user-workshop relationship."""
        from app.models.workshop import Workshop
        workshop = Workshop.query.get(sample_workshop)
        assert workshop in admin_user.workshops.all()
    
    def test_user_workshops_cascade_delete(self, db):
        """Test that deleting user deletes workshops."""
        from app.models.workshop import Workshop
        
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        workshop = Workshop(name='Test Workshop', user_id=user.id)
        db.session.add(workshop)
        db.session.commit()
        
        workshop_id = workshop.id
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        # Workshop should be deleted
        assert Workshop.query.get(workshop_id) is None

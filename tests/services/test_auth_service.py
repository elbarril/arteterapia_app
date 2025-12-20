"""
Tests for AuthService.

Tests authentication, registration, password management, and invitations.
"""
import pytest
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.user_invitation import UserInvitation


class TestAuthServicePasswordValidation:
    """Tests for password validation."""
    
    def test_password_too_short(self):
        """Should reject password too short."""
        is_valid, error = AuthService.validate_password_strength('short')
        assert is_valid is False
        assert 'al menos' in error.lower()
    
    def test_password_valid(self):
        """Should accept valid password."""
        is_valid, error = AuthService.validate_password_strength('ValidPass123')
        assert is_valid is True
        assert error is None


class TestAuthServiceUsernameValidation:
    """Tests for username validation."""
    
    def test_username_too_short(self):
        """Should reject username too short."""
        is_valid, error = AuthService.validate_username('ab')
        assert is_valid is False
        assert 'al menos' in error.lower()
    
    def test_username_invalid_characters(self):
        """Should reject username with invalid characters."""
        is_valid, error = AuthService.validate_username('user@name!')
        assert is_valid is False
        assert 'letras' in error.lower() or 'alfanum' in error.lower()
    
    def test_username_already_taken(self, app, db):
        """Should reject already taken username."""
        with app.app_context():
            is_valid, error = AuthService.validate_username('admin')
            assert is_valid is False
            assert 'uso' in error.lower()
    
    def test_username_valid(self, app, db):
        """Should accept valid username."""
        with app.app_context():
            is_valid, error = AuthService.validate_username('newuser123')
            assert is_valid is True
            assert error is None


class TestAuthServiceAuthentication:
    """Tests for user authentication."""
    
    def test_authenticate_with_username(self, app, db):
        """Should authenticate with valid username and password."""
        with app.app_context():
            user, error = AuthService.authenticate_user('admin', 'admin123')
            
            assert user is not None
            assert error is None
            assert user.username == 'admin'
    
    def test_authenticate_with_email(self, app, db):
        """Should authenticate with valid email and password."""
        with app.app_context():
            user, error = AuthService.authenticate_user('admin@test.com', 'admin123')
            
            assert user is not None
            assert error is None
            assert user.email == 'admin@test.com'
    
    def test_authenticate_invalid_password(self, app, db):
        """Should reject invalid password."""
        with app.app_context():
            user, error = AuthService.authenticate_user('admin', 'wrongpassword')
            
            assert user is None
            assert error is not None
            assert 'contraseña' in error.lower() or 'credencial' in error.lower()
    
    def test_authenticate_nonexistent_user(self, app, db):
        """Should reject non-existent user."""
        with app.app_context():
            user, error = AuthService.authenticate_user('nonexistent', 'password')
            
            assert user is None
            assert error is not None


class TestAuthServiceRegistration:
    """Tests for user registration."""
    
    def test_register_user_success(self, app, db):
        """Should register user successfully."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            # Create invitation
            invitation, _ = AuthService.create_invitation(
                email='newuser@test.com',
                admin_user_id=admin.id
            )
            
            # Register with invitation
            user, error = AuthService.register_user(
                invitation_token=invitation.token,
                username='newuser',
                password='ValidPass123',
                password_confirm='ValidPass123'
            )
            
            assert user is not None
            assert error is None
            assert user.username == 'newuser'
            assert user.email == 'newuser@test.com'
    
    def test_register_user_invalid_token(self, app, db):
        """Should reject invalid invitation token."""
        with app.app_context():
            user, error = AuthService.register_user(
                invitation_token='invalid-token',
                username='newuser',
                password='ValidPass123',
                password_confirm='ValidPass123'
            )
            
            assert user is None
            assert error is not None
    
    def test_register_user_password_mismatch(self, app, db):
        """Should reject mismatched passwords."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            invitation, _ = AuthService.create_invitation(
                email='newuser@test.com',
                admin_user_id=admin.id
            )
            
            user, error = AuthService.register_user(
                invitation_token=invitation.token,
                username='newuser',
                password='ValidPass123',
                password_confirm='DifferentPass123'
            )
            
            assert user is None
            assert error is not None
            assert 'coincid' in error.lower()
    
    def test_register_user_weak_password(self, app, db):
        """Should reject weak password."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            invitation, _ = AuthService.create_invitation(
                email='newuser@test.com',
                admin_user_id=admin.id
            )
            
            user, error = AuthService.register_user(
                invitation_token=invitation.token,
                username='newuser',
                password='weak',
                password_confirm='weak'
            )
            
            assert user is None
            assert error is not None


class TestAuthServicePasswordReset:
    """Tests for password reset flow."""
    
    def test_request_password_reset_existing_email(self, app, db):
        """Should process password reset for existing email."""
        with app.app_context():
            user, should_send = AuthService.request_password_reset('admin@test.com')
            
            assert user is not None
            assert should_send is True
    
    def test_request_password_reset_nonexistent_email(self, app, db):
        """Should handle non-existent email safely."""
        with app.app_context():
            user, should_send = AuthService.request_password_reset('nonexistent@test.com')
            
            # Should return None, False to prevent email enumeration
            assert user is None
            assert should_send is False
    
    def test_reset_password_success(self, app, db):
        """Should reset password successfully."""
        with app.app_context():
            # Request reset
            user_obj = User.query.filter_by(username='admin').first()
            token = user_obj.generate_reset_token()  # Fixed method name
            
            # Reset password
            user, error = AuthService.reset_password(
                reset_token=token,
                new_password='NewPassword123',
                new_password_confirm='NewPassword123'
            )
            
            assert user is not None
            assert error is None
            
            # Verify new password works
            assert user.check_password('NewPassword123')
    
    def test_reset_password_mismatch(self, app, db):
        """Should reject mismatched passwords."""
        with app.app_context():
            user_obj = User.query.filter_by(username='admin').first()
            token = user_obj.generate_reset_token()  # Fixed method name
            
            user, error = AuthService.reset_password(
                reset_token=token,
                new_password='NewPassword123',
                new_password_confirm='DifferentPassword123'
            )
            
            assert user is None
            assert error is not None
            assert 'coincid' in error.lower()


class TestAuthServiceChangePassword:
    """Tests for changing password."""
    
    def test_change_password_success(self, app, db):
        """Should change password successfully."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            success, error = AuthService.change_password(
                user_id=admin.id,
                current_password='admin123',
                new_password='NewPassword123',
                new_password_confirm='NewPassword123'
            )
            
            assert success is True
            assert error is None
            
            # Verify new password works
            user = User.query.get(admin.id)
            assert user.check_password('NewPassword123')
    
    def test_change_password_incorrect_current(self, app, db):
        """Should reject incorrect current password."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            success, error = AuthService.change_password(
                user_id=admin.id,
                current_password='wrongpassword',
                new_password='NewPassword123',
                new_password_confirm='NewPassword123'
            )
            
            assert success is False
            assert error is not None
            assert 'actual' in error.lower()


class TestAuthServiceInvitations:
    """Tests for invitation management."""
    
    def test_create_invitation_success(self, app, db):
        """Should create invitation successfully."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            invitation, error = AuthService.create_invitation(
                email='invited@test.com',
                admin_user_id=admin.id
            )
            
            assert invitation is not None
            assert error is None
            assert invitation.email == 'invited@test.com'
            assert invitation.token is not None
    
    def test_create_invitation_duplicate_email(self, app, db):
        """Should reject duplicate email invitation."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            # Create first invitation
            AuthService.create_invitation(
                email='invited@test.com',
                admin_user_id=admin.id
            )
            
            # Try to create duplicate
            invitation, error = AuthService.create_invitation(
                email='invited@test.com',
                admin_user_id=admin.id
            )
            
            assert invitation is None
            assert error is not None
    
    def test_get_invitation_by_token(self, app, db):
        """Should retrieve invitation by token."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            # Create invitation
            created, _ = AuthService.create_invitation(
                email='test@test.com',
                admin_user_id=admin.id
            )
            
            # Retrieve by token
            retrieved = AuthService.get_invitation_by_token(created.token)
            
            assert retrieved is not None
            assert retrieved.id == created.id
    
    def test_get_invitation_by_invalid_token(self, app, db):
        """Should return None for invalid token."""
        with app.app_context():
            invitation = AuthService.get_invitation_by_token('invalid-token')
            assert invitation is None

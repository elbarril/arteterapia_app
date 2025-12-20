"""
Tests for authentication routes.

Tests all auth routes including login, logout, registration,
email verification, password reset, and password change.
"""
import pytest
from flask import url_for
from app.models.user import User
from app.models.user_invitation import UserInvitation
from app.services.auth_service import AuthService


class TestAuthLogin:
    """Tests for login route."""
    
    def test_login_page_get(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_success(self, client, app, db):
        """Test successful login."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123',
            'remember': 'on'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/workshop' in response.location or response.location == '/'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 200
    
    def test_login_redirect_when_authenticated(self, client, admin_user):
        """Test that authenticated users are redirected from login page."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Try to access login page again
        response = client.get('/login', follow_redirects=False)
        assert response.status_code == 302
    
    def test_login_with_next_parameter(self, client):
        """Test login with next parameter for redirect."""
        response = client.post('/login?next=/workshop/1', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        
        assert response.status_code == 302


class TestAuthLogout:
    """Tests for logout route."""
    
    def test_logout_requires_login(self, client):
        """Test that logout requires authentication."""
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_logout_success(self, client):
        """Test successful logout."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Logout
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location


class TestAuthRegister:
    """Tests for registration route."""
    
    def test_register_invalid_token(self, client):
        """Test registration with invalid token."""
        response = client.get('/register/invalid-token', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_register_page_with_valid_token(self, client, app, db, admin_user):
        """Test GET request to register page with valid token."""
        # Create a valid invitation
        invitation = UserInvitation(email='newuser@test.com', created_by_user_id=admin_user.id)
        db.session.add(invitation)
        db.session.commit()
        
        token = invitation.token
        
        response = client.get(f'/register/{token}')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'registro' in response.data.lower()
    
    def test_register_success(self, client, app, db, admin_user):
        """Test successful registration."""
        # Create a valid invitation
        invitation = UserInvitation(email='newuser@test.com', created_by_user_id=admin_user.id)
        db.session.add(invitation)
        db.session.commit()
        
        token = invitation.token
        
        response = client.post(f'/register/{token}', data={
            'username': 'newuser',
            'password': 'password123',
            'password_confirm': 'password123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Verify user was created
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@test.com'
    
    def test_register_password_mismatch(self, client, app, db, admin_user):
        """Test registration with mismatched passwords."""
        # Create a valid invitation
        invitation = UserInvitation(email='newuser@test.com', created_by_user_id=admin_user.id)
        db.session.add(invitation)
        db.session.commit()
        
        token = invitation.token
        
        response = client.post(f'/register/{token}', data={
            'username': 'newuser',
            'password': 'password123',
            'password_confirm': 'different123'
        })
        
        assert response.status_code == 200
    
    def test_register_duplicate_username(self, client, app, db, admin_user):
        """Test registration with existing username."""
        # Create a valid invitation
        invitation = UserInvitation(email='newuser@test.com', created_by_user_id=admin_user.id)
        db.session.add(invitation)
        db.session.commit()
        
        token = invitation.token
        
        response = client.post(f'/register/{token}', data={
            'username': 'admin',  # Already exists
            'password': 'password123',
            'password_confirm': 'password123'
        })
        
        assert response.status_code == 200


class TestAuthVerifyEmail:
    """Tests for email verification route."""
    
    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.get('/verify-email/invalid-token', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_verify_email_success(self, client, app, db):
        """Test successful email verification."""
        # Create unverified user
        user = User(
            username='unverified',
            email='unverified@test.com',
            active=True,
            email_verified=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Generate verification token
        token = user.generate_verification_token()
        
        response = client.get(f'/verify-email/{token}', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Verify user is now verified
        db.session.refresh(user)
        assert user.email_verified is True


class TestAuthForgotPassword:
    """Tests for forgot password route."""
    
    def test_forgot_password_page_get(self, client):
        """Test GET request to forgot password page."""
        response = client.get('/forgot-password')
        assert response.status_code == 200
    
    def test_forgot_password_redirect_when_authenticated(self, client):
        """Test that authenticated users are redirected."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/forgot-password', follow_redirects=False)
        assert response.status_code == 302
    
    def test_forgot_password_submit(self, client, app, db):
        """Test forgot password submission."""
        response = client.post('/forgot-password', data={
            'email': 'admin@test.com'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_forgot_password_nonexistent_email(self, client):
        """Test forgot password with non-existent email."""
        response = client.post('/forgot-password', data={
            'email': 'nonexistent@test.com'
        }, follow_redirects=False)
        
        # Should still redirect to prevent email enumeration
        assert response.status_code == 302


class TestAuthResetPassword:
    """Tests for reset password route."""
    
    def test_reset_password_invalid_token(self, client):
        """Test reset password with invalid token."""
        response = client.get('/reset-password/invalid-token', follow_redirects=False)
        assert response.status_code == 302
    
    def test_reset_password_page_with_valid_token(self, client, app, db, admin_user):
        """Test GET request to reset password page with valid token."""
        # Generate reset token
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        response = client.get(f'/reset-password/{token}')
        assert response.status_code == 200
    
    def test_reset_password_success(self, client, app, db, admin_user):
        """Test successful password reset."""
        # Generate reset token
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        response = client.post(f'/reset-password/{token}', data={
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Verify password was changed
        db.session.refresh(admin_user)
        assert admin_user.check_password('newpassword123')
    
    def test_reset_password_mismatch(self, client, app, db, admin_user):
        """Test reset password with mismatched passwords."""
        # Generate reset token
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        response = client.post(f'/reset-password/{token}', data={
            'password': 'newpassword123',
            'password_confirm': 'different123'
        })
        
        assert response.status_code == 200
    
    def test_reset_password_redirect_when_authenticated(self, client, db, admin_user):
        """Test that authenticated users are redirected."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Generate reset token
        token = admin_user.generate_reset_token()
        db.session.commit()
        
        response = client.get(f'/reset-password/{token}', follow_redirects=False)
        assert response.status_code == 302


class TestAuthChangePassword:
    """Tests for change password route."""
    
    def test_change_password_requires_login(self, client):
        """Test that change password requires authentication."""
        response = client.get('/change-password', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_change_password_page_get(self, client):
        """Test GET request to change password page."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/change-password')
        assert response.status_code == 200
    
    def test_change_password_success(self, client, app, db, admin_user):
        """Test successful password change."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify password was changed
        db.session.refresh(admin_user)
        assert admin_user.check_password('newpassword123')
    
    def test_change_password_wrong_current(self, client):
        """Test change password with wrong current password."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        })
        
        assert response.status_code == 200
    
    def test_change_password_mismatch(self, client):
        """Test change password with mismatched new passwords."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'different123'
        })
        
        assert response.status_code == 200


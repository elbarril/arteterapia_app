"""Authentication service layer for business logic.

This service handles all authentication-related operations including
login, registration, password management, and email verification.
"""
import re
from app import db
from app.models.user import User
from app.models.user_invitation import UserInvitation
from app.models.role import Role


class AuthService:
    """Authentication business logic layer."""
    
    # Password validation constants
    MIN_PASSWORD_LENGTH = 8
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password meets minimum security requirements.
        
        Args:
            password: Password string to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if len(password) < AuthService.MIN_PASSWORD_LENGTH:
            return False, f'La contraseña debe tener al menos {AuthService.MIN_PASSWORD_LENGTH} caracteres'
        
        if not re.search(r'[A-Za-z]', password):
            return False, 'La contraseña debe contener al menos una letra'
        
        if not re.search(r'\d', password):
            return False, 'La contraseña debe contener al menos un número'
        
        return True, None
    
    @staticmethod
    def authenticate_user(username_or_email, password):
        """
        Authenticate user with username/email and password.
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
            
        Returns:
            Tuple of (user: User or None, error_message: str or None)
        """
        if not username_or_email or not password:
            return None, 'Por favor completa todos los campos'
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return None, 'Usuario o contraseña incorrectos'
        
        if not user.active:
            return None, 'Tu cuenta ha sido desactivada'
        
        if not user.email_verified:
            return None, 'Por favor verifica tu correo electrónico antes de iniciar sesión'
        
        return user, None
    
    @staticmethod
    def register_user(invitation_token, username, password, password_confirm):
        """
        Register a new user via invitation token.
        
        Args:
            invitation_token: Invitation token string
            username: Desired username
            password: Plain text password
            password_confirm: Password confirmation
            
        Returns:
            Tuple of (user: User or None, error_message: str or None)
        """
        # Validate invitation
        invitation = UserInvitation.query.filter_by(token=invitation_token).first()
        
        if not invitation:
            return None, 'Invitación no válida'
        
        if not invitation.is_valid():
            return None, 'Esta invitación ha expirado o ya fue utilizada'
        
        # Validate input
        if not username or not password:
            return None, 'Por favor completa todos los campos'
        
        if password != password_confirm:
            return None, 'Las contraseñas no coinciden'
        
        # Validate password strength
        valid, error_msg = AuthService.validate_password_strength(password)
        if not valid:
            return None, error_msg
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, 'Este nombre de usuario ya está en uso'
        
        # Check if email already exists
        if User.query.filter_by(email=invitation.email).first():
            return None, 'Este correo electrónico ya está registrado'
        
        # Create new user
        user = User(
            username=username,
            email=invitation.email,
            active=True,
            email_verified=False
        )
        user.set_password(password)
        user.generate_verification_token()
        
        # Assign default role (Editor)
        editor_role = Role.query.filter_by(name='editor').first()
        if editor_role:
            user.roles.append(editor_role)
        
        db.session.add(user)
        
        # Mark invitation as used
        invitation.mark_as_used()
        
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def verify_email(verification_token):
        """
        Verify user email address with token.
        
        Args:
            verification_token: Email verification token
            
        Returns:
            Tuple of (user: User or None, error_message: str or None)
        """
        user = User.query.filter_by(verification_token=verification_token).first()
        
        if not user:
            return None, 'Token de verificación no válido'
        
        user.verify_email()
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def request_password_reset(email):
        """
        Request password reset for user email.
        
        Args:
            email: User email address
            
        Returns:
            Tuple of (user: User or None, should_send_email: bool)
            Note: Returns (None, False) for non-existent emails to prevent enumeration
        """
        if not email:
            return None, False
        
        user = User.query.filter_by(email=email).first()
        
        # Only generate token for active users
        if user and user.active:
            user.generate_reset_token()
            db.session.commit()
            return user, True
        
        # Return None but don't reveal if email exists (prevent enumeration)
        return None, False
    
    @staticmethod
    def verify_reset_token(reset_token):
        """
        Verify password reset token is valid.
        
        Args:
            reset_token: Password reset token
            
        Returns:
            Tuple of (user: User or None, error_message: str or None)
        """
        user = User.query.filter_by(reset_token=reset_token).first()
        
        if not user or not user.verify_reset_token(reset_token):
            return None, 'Token de restablecimiento no válido o expirado'
        
        return user, None
    
    @staticmethod
    def reset_password(reset_token, new_password, new_password_confirm):
        """
        Reset user password with reset token.
        
        Args:
            reset_token: Password reset token
            new_password: New password
            new_password_confirm: Password confirmation
            
        Returns:
            Tuple of (user: User or None, error_message: str or None)
        """
        # Verify token
        user, error = AuthService.verify_reset_token(reset_token)
        if error:
            return None, error
        
        # Validate input
        if not new_password:
            return None, 'Por favor ingresa una contraseña'
        
        if new_password != new_password_confirm:
            return None, 'Las contraseñas no coinciden'
        
        # Validate password strength
        valid, error_msg = AuthService.validate_password_strength(new_password)
        if not valid:
            return None, error_msg
        
        # Update password
        user.set_password(new_password)
        user.clear_reset_token()
        user.must_change_password = False
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def change_password(user_id, current_password, new_password, new_password_confirm):
        """
        Change password for authenticated user.
        
        Args:
            user_id: ID of the user
            current_password: Current password for verification
            new_password: New password
            new_password_confirm: Password confirmation
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        user = User.query.get(user_id)
        
        if not user:
            return False, 'Usuario no encontrado'
        
        # Verify current password
        if not user.check_password(current_password):
            return False, 'Contraseña actual incorrecta'
        
        # Validate new password
        if not new_password:
            return False, 'Por favor ingresa una nueva contraseña'
        
        if new_password != new_password_confirm:
            return False, 'Las contraseñas nuevas no coinciden'
        
        # Validate password strength
        valid, error_msg = AuthService.validate_password_strength(new_password)
        if not valid:
            return False, error_msg
        
        # Update password
        user.set_password(new_password)
        user.must_change_password = False
        db.session.commit()
        
        return True, None
    
    @staticmethod
    def create_invitation(email, admin_user_id, expiry_days=7):
        """
        Create user invitation (admin only).
        
        Args:
            email: Email address to invite
            admin_user_id: ID of admin creating the invitation
            expiry_days: Days until invitation expires (default: 7)
            
        Returns:
            Tuple of (invitation: UserInvitation or None, error_message: str or None)
        """
        # Verify admin user
        admin = User.query.get(admin_user_id)
        if not admin or not admin.is_admin():
            return None, 'No tienes permiso para crear invitaciones'
        
        # Validate email
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return None, 'Correo electrónico no válido'
        
        # Check if email already registered
        if User.query.filter_by(email=email).first():
            return None, 'Este correo electrónico ya está registrado'
        
        # Check for existing pending invitation
        existing = UserInvitation.query.filter_by(email=email).filter(
            UserInvitation.used_at.is_(None)
        ).first()
        
        if existing and existing.is_valid():
            return None, 'Ya existe una invitación pendiente para este correo'
        
        # Create invitation
        invitation = UserInvitation(
            email=email,
            created_by_user_id=admin_user_id,
            expiry_days=expiry_days
        )
        
        db.session.add(invitation)
        db.session.commit()
        
        return invitation, None
    
    @staticmethod
    def get_invitation_by_token(token):
        """
        Get invitation by token.
        
        Args:
            token: Invitation token
            
        Returns:
            UserInvitation or None
        """
        return UserInvitation.query.filter_by(token=token).first()
    
    @staticmethod
    def validate_username(username):
        """
        Validate username format and availability.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if not username:
            return False, 'El nombre de usuario es obligatorio'
        
        if len(username) < 3:
            return False, 'El nombre de usuario debe tener al menos 3 caracteres'
        
        if len(username) > 80:
            return False, 'El nombre de usuario no puede exceder 80 caracteres'
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, 'El nombre de usuario solo puede contener letras, números, guiones y guiones bajos'
        
        if User.query.filter_by(username=username).first():
            return False, 'Este nombre de usuario ya está en uso'
        
        return True, None

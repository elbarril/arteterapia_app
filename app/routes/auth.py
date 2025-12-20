"""Authentication controller."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.services.auth_service import AuthService
from app.utils.email_utils import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        # Use service to authenticate
        user, error = AuthService.authenticate_user(username_or_email, password)
        
        if error:
            flash(error, 'danger')
            return render_template('auth/login.html')
        
        # Login successful
        login_user(user, remember=remember)
        
        # Check if password must be changed
        if user.must_change_password:
            flash('Debes cambiar tu contraseña antes de continuar', 'warning')
            return redirect(url_for('auth_bp.change_password', force=True))
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('workshop_bp.list_workshops'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    """User registration via invitation token."""
    # Get invitation using service
    invitation = AuthService.get_invitation_by_token(token)
    
    if not invitation:
        flash('Invitación no válida', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if not invitation.is_valid():
        flash('Esta invitación ha expirado o ya fue utilizada', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Use service to register user
        user, error = AuthService.register_user(token, username, password, password_confirm)
        
        if error:
            flash(error, 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        # Send verification email
        send_verification_email(user)
        
        # Log out current user if any (e.g., admin who created the invitation)
        if current_user.is_authenticated:
            logout_user()
        
        flash('Cuenta creada exitosamente. Por favor verifica tu correo electrónico.', 'success')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/register.html', invitation=invitation)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email address."""
    # Use service to verify email
    user, error = AuthService.verify_email(token)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth_bp.login'))
    
    flash('¡Correo electrónico verificado exitosamente! Ya puedes iniciar sesión.', 'success')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        # Use service to request password reset
        user, should_send = AuthService.request_password_reset(email)
        
        # Send email if user exists and is active
        if should_send and user:
            send_password_reset_email(user)
        
        # Always show success message to prevent email enumeration
        flash('Si el correo existe, recibirás instrucciones para restablecer tu contraseña', 'info')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    # Verify token first
    user, error = AuthService.verify_reset_token(token)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth_bp.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Use service to reset password
        user, error = AuthService.reset_password(token, password, password_confirm)
        
        if error:
            flash(error, 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        flash('Contraseña restablecida exitosamente', 'success')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user."""
    force = request.args.get('force', False)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        new_password_confirm = request.form.get('new_password_confirm', '')
        
        # Use service to change password
        success, error = AuthService.change_password(
            current_user.id,
            current_password,
            new_password,
            new_password_confirm
        )
        
        if not success:
            flash(error, 'danger')
            return render_template('auth/change_password.html', force=force)
        
        flash('Contraseña cambiada exitosamente', 'success')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    return render_template('auth/change_password.html', force=force)

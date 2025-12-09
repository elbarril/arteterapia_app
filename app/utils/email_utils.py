"""Email utility functions for sending authentication emails."""
from flask import url_for, current_app
from flask_mail import Mail, Message


mail = Mail()


def send_verification_email(user):
    """Send email verification link to user."""
    verification_url = url_for('auth_bp.verify_email', 
                               token=user.verification_token, 
                               _external=True)
    
    subject = 'Verificar tu correo electrónico - Arteterapia'
    body = f"""Hola {user.username},

Por favor verifica tu correo electrónico haciendo clic en el siguiente enlace:

{verification_url}

Este enlace es válido hasta que completes la verificación.

Si no creaste esta cuenta, puedes ignorar este correo.

Saludos,
El equipo de Arteterapia
"""
    
    # In development, log to console instead of sending
    if current_app.config.get('MAIL_SUPPRESS_SEND', True):
        print("\n" + "="*80)
        print("EMAIL: Verification Email")
        print("="*80)
        print(f"To: {user.email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
    else:
        msg = Message(subject,
                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[user.email])
        msg.body = body
        mail.send(msg)


def send_password_reset_email(user):
    """Send password reset link to user."""
    reset_url = url_for('auth_bp.reset_password', 
                       token=user.reset_token, 
                       _external=True)
    
    subject = 'Restablecer tu contraseña - Arteterapia'
    body = f"""Hola {user.username},

Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace:

{reset_url}

Este enlace expirará en 24 horas.

Si no solicitaste restablecer tu contraseña, puedes ignorar este correo de forma segura.

Saludos,
El equipo de Arteterapia
"""
    
    # In development, log to console instead of sending
    if current_app.config.get('MAIL_SUPPRESS_SEND', True):
        print("\n" + "="*80)
        print("EMAIL: Password Reset")
        print("="*80)
        print(f"To: {user.email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
    else:
        msg = Message(subject,
                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[user.email])
        msg.body = body
        mail.send(msg)


def send_invitation_email(invitation):
    """Send invitation link to new user."""
    register_url = url_for('auth_bp.register', 
                          token=invitation.token, 
                          _external=True)
    
    subject = 'Invitación a Arteterapia'
    body = f"""Hola,

Has sido invitado a unirte a Arteterapia, la plataforma de gestión de talleres terapéuticos.

Para crear tu cuenta, haz clic en el siguiente enlace:

{register_url}

Esta invitación expirará el {invitation.expires_at.strftime('%d/%m/%Y a las %H:%M')}.

Saludos,
El equipo de Arteterapia
"""
    
    # In development, log to console instead of sending
    if current_app.config.get('MAIL_SUPPRESS_SEND', True):
        print("\n" + "="*80)
        print("EMAIL: User Invitation")
        print("="*80)
        print(f"To: {invitation.email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
    else:
        msg = Message(subject,
                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[invitation.email])
        msg.body = body
        mail.send(msg)

"""
Flask CLI Commands
==================
Custom CLI commands for common administrative and development tasks.

Usage:
    flask --app run <command> [options]

Available commands:
    - db: Database management commands
    - users: User management commands
    - data: Sample data management commands
    - admin: Admin utilities
"""
import click
from flask import current_app
from datetime import datetime, timedelta
import secrets
import os
import shutil

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.workshop import Workshop
from app.models.participant import Participant
from app.models.session import Session
from app.models.observation import ObservationalRecord
from app.models.user_invitation import UserInvitation


def register_cli_commands(app):
    """Register all CLI commands with the Flask app."""
    
    # ============================================================================
    # DATABASE COMMANDS
    # ============================================================================
    
    @app.cli.group()
    def database():
        """Database management commands."""
        pass
    
    @database.command('reset')
    @click.option('--yes', is_flag=True, help='Skip confirmation prompt')
    def reset_database(yes):
        """Reset database (WARNING: deletes all data)."""
        if not yes:
            click.confirm(
                '⚠️  WARNING: This will delete ALL data. Continue?',
                abort=True
            )
        
        db_path = 'arteterapia.db'
        migrations_dir = 'migrations'
        
        # Remove database file
        if os.path.exists(db_path):
            os.remove(db_path)
            click.echo(f'✓ Removed database: {db_path}')
        
        # Remove migrations directory
        if os.path.exists(migrations_dir):
            shutil.rmtree(migrations_dir)
            click.echo(f'✓ Removed migrations directory')
        
        click.echo('✓ Database reset complete')
        click.echo('  Run: flask --app run database init')
    
    @database.command('init')
    @click.option('--with-data', is_flag=True, help='Populate with sample data')
    def init_database(with_data):
        """Initialize database with tables and admin user."""
        from flask_migrate import init as migrate_init
        
        # Check if migrations directory exists
        if not os.path.exists('migrations'):
            click.echo('Creating migrations directory...')
            migrate_init()
            click.echo('✓ Migrations directory created')
        
        # Create all tables
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('✓ Database tables created')
        
        # Create roles
        click.echo('Creating roles...')
        _create_roles()
        click.echo('✓ Roles created')
        
        # Create admin user
        click.echo('Creating admin user...')
        admin = _create_admin_user()
        click.echo('✓ Admin user created')
        click.echo(f'  Username: admin')
        click.echo(f'  Password: admin123')
        click.echo(f'  ⚠️  CHANGE PASSWORD ON FIRST LOGIN!')
        
        # Create sample data if requested
        if with_data:
            click.echo('Creating sample data...')
            _create_sample_data(admin)
            click.echo('✓ Sample data created')
        
        click.echo('\n✓ Database initialization complete!')
    
    @database.command('stats')
    def database_stats():
        """Show database statistics."""
        stats = {
            'Users': User.query.count(),
            'Roles': Role.query.count(),
            'Workshops': Workshop.query.count(),
            'Participants': Participant.query.count(),
            'Sessions': Session.query.count(),
            'Observations': ObservationalRecord.query.count(),
            'Invitations': UserInvitation.query.count(),
        }
        
        click.echo('\n' + '='*50)
        click.echo('DATABASE STATISTICS')
        click.echo('='*50)
        for key, value in stats.items():
            click.echo(f'  {key:20} {value:>5}')
        click.echo('='*50 + '\n')
    
    # ============================================================================
    # USER MANAGEMENT COMMANDS
    # ============================================================================
    
    @app.cli.group()
    def users():
        """User management commands."""
        pass
    
    @users.command('list')
    @click.option('--role', help='Filter by role (admin/editor)')
    def list_users(role):
        """List all users."""
        query = User.query
        
        if role:
            role_obj = Role.query.filter_by(name=role).first()
            if not role_obj:
                click.echo(f'❌ Role "{role}" not found')
                return
            query = query.filter(User.roles.contains(role_obj))
        
        users_list = query.all()
        
        if not users_list:
            click.echo('No users found.')
            return
        
        click.echo('\n' + '='*80)
        click.echo(f'{"ID":<5} {"Username":<20} {"Email":<30} {"Roles":<15} {"Active"}')
        click.echo('='*80)
        
        for user in users_list:
            roles_str = ', '.join([r.name for r in user.roles])
            active_str = '✓' if user.active else '✗'
            click.echo(
                f'{user.id:<5} {user.username:<20} {user.email:<30} '
                f'{roles_str:<15} {active_str}'
            )
        
        click.echo('='*80 + '\n')
    
    @users.command('create')
    @click.option('--username', prompt=True, help='Username')
    @click.option('--email', prompt=True, help='Email address')
    @click.option('--password', prompt=True, hide_input=True, 
                  confirmation_prompt=True, help='Password')
    @click.option('--role', type=click.Choice(['admin', 'editor']), 
                  default='editor', help='User role')
    @click.option('--active/--inactive', default=True, help='User active status')
    def create_user(username, email, password, role, active):
        """Create a new user."""
        # Check if user exists
        if User.query.filter_by(username=username).first():
            click.echo(f'❌ User "{username}" already exists')
            return
        
        if User.query.filter_by(email=email).first():
            click.echo(f'❌ Email "{email}" already in use')
            return
        
        # Get role
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            click.echo(f'❌ Role "{role}" not found')
            return
        
        # Create user
        user = User(
            username=username,
            email=email,
            active=active,
            email_verified=True  # CLI-created users are pre-verified
        )
        user.set_password(password)
        user.roles.append(role_obj)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'✓ User "{username}" created successfully')
        click.echo(f'  Email: {email}')
        click.echo(f'  Role: {role}')
        click.echo(f'  Active: {active}')
    
    @users.command('delete')
    @click.argument('username')
    @click.option('--yes', is_flag=True, help='Skip confirmation prompt')
    def delete_user(username, yes):
        """Delete a user."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        if not yes:
            click.confirm(
                f'⚠️  Delete user "{username}"? This cannot be undone.',
                abort=True
            )
        
        db.session.delete(user)
        db.session.commit()
        
        click.echo(f'✓ User "{username}" deleted')
    
    @users.command('change-password')
    @click.argument('username')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='New password')
    def change_password(username, password):
        """Change a user's password."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        user.set_password(password)
        user.must_change_password = False
        db.session.commit()
        
        click.echo(f'✓ Password changed for user "{username}"')
    
    @users.command('activate')
    @click.argument('username')
    def activate_user(username):
        """Activate a user account."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        user.active = True
        db.session.commit()
        
        click.echo(f'✓ User "{username}" activated')
    
    @users.command('deactivate')
    @click.argument('username')
    def deactivate_user(username):
        """Deactivate a user account."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        user.active = False
        db.session.commit()
        
        click.echo(f'✓ User "{username}" deactivated')
    
    @users.command('grant-role')
    @click.argument('username')
    @click.argument('role', type=click.Choice(['admin', 'editor']))
    def grant_role(username, role):
        """Grant a role to a user."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            click.echo(f'❌ Role "{role}" not found')
            return
        
        if role_obj in user.roles:
            click.echo(f'  User "{username}" already has role "{role}"')
            return
        
        user.roles.append(role_obj)
        db.session.commit()
        
        click.echo(f'✓ Granted role "{role}" to user "{username}"')
    
    @users.command('revoke-role')
    @click.argument('username')
    @click.argument('role', type=click.Choice(['admin', 'editor']))
    def revoke_role(username, role):
        """Revoke a role from a user."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            click.echo(f'❌ Role "{role}" not found')
            return
        
        if role_obj not in user.roles:
            click.echo(f'  User "{username}" does not have role "{role}"')
            return
        
        user.roles.remove(role_obj)
        db.session.commit()
        
        click.echo(f'✓ Revoked role "{role}" from user "{username}"')
    
    # ============================================================================
    # INVITATION COMMANDS
    # ============================================================================
    
    @app.cli.group()
    def invitations():
        """User invitation management commands."""
        pass
    
    @invitations.command('create')
    @click.option('--email', prompt=True, help='Email address to invite')
    @click.option('--role', type=click.Choice(['admin', 'editor']), 
                  default='editor', help='Role for new user')
    def create_invitation(email, role):
        """Create a user invitation."""
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            click.echo(f'❌ User with email "{email}" already exists')
            return
        
        # Check for existing active invitation
        existing = UserInvitation.query.filter_by(
            email=email,
            used=False
        ).first()
        
        if existing and not existing.is_expired():
            click.echo(f'  Active invitation already exists for "{email}"')
            click.echo(f'  Token: {existing.token}')
            return
        
        # Get role
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            click.echo(f'❌ Role "{role}" not found')
            return
        
        # Create invitation
        invitation = UserInvitation(
            email=email,
            token=secrets.token_urlsafe(32),
            role_id=role_obj.id,
            invited_by_id=1  # Assume admin user
        )
        
        db.session.add(invitation)
        db.session.commit()
        
        click.echo(f'✓ Invitation created for "{email}"')
        click.echo(f'  Token: {invitation.token}')
        click.echo(f'  Role: {role}')
        click.echo(f'  Expires: {invitation.expires_at}')
        click.echo(f'\n  Registration URL:')
        click.echo(f'  http://localhost:5000/auth/register/{invitation.token}')
    
    @invitations.command('list')
    @click.option('--all', 'show_all', is_flag=True, 
                  help='Show all invitations (including used/expired)')
    def list_invitations(show_all):
        """List user invitations."""
        query = UserInvitation.query
        
        if not show_all:
            query = query.filter_by(used=False)
        
        invitations_list = query.order_by(UserInvitation.created_at.desc()).all()
        
        if not invitations_list:
            click.echo('No invitations found.')
            return
        
        click.echo('\n' + '='*100)
        click.echo(f'{"Email":<30} {"Role":<10} {"Status":<15} {"Created":<20} {"Expires"}')
        click.echo('='*100)
        
        for inv in invitations_list:
            role_name = inv.role.name if inv.role else 'N/A'
            
            if inv.used:
                status = 'Used'
            elif inv.is_expired():
                status = 'Expired'
            else:
                status = 'Active'
            
            created = inv.created_at.strftime('%Y-%m-%d %H:%M')
            expires = inv.expires_at.strftime('%Y-%m-%d %H:%M')
            
            click.echo(
                f'{inv.email:<30} {role_name:<10} {status:<15} '
                f'{created:<20} {expires}'
            )
        
        click.echo('='*100 + '\n')
    
    @invitations.command('revoke')
    @click.argument('email')
    def revoke_invitation(email):
        """Revoke an active invitation."""
        invitation = UserInvitation.query.filter_by(
            email=email,
            used=False
        ).first()
        
        if not invitation:
            click.echo(f'❌ No active invitation found for "{email}"')
            return
        
        db.session.delete(invitation)
        db.session.commit()
        
        click.echo(f'✓ Invitation for "{email}" revoked')
    
    # ============================================================================
    # DATA MANAGEMENT COMMANDS
    # ============================================================================
    
    @app.cli.group()
    def data():
        """Sample data management commands."""
        pass
    
    @data.command('create')
    @click.option('--workshops', default=3, help='Number of workshops to create')
    def create_sample_data(workshops):
        """Create sample data for testing."""
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            click.echo('❌ Admin user not found. Run: flask --app run database init')
            return
        
        click.echo(f'Creating {workshops} sample workshops...')
        _create_sample_data(admin, num_workshops=workshops)
        click.echo('✓ Sample data created successfully')
    
    @data.command('clear')
    @click.option('--yes', is_flag=True, help='Skip confirmation prompt')
    def clear_data(yes):
        """Clear all application data (keeps users and roles)."""
        if not yes:
            click.confirm(
                '⚠️  WARNING: This will delete all workshops, participants, '
                'sessions, and observations. Continue?',
                abort=True
            )
        
        # Delete in correct order to respect foreign keys
        ObservationalRecord.query.delete()
        Session.query.delete()
        Participant.query.delete()
        Workshop.query.delete()
        
        db.session.commit()
        
        click.echo('✓ Application data cleared')
        click.echo('  Users and roles preserved')
    
    # ============================================================================
    # ADMIN UTILITIES
    # ============================================================================
    
    @app.cli.group()
    def admin():
        """Administrative utilities."""
        pass
    
    @admin.command('generate-secret-key')
    def generate_secret_key():
        """Generate a new SECRET_KEY for configuration."""
        key = secrets.token_hex(32)
        click.echo('\nGenerated SECRET_KEY:')
        click.echo(f'  {key}')
        click.echo('\nAdd this to your .env file:')
        click.echo(f'  SECRET_KEY={key}\n')
    
    @admin.command('check-config')
    def check_config():
        """Check application configuration."""
        click.echo('\n' + '='*60)
        click.echo('APPLICATION CONFIGURATION')
        click.echo('='*60)
        
        config_items = [
            ('Environment', current_app.config.get('ENV')),
            ('Debug Mode', current_app.config.get('DEBUG')),
            ('Database URI', current_app.config.get('SQLALCHEMY_DATABASE_URI')),
            ('Secret Key Set', bool(current_app.config.get('SECRET_KEY'))),
            ('Mail Server', current_app.config.get('MAIL_SERVER')),
            ('Mail Username', current_app.config.get('MAIL_USERNAME')),
            ('JWT Secret Set', bool(current_app.config.get('JWT_SECRET_KEY'))),
        ]
        
        for key, value in config_items:
            # Mask sensitive values
            if 'SECRET' in key.upper() or 'PASSWORD' in key.upper():
                display_value = '***' if value else 'Not Set'
            else:
                display_value = value
            
            click.echo(f'  {key:<20} {display_value}')
        
        click.echo('='*60 + '\n')
    
    @admin.command('cleanup-invitations')
    def cleanup_invitations():
        """Remove expired and used invitations."""
        now = datetime.now(datetime.UTC)
        
        # Find expired invitations
        expired = UserInvitation.query.filter(
            UserInvitation.expires_at < now,
            UserInvitation.used == False
        ).all()
        
        # Find used invitations older than 30 days
        thirty_days_ago = now - timedelta(days=30)
        old_used = UserInvitation.query.filter(
            UserInvitation.used == True,
            UserInvitation.created_at < thirty_days_ago
        ).all()
        
        total = len(expired) + len(old_used)
        
        if total == 0:
            click.echo('No invitations to clean up.')
            return
        
        for inv in expired + old_used:
            db.session.delete(inv)
        
        db.session.commit()
        
        click.echo(f'✓ Cleaned up {total} invitations')
        click.echo(f'  Expired: {len(expired)}')
        click.echo(f'  Old used: {len(old_used)}')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _create_roles():
    """Create default roles."""
    roles_data = [
        ('admin', 'Administrator with full access'),
        ('editor', 'Editor with content management access')
    ]
    
    for role_name, description in roles_data:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=description)
            db.session.add(role)
    
    db.session.commit()


def _create_admin_user():
    """Create admin user."""
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        return admin
    
    admin_role = Role.query.filter_by(name='admin').first()
    
    admin = User(
        username='admin',
        email='admin@arteterapia.local',
        active=True,
        email_verified=True,
        must_change_password=True
    )
    admin.set_password('admin123')
    admin.roles.append(admin_role)
    
    db.session.add(admin)
    db.session.commit()
    
    return admin


def _create_sample_data(admin_user, num_workshops=3):
    """Create sample data for testing."""
    workshops_data = [
        {
            'name': 'Taller de Expresión Emocional',
            'objective': 'Explorar y expresar emociones a través del arte, '
                        'desarrollando habilidades de autoconocimiento y regulación emocional.'
        },
        {
            'name': 'Creatividad y Autoestima',
            'objective': 'Fortalecer la autoestima y confianza personal mediante '
                        'actividades artísticas que promuevan la autoaceptación.'
        },
        {
            'name': 'Arte y Mindfulness',
            'objective': 'Integrar técnicas de mindfulness con expresión artística '
                        'para reducir el estrés y aumentar la conciencia plena.'
        },
        {
            'name': 'Narrativa Visual',
            'objective': 'Desarrollar habilidades de narrativa personal a través '
                        'de la creación de historias visuales.'
        },
        {
            'name': 'Identidad y Pertenencia',
            'objective': 'Explorar temas de identidad cultural y pertenencia '
                        'mediante proyectos artísticos colaborativos.'
        }
    ]
    
    # Create workshops
    workshops = []
    for i in range(min(num_workshops, len(workshops_data))):
        w_data = workshops_data[i]
        workshop = Workshop(
            name=w_data['name'],
            objective=w_data['objective'],
            user_id=admin_user.id,
            created_at=datetime.now(datetime.UTC) - timedelta(days=30-i*5)
        )
        db.session.add(workshop)
        workshops.append(workshop)
    
    db.session.commit()
    
    # Create participants
    participants_names = [
        'María González', 'Juan Pérez', 'Ana Martínez', 'Carlos López',
        'Laura Rodríguez', 'Pedro Sánchez', 'Carmen Fernández', 'Miguel Torres'
    ]
    
    for workshop in workshops:
        num_participants = 4 + (workshops.index(workshop) % 3)
        for i in range(num_participants):
            participant = Participant(
                name=participants_names[i % len(participants_names)],
                workshop_id=workshop.id,
                extra_data={
                    'age': 25 + i * 5,
                    'notes': f'Participante activo del taller {workshop.name}'
                },
                created_at=workshop.created_at + timedelta(days=1)
            )
            db.session.add(participant)
    
    db.session.commit()
    
    # Create sessions
    sessions_data = [
        {
            'prompt': 'Dibuja cómo te sientes hoy usando solo colores',
            'motivation': 'Explorar la conexión entre emociones y colores.',
            'materials': ['Acuarelas', 'Pinceles', 'Papel acuarela', 'Agua']
        },
        {
            'prompt': 'Crea un collage que represente tu lugar seguro',
            'motivation': 'Identificar espacios emocionales de seguridad.',
            'materials': ['Revistas', 'Tijeras', 'Pegamento', 'Cartulina']
        },
        {
            'prompt': 'Modela con arcilla una forma que represente un desafío',
            'motivation': 'Externalizar dificultades mediante materiales táctiles.',
            'materials': ['Arcilla', 'Herramientas de modelado', 'Agua']
        }
    ]
    
    for workshop in workshops:
        num_sessions = 2 + (workshops.index(workshop) % 2)
        for i in range(num_sessions):
            session_data = sessions_data[i % len(sessions_data)]
            session = Session(
                workshop_id=workshop.id,
                prompt=session_data['prompt'],
                motivation=session_data['motivation'],
                materials=session_data['materials'],
                created_at=workshop.created_at + timedelta(days=7*(i+1))
            )
            db.session.add(session)
    
    db.session.commit()

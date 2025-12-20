"""
Database Setup Script
=====================
This script initializes the database with all tables and creates the admin user.
It can optionally populate the database with sample data for testing.

Usage:
    python setup_db.py              # Initialize DB + admin user only
    python setup_db.py --with-data  # Initialize DB + admin user + sample data
    python setup_db.py --reset      # Reset DB and initialize with admin only
    python setup_db.py --reset --with-data  # Reset DB and initialize with sample data
"""
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from flask_migrate import upgrade, init as migrate_init
from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.workshop import Workshop
from app.models.participant import Participant
from app.models.session import Session
from app.models.observation import ObservationalRecord


def reset_database():
    """Remove existing database file."""
    db_path = 'arteterapia.db'
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
        print("✓ Database removed")
    
    # Remove migrations directory
    migrations_dir = 'migrations'
    if os.path.exists(migrations_dir):
        import shutil
        print(f"Removing migrations directory: {migrations_dir}")
        shutil.rmtree(migrations_dir)
        print("✓ Migrations directory removed")


def init_database():
    """Initialize database with all tables."""
    print("\n" + "="*60)
    print("INITIALIZING DATABASE")
    print("="*60)
    
    # Remove empty database if exists
    db_path = 'arteterapia.db'
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        if file_size == 0:
            print(f"Removing empty database file...")
            os.remove(db_path)
    
    # Check if migrations directory exists
    migrations_dir = 'migrations'
    migrations_versions_dir = os.path.join(migrations_dir, 'versions')
    
    # Check if we have any migration files
    has_migrations = False
    if os.path.exists(migrations_versions_dir):
        migration_files = [f for f in os.listdir(migrations_versions_dir) if f.endswith('.py')]
        has_migrations = len(migration_files) > 0
    
    if not os.path.exists(migrations_dir):
        print("Migrations directory not found. Creating...")
        migrate_init()
        print("✓ Migrations directory created")
    
    # If we have migrations, apply them; otherwise create tables directly
    if has_migrations:
        print("Applying migrations...")
        try:
            upgrade()
            print("✓ Database migrations applied successfully")
        except Exception as e:
            print(f"Error applying migrations: {e}")
            print("Creating all tables directly...")
            db.create_all()
            print("✓ All tables created")
    else:
        print("No migration files found. Creating all tables directly...")
        db.create_all()
        print("✓ All tables created")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n✓ Database initialized successfully!")
    print(f"  Tables created: {len(tables)}")
    for table in sorted(tables):
        print(f"    - {table}")
    
    return True


def create_roles():
    """Create default roles."""
    print("\n" + "="*60)
    print("CREATING ROLES")
    print("="*60)
    
    roles_to_create = [
        ('admin', 'Administrator with full access'),
        ('editor', 'Editor with content management access')
    ]
    
    created_roles = []
    for role_name, description in roles_to_create:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.session.add(role)
            created_roles.append(role_name)
            print(f"✓ Created role: {role_name}")
        else:
            print(f"  Role already exists: {role_name}")
    
    db.session.commit()
    return created_roles


def create_admin_user():
    """Create admin user."""
    print("\n" + "="*60)
    print("CREATING ADMIN USER")
    print("="*60)
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("  Admin user already exists")
        return admin_user
    
    # Get admin role
    admin_role = Role.query.filter_by(name='admin').first()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@arteterapia.local',
        active=True,
        email_verified=True,  # Admin is pre-verified
        must_change_password=True  # Force password change on first login
    )
    admin.set_password('admin123')
    admin.roles.append(admin_role)
    
    db.session.add(admin)
    db.session.commit()
    
    print("✓ Admin user created successfully")
    print(f"  Username: admin")
    print(f"  Email: admin@arteterapia.local")
    print(f"  Password: admin123")
    print(f"  ⚠ IMPORTANT: Change this password on first login!")
    
    return admin


def create_sample_data(admin_user):
    """Create sample data for testing."""
    print("\n" + "="*60)
    print("CREATING SAMPLE DATA")
    print("="*60)
    
    # Create sample workshops
    workshops_data = [
        {
            'name': 'Taller de Expresión Emocional',
            'objective': 'Explorar y expresar emociones a través del arte, desarrollando habilidades de autoconocimiento y regulación emocional.'
        },
        {
            'name': 'Creatividad y Autoestima',
            'objective': 'Fortalecer la autoestima y confianza personal mediante actividades artísticas que promuevan la autoaceptación.'
        },
        {
            'name': 'Arte y Mindfulness',
            'objective': 'Integrar técnicas de mindfulness con expresión artística para reducir el estrés y aumentar la conciencia plena.'
        }
    ]
    
    workshops = []
    for idx, w_data in enumerate(workshops_data, 1):
        workshop = Workshop(
            name=w_data['name'],
            objective=w_data['objective'],
            user_id=admin_user.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=30-idx*5)
        )
        db.session.add(workshop)
        workshops.append(workshop)
        print(f"✓ Created workshop: {workshop.name}")
    
    db.session.commit()
    
    # Create participants for each workshop
    participants_names = [
        'María González', 'Juan Pérez', 'Ana Martínez', 'Carlos López',
        'Laura Rodríguez', 'Pedro Sánchez', 'Carmen Fernández', 'Miguel Torres'
    ]
    
    all_participants = []
    for workshop in workshops:
        # Each workshop gets 4-6 participants
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
            all_participants.append(participant)
        
        print(f"  ✓ Added {num_participants} participants to '{workshop.name}'")
    
    db.session.commit()
    
    # Create sessions for each workshop
    sessions_data = [
        {
            'prompt': 'Dibuja cómo te sientes hoy usando solo colores',
            'motivation': 'Explorar la conexión entre emociones y colores sin la presión de crear formas reconocibles.',
            'materials': ['Acuarelas', 'Pinceles', 'Papel acuarela', 'Agua']
        },
        {
            'prompt': 'Crea un collage que represente tu lugar seguro',
            'motivation': 'Identificar y visualizar espacios emocionales de seguridad y calma.',
            'materials': ['Revistas', 'Tijeras', 'Pegamento', 'Cartulina', 'Marcadores']
        },
        {
            'prompt': 'Modela con arcilla una forma que represente un desafío actual',
            'motivation': 'Externalizar dificultades mediante la manipulación táctil de materiales.',
            'materials': ['Arcilla', 'Herramientas de modelado', 'Agua', 'Paños']
        },
        {
            'prompt': 'Pinta un autorretrato emocional',
            'motivation': 'Explorar la autopercepción y la identidad emocional.',
            'materials': ['Acrílicos', 'Pinceles', 'Lienzo', 'Paleta', 'Agua']
        }
    ]
    
    all_sessions = []
    for workshop in workshops:
        # Each workshop gets 2-3 sessions
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
            all_sessions.append(session)
        
        print(f"  ✓ Added {num_sessions} sessions to '{workshop.name}'")
    
    db.session.commit()
    
    # Create observational records
    # Sample answers for observations
    sample_answers = {
        'entry_on_time': 'yes',
        'entry_resistance': 'no',
        'entry_mood': 'positive',
        'process_engagement': 'high',
        'process_focus': 'sustained',
        'process_creativity': 'exploratory',
        'process_materials': 'confident',
        'social_interaction': 'collaborative',
        'social_sharing': 'willing',
        'emotional_expression': 'open',
        'emotional_regulation': 'adaptive',
        'completion_satisfaction': 'satisfied',
        'completion_reflection': 'insightful'
    }
    
    observation_count = 0
    for session in all_sessions:
        # Get participants from the same workshop
        workshop_participants = Participant.query.filter_by(
            workshop_id=session.workshop_id
        ).all()
        
        # Create observations for 50-75% of participants
        num_observations = max(1, int(len(workshop_participants) * 0.6))
        for i in range(num_observations):
            participant = workshop_participants[i % len(workshop_participants)]
            
            # Vary the answers slightly for each observation
            varied_answers = sample_answers.copy()
            if i % 3 == 0:
                varied_answers['entry_mood'] = 'neutral'
                varied_answers['process_engagement'] = 'moderate'
            elif i % 3 == 1:
                varied_answers['emotional_expression'] = 'reserved'
                varied_answers['social_interaction'] = 'independent'
            
            observation = ObservationalRecord(
                session_id=session.id,
                participant_id=participant.id,
                version=1,
                answers=varied_answers,
                freeform_notes=f'El participante mostró interés en la actividad. '
                              f'Se observó progreso en la expresión emocional.',
                created_at=session.created_at + timedelta(hours=2)
            )
            db.session.add(observation)
            observation_count += 1
    
    db.session.commit()
    print(f"  ✓ Created {observation_count} observational records")
    
    # Summary
    print("\n" + "="*60)
    print("SAMPLE DATA SUMMARY")
    print("="*60)
    print(f"  Workshops: {len(workshops)}")
    print(f"  Participants: {len(all_participants)}")
    print(f"  Sessions: {len(all_sessions)}")
    print(f"  Observations: {observation_count}")
    print("="*60)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description='Initialize the arteterapia database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--with-data',
        action='store_true',
        help='Populate database with sample data'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database before initialization (WARNING: deletes all data)'
    )
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        try:
            # Reset database if requested
            if args.reset:
                print("\n⚠ WARNING: This will delete all existing data!")
                response = input("Are you sure you want to reset the database? (yes/no): ")
                if response.lower() != 'yes':
                    print("Operation cancelled.")
                    sys.exit(0)
                reset_database()
            
            # Initialize database
            init_database()
            
            # Create roles
            create_roles()
            
            # Create admin user
            admin_user = create_admin_user()
            
            # Create sample data if requested
            if args.with_data:
                create_sample_data(admin_user)
            
            # Final summary
            print("\n" + "="*60)
            print("DATABASE SETUP COMPLETE!")
            print("="*60)
            print("\n✓ Database initialized successfully")
            print("✓ Admin user created")
            if args.with_data:
                print("✓ Sample data created")
            
            print("\n" + "="*60)
            print("NEXT STEPS")
            print("="*60)
            print("1. Start the application: python run.py")
            print("2. Login with:")
            print("   Username: admin")
            print("   Password: admin123")
            print("3. Change the admin password on first login")
            print("="*60 + "\n")
            
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()

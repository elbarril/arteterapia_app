"""
Tests for SessionService.

Tests all CRUD operations, permission checks, and material parsing.
"""
import pytest
from app.services.session_service import SessionService
from app.models.session import Session
from app.models.user import User


class TestSessionServiceList:
    """Tests for listing sessions."""
    
    def test_get_workshop_sessions_as_owner(self, app, db, sample_workshop, sample_session):
        """Owner should see workshop sessions."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            sessions = SessionService.get_workshop_sessions(sample_workshop, admin.id)
            
            assert sessions is not None
            assert len(sessions) >= 1
    
    def test_get_workshop_sessions_no_permission(self, app, db, sample_workshop):
        """Editor should not see other's workshop sessions."""
        with app.app_context():
            editor = User.query.filter_by(username='editor').first()
            sessions = SessionService.get_workshop_sessions(sample_workshop, editor.id)
            
            # Should return None for no permission
            admin = User.query.filter_by(username='admin').first()
            if admin.id != editor.id:
                assert sessions is None


class TestSessionServiceGet:
    """Tests for getting single session."""
    
    def test_get_session_as_owner(self, app, db, sample_session):
        """Owner should access their session."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            session = SessionService.get_session(sample_session, admin.id)
            
            assert session is not None
            assert session.id == sample_session
    
    def test_get_session_no_permission(self, app, db, sample_session):
        """Editor should not access other's session."""
        with app.app_context():
            editor = User.query.filter_by(username='editor').first()
            session = SessionService.get_session(sample_session, editor.id)
            
            admin = User.query.filter_by(username='admin').first()
            if admin.id != editor.id:
                assert session is None


class TestSessionServiceCreate:
    """Tests for creating sessions."""
    
    def test_create_session_success(self, app, db, sample_workshop):
        """Should create session successfully."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            session = SessionService.create_session(
                workshop_id=sample_workshop,
                user_id=admin.id,
                prompt='Test prompt',
                motivation='Test motivation',
                materials='paint, brushes, canvas'
            )
            
            assert session is not None
            assert session.prompt == 'Test prompt'
            assert session.motivation == 'Test motivation'
            assert session.materials == ['paint', 'brushes', 'canvas']
    
    def test_create_session_with_list_materials(self, app, db, sample_workshop):
        """Should create session with materials as list."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            session = SessionService.create_session(
                workshop_id=sample_workshop,
                user_id=admin.id,
                prompt='Test prompt',
                materials=['clay', 'tools']
            )
            
            assert session is not None
            assert session.materials == ['clay', 'tools']
    
    def test_create_session_no_permission(self, app, db, sample_workshop):
        """Editor should not create session for other's workshop."""
        with app.app_context():
            editor = User.query.filter_by(username='editor').first()
            
            session = SessionService.create_session(
                workshop_id=sample_workshop,
                user_id=editor.id,
                prompt='Hacked prompt'
            )
            
            admin = User.query.filter_by(username='admin').first()
            if admin.id != editor.id:
                assert session is None


class TestSessionServiceUpdate:
    """Tests for updating sessions."""
    
    def test_update_session_prompt(self, app, db, sample_session):
        """Should update session prompt."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            session = SessionService.update_session(
                sample_session,
                admin.id,
                {'prompt': 'Updated prompt'}
            )
            
            assert session is not None
            assert session.prompt == 'Updated prompt'
    
    def test_update_session_materials(self, app, db, sample_session):
        """Should update session materials."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            session = SessionService.update_session(
                sample_session,
                admin.id,
                {'materials': 'watercolors, paper'}
            )
            
            assert session is not None
            assert session.materials == ['watercolors', 'paper']
    
    def test_update_session_no_permission(self, app, db, sample_session):
        """Editor should not update other's session."""
        with app.app_context():
            editor = User.query.filter_by(username='editor').first()
            
            session = SessionService.update_session(
                sample_session,
                editor.id,
                {'prompt': 'Hacked prompt'}
            )
            
            admin = User.query.filter_by(username='admin').first()
            if admin.id != editor.id:
                assert session is None


class TestSessionServiceDelete:
    """Tests for deleting sessions."""
    
    def test_delete_session_success(self, app, db, sample_workshop):
        """Should delete session successfully."""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            # Create session to delete
            session = SessionService.create_session(
                workshop_id=sample_workshop,
                user_id=admin.id,
                prompt='To delete'
            )
            session_id = session.id
            
            # Delete it
            result = SessionService.delete_session(session_id, admin.id)
            
            assert result is not None
            assert result['workshop_id'] == sample_workshop
            
            # Verify deletion
            deleted = Session.query.get(session_id)
            assert deleted is None
    
    def test_delete_session_no_permission(self, app, db, sample_session):
        """Editor should not delete other's session."""
        with app.app_context():
            editor = User.query.filter_by(username='editor').first()
            
            result = SessionService.delete_session(sample_session, editor.id)
            
            admin = User.query.filter_by(username='admin').first()
            if admin.id != editor.id:
                assert result is None


class TestSessionServiceMaterialParsing:
    """Tests for material parsing helper."""
    
    def test_parse_materials_comma_separated(self):
        """Should parse comma-separated materials."""
        materials = SessionService._parse_materials('paint, brushes, canvas')
        assert materials == ['paint', 'brushes', 'canvas']
    
    def test_parse_materials_single_item(self):
        """Should parse single material."""
        materials = SessionService._parse_materials('clay')
        assert materials == ['clay']
    
    def test_parse_materials_empty_string(self):
        """Should return None for empty string."""
        materials = SessionService._parse_materials('')
        assert materials is None
    
    def test_parse_materials_whitespace_only(self):
        """Should return None for whitespace only."""
        materials = SessionService._parse_materials('   ')
        assert materials is None
    
    def test_parse_materials_with_extra_spaces(self):
        """Should strip extra spaces."""
        materials = SessionService._parse_materials('  paint  ,  brushes  ,  canvas  ')
        assert materials == ['paint', 'brushes', 'canvas']

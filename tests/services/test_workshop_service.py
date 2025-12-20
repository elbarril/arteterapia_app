"""
Tests for WorkshopService.

Tests all CRUD operations and permission checks for workshop management.
"""
import pytest
from app.services.workshop_service import WorkshopService
from app.models.workshop import Workshop
from app.models.user import User


class TestWorkshopServiceList:
    """Tests for listing workshops."""
    
    def test_get_user_workshops_as_admin(self, app, db, admin_user, editor_user, sample_workshop):
        """Admin should see all workshops."""
        with app.app_context():
            workshops = WorkshopService.get_user_workshops(admin_user.id)
            
            assert workshops is not None
            assert len(workshops) >= 1
            assert any(w.id == sample_workshop for w in workshops)
    
    def test_get_user_workshops_as_editor(self, app, db, admin_user, editor_user):
        """Editor should only see their own workshops."""
        with app.app_context():
            
            # Create workshop for editor
            workshop = WorkshopService.create_workshop(
                user_id=editor_user.id,
                name='Editor Workshop',
                objective='Editor objective'
            )
            
            workshops = WorkshopService.get_user_workshops(editor_user.id)
            
            assert workshops is not None
            assert all(w.user_id == editor_user.id for w in workshops)
    
    def test_get_user_workshops_invalid_user(self, app, db, admin_user, editor_user):
        """Should return empty list for invalid user."""
        with app.app_context():
            workshops = WorkshopService.get_user_workshops(99999)
            assert workshops == []


class TestWorkshopServiceGet:
    """Tests for getting single workshop."""
    
    def test_get_workshop_as_owner(self, app, db, admin_user, editor_user, sample_workshop):
        """Owner should access their workshop."""
        with app.app_context():
            workshop = WorkshopService.get_workshop(sample_workshop, admin_user.id)
            
            assert workshop is not None
            assert workshop.id == sample_workshop
    
    def test_get_workshop_as_admin(self, app, db, admin_user, editor_user, sample_workshop):
        """Admin should access any workshop."""
        with app.app_context():
            workshop = WorkshopService.get_workshop(sample_workshop, admin_user.id)
            
            assert workshop is not None
    
    def test_get_workshop_no_permission(self, app, db, admin_user, editor_user, sample_workshop):
        """Editor should not access other's workshop."""
        with app.app_context():
            workshop = WorkshopService.get_workshop(sample_workshop, editor_user.id)
            
            # Editor cannot access admin's workshop
            if admin_user.id != editor_user.id:
                assert workshop is None
    
    def test_get_workshop_not_found(self, app, db, admin_user, editor_user):
        """Should return None for non-existent workshop."""
        with app.app_context():
            workshop = WorkshopService.get_workshop(99999, admin_user.id)
            
            assert workshop is None


class TestWorkshopServiceCreate:
    """Tests for creating workshops."""
    
    def test_create_workshop_success(self, app, db, admin_user, editor_user):
        """Should create workshop successfully."""
        with app.app_context():
            
            workshop = WorkshopService.create_workshop(
                user_id=admin_user.id,
                name='New Workshop',
                objective='Test objective'
            )
            
            assert workshop is not None
            assert workshop.name == 'New Workshop'
            assert workshop.objective == 'Test objective'
            assert workshop.user_id == admin_user.id
    
    def test_create_workshop_without_objective(self, app, db, admin_user, editor_user):
        """Should create workshop without objective."""
        with app.app_context():
            
            workshop = WorkshopService.create_workshop(
                user_id=admin_user.id,
                name='Workshop No Objective'
            )
            
            assert workshop is not None
            assert workshop.objective is None


class TestWorkshopServiceUpdate:
    """Tests for updating workshops."""
    
    def test_update_workshop_name(self, app, db, admin_user, editor_user, sample_workshop):
        """Should update workshop name."""
        with app.app_context():
            
            workshop = WorkshopService.update_workshop(
                sample_workshop,
                admin_user.id,
                {'name': 'Updated Name'}
            )
            
            assert workshop is not None
            assert workshop.name == 'Updated Name'
    
    def test_update_workshop_objective(self, app, db, admin_user, editor_user, sample_workshop):
        """Should update workshop objective."""
        with app.app_context():
            
            workshop = WorkshopService.update_workshop(
                sample_workshop,
                admin_user.id,
                {'objective': 'Updated Objective'}
            )
            
            assert workshop is not None
            assert workshop.objective == 'Updated Objective'
    
    def test_update_workshop_no_permission(self, app, db, admin_user, editor_user, sample_workshop):
        """Editor should not update other's workshop."""
        with app.app_context():
            
            workshop = WorkshopService.update_workshop(
                sample_workshop,
                editor_user.id,
                {'name': 'Hacked Name'}
            )
            
            # Should return None for no permission
            if admin_user.id != editor_user.id:
                assert workshop is None


class TestWorkshopServiceDelete:
    """Tests for deleting workshops."""
    
    def test_delete_workshop_success(self, app, db, admin_user, editor_user):
        """Should delete workshop successfully."""
        with app.app_context():
            
            # Create workshop to delete
            workshop = WorkshopService.create_workshop(
                user_id=admin_user.id,
                name='To Delete'
            )
            workshop_id = workshop.id
            
            # Delete it
            result = WorkshopService.delete_workshop(workshop_id, admin_user.id)
            
            assert result is True
            
            # Verify deletion
            deleted = Workshop.query.get(workshop_id)
            assert deleted is None
    
    def test_delete_workshop_no_permission(self, app, db, admin_user, editor_user, sample_workshop):
        """Editor should not delete other's workshop."""
        with app.app_context():
            
            result = WorkshopService.delete_workshop(sample_workshop, editor_user.id)
            
            # Should return False for no permission
            if admin_user.id != editor_user.id:
                assert result is False

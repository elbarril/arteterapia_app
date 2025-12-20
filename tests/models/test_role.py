"""Tests for Role model."""
import pytest
from app.models.role import Role


class TestRoleModel:
    """Tests for Role model basic functionality."""
    
    def test_create_role(self, db):
        """Test creating a new role."""
        role = Role(
            name='test_role',
            description='Test role description'
        )
        db.session.add(role)
        db.session.commit()
        
        assert role.id is not None
        assert role.name == 'test_role'
        assert role.description == 'Test role description'
        assert role.created_at is not None
    
    def test_role_repr(self, db):
        """Test role string representation."""
        role = Role(name='test_role')
        db.session.add(role)
        db.session.commit()
        
        assert repr(role) == '<Role test_role>'
    
    def test_unique_name_constraint(self, db):
        """Test that role names must be unique."""
        role1 = Role(name='duplicate')
        db.session.add(role1)
        db.session.commit()
        
        role2 = Role(name='duplicate')
        db.session.add(role2)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_role_without_description(self, db):
        """Test creating role without description."""
        role = Role(name='minimal_role')
        db.session.add(role)
        db.session.commit()
        
        assert role.description is None


class TestRoleRelationships:
    """Tests for Role relationships."""
    
    def test_role_users_relationship(self, db, admin_user):
        """Test role-users relationship."""
        admin_role = Role.query.filter_by(name='admin').first()
        
        assert admin_user in admin_role.users.all()
    
    def test_multiple_users_same_role(self, db, admin_user, editor_user):
        """Test multiple users with same role."""
        from app.models.user import User
        
        editor_role = Role.query.filter_by(name='editor').first()
        
        # Add editor role to admin user
        admin_user.roles.append(editor_role)
        db.session.commit()
        
        # Both users should have editor role
        assert admin_user in editor_role.users.all()
        assert editor_user in editor_role.users.all()

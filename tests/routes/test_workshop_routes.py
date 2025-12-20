"""
Tests for workshop routes.

Tests all workshop routes including list, create, detail,
update objective, and delete operations.
"""
import pytest
from app.models.workshop import Workshop


class TestWorkshopList:
    """Tests for workshop list route."""
    
    def test_list_requires_login(self, client):
        """Test that workshop list requires authentication."""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_list_workshops_empty(self, client, admin_user):
        """Test workshop list when no workshops exist."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'taller' in response.data.lower() or b'workshop' in response.data.lower()
    
    def test_list_workshops_with_data(self, client, db, admin_user, sample_workshop):
        """Test workshop list with existing workshops."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'Test Workshop' in response.data


class TestWorkshopCreate:
    """Tests for workshop creation route."""
    
    def test_create_requires_login(self, client):
        """Test that workshop creation requires authentication."""
        response = client.post('/workshop/create', data={'name': 'Test'}, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_create_workshop_success(self, client, db, admin_user):
        """Test successful workshop creation."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/workshop/create', data={
            'name': 'New Workshop'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify workshop was created
        workshop = Workshop.query.filter_by(name='New Workshop').first()
        assert workshop is not None
        assert workshop.user_id == admin_user.id
    
    def test_create_workshop_empty_name(self, client, db, admin_user):
        """Test workshop creation with empty name."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post('/workshop/create', data={
            'name': ''
        })
        
        assert response.status_code == 400


class TestWorkshopDetail:
    """Tests for workshop detail route."""
    
    def test_detail_requires_login(self, client, sample_workshop):
        """Test that workshop detail requires authentication."""
        response = client.get(f'/{sample_workshop}', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_detail_workshop_success(self, client, db, admin_user, sample_workshop):
        """Test successful workshop detail view."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get(f'/{sample_workshop}')
        assert response.status_code == 200
        assert b'Test Workshop' in response.data
    
    def test_detail_workshop_not_found(self, client, admin_user):
        """Test workshop detail with non-existent workshop."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/99999')
        assert response.status_code == 404
    
    def test_detail_workshop_permission_denied(self, client, db, admin_user, editor_user):
        """Test workshop detail when user doesn't own the workshop."""
        # Create workshop as admin
        workshop = Workshop(name='Admin Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        workshop_id = workshop.id
        
        # Login as editor
        client.post('/login', data={
            'username': 'editor',
            'password': 'editor123'
        })
        
        response = client.get(f'/{workshop_id}', follow_redirects=False)
        assert response.status_code == 302


class TestWorkshopUpdateObjective:
    """Tests for workshop objective update route."""
    
    def test_update_objective_requires_login(self, client, sample_workshop):
        """Test that objective update requires authentication."""
        response = client.post(f'/{sample_workshop}/objective',
                             json={'objective': 'New objective'},
                             follow_redirects=False)
        assert response.status_code == 302
    
    def test_update_objective_success(self, client, db, admin_user, sample_workshop):
        """Test successful objective update."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/{sample_workshop}/objective',
                             json={'objective': 'Updated objective'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['objective'] == 'Updated objective'
        
        # Verify in database
        workshop = Workshop.query.get(sample_workshop)
        assert workshop.objective == 'Updated objective'
    
    def test_update_objective_permission_denied(self, client, db, admin_user, editor_user):
        """Test objective update when user doesn't own the workshop."""
        # Create workshop as admin
        workshop = Workshop(name='Admin Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        workshop_id = workshop.id
        
        # Login as editor
        client.post('/login', data={
            'username': 'editor',
            'password': 'editor123'
        })
        
        response = client.post(f'/{workshop_id}/objective',
                             json={'objective': 'Hacked objective'})
        
        assert response.status_code == 403


class TestWorkshopDelete:
    """Tests for workshop deletion route."""
    
    def test_delete_requires_login(self, client, sample_workshop):
        """Test that workshop deletion requires authentication."""
        response = client.post(f'/{sample_workshop}/delete', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_delete_workshop_success(self, client, db, admin_user, sample_workshop):
        """Test successful workshop deletion."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.post(f'/{sample_workshop}/delete', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/' in response.location
        
        # Verify workshop was deleted
        workshop = Workshop.query.get(sample_workshop)
        assert workshop is None
    
    def test_delete_workshop_permission_denied(self, client, db, admin_user, editor_user):
        """Test workshop deletion when user doesn't own the workshop."""
        # Create workshop as admin
        workshop = Workshop(name='Admin Workshop', user_id=admin_user.id)
        db.session.add(workshop)
        db.session.commit()
        workshop_id = workshop.id
        
        # Login as editor
        client.post('/login', data={
            'username': 'editor',
            'password': 'editor123'
        })
        
        response = client.post(f'/{workshop_id}/delete', follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify workshop was NOT deleted
        workshop = Workshop.query.get(workshop_id)
        assert workshop is not None

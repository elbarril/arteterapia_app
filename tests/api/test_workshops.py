"""
Tests for workshop API endpoints.
"""
import pytest


class TestWorkshopList:
    """Tests for GET /api/v1/workshops"""
    
    def test_list_workshops_as_admin(self, client, admin_headers, sample_workshop):
        """Test listing workshops as admin user."""
        response = client.get('/api/v1/workshops', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(w['id'] == sample_workshop for w in data)
    
    def test_list_workshops_as_editor(self, client, editor_headers):
        """Test listing workshops as editor user (only owns their own)."""
        response = client.get('/api/v1/workshops', headers=editor_headers)
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
    
    def test_list_workshops_without_auth(self, client):
        """Test listing workshops without authentication."""
        response = client.get('/api/v1/workshops')
        
        assert response.status_code == 401


class TestWorkshopCreate:
    """Tests for POST /api/v1/workshops"""
    
    def test_create_workshop_success(self, client, admin_headers):
        """Test creating a workshop successfully."""
        response = client.post('/api/v1/workshops', 
                              headers=admin_headers,
                              json={
                                  'name': 'New API Workshop',
                                  'objective': 'Test objective'
                              })
        
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'New API Workshop'
        assert data['objective'] == 'Test objective'
        assert 'id' in data
    
    def test_create_workshop_without_objective(self, client, admin_headers):
        """Test creating workshop without objective (optional field)."""
        response = client.post('/api/v1/workshops',
                              headers=admin_headers,
                              json={'name': 'Workshop without objective'})
        
        assert response.status_code == 201
        assert response.json['name'] == 'Workshop without objective'
    
    def test_create_workshop_without_name(self, client, admin_headers):
        """Test creating workshop without name (required field)."""
        response = client.post('/api/v1/workshops',
                              headers=admin_headers,
                              json={'objective': 'No name'})
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_create_workshop_without_auth(self, client):
        """Test creating workshop without authentication."""
        response = client.post('/api/v1/workshops',
                              json={'name': 'Unauthorized Workshop'})
        
        assert response.status_code == 401


class TestWorkshopGet:
    """Tests for GET /api/v1/workshops/{id}"""
    
    def test_get_workshop_success(self, client, admin_headers, sample_workshop):
        """Test getting workshop details."""
        response = client.get(f'/api/v1/workshops/{sample_workshop}',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_workshop
        assert data['name'] == 'Test Workshop'
        assert 'participants' in data
        assert 'sessions' in data
    
    def test_get_workshop_not_found(self, client, admin_headers):
        """Test getting non-existent workshop."""
        response = client.get('/api/v1/workshops/99999',
                            headers=admin_headers)
        
        assert response.status_code == 404
        assert 'error' in response.json
    
    def test_get_workshop_without_auth(self, client, sample_workshop):
        """Test getting workshop without authentication."""
        response = client.get(f'/api/v1/workshops/{sample_workshop}')
        
        assert response.status_code == 401


class TestWorkshopUpdate:
    """Tests for PATCH /api/v1/workshops/{id}"""
    
    def test_update_workshop_name(self, client, admin_headers, sample_workshop):
        """Test updating workshop name."""
        response = client.patch(f'/api/v1/workshops/{sample_workshop}',
                               headers=admin_headers,
                               json={'name': 'Updated Workshop Name'})
        
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'Updated Workshop Name'
    
    def test_update_workshop_objective(self, client, admin_headers, sample_workshop):
        """Test updating workshop objective."""
        response = client.patch(f'/api/v1/workshops/{sample_workshop}',
                               headers=admin_headers,
                               json={'objective': 'Updated objective'})
        
        assert response.status_code == 200
        assert response.json['objective'] == 'Updated objective'
    
    def test_update_workshop_both_fields(self, client, admin_headers, sample_workshop):
        """Test updating multiple fields at once."""
        response = client.patch(f'/api/v1/workshops/{sample_workshop}',
                               headers=admin_headers,
                               json={
                                   'name': 'New Name',
                                   'objective': 'New Objective'
                               })
        
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'New Name'
        assert data['objective'] == 'New Objective'
    
    def test_update_workshop_not_found(self, client, admin_headers):
        """Test updating non-existent workshop."""
        response = client.patch('/api/v1/workshops/99999',
                               headers=admin_headers,
                               json={'name': 'Does not exist'})
        
        assert response.status_code == 404
    
    def test_update_workshop_without_data(self, client, admin_headers, sample_workshop):
        """Test updating without providing data."""
        response = client.patch(f'/api/v1/workshops/{sample_workshop}',
                               headers=admin_headers,
                               json={})
        
        assert response.status_code == 400


class TestWorkshopDelete:
    """Tests for DELETE /api/v1/workshops/{id}"""
    
    def test_delete_workshop_success(self, client, admin_headers, sample_workshop):
        """Test deleting a workshop."""
        response = client.delete(f'/api/v1/workshops/{sample_workshop}',
                                headers=admin_headers)
        
        assert response.status_code == 200
        assert 'message' in response.json
        
        # Verify it's deleted
        get_response = client.get(f'/api/v1/workshops/{sample_workshop}',
                                  headers=admin_headers)
        assert get_response.status_code == 404
    
    def test_delete_workshop_not_found(self, client, admin_headers):
        """Test deleting non-existent workshop."""
        response = client.delete('/api/v1/workshops/99999',
                                headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_delete_workshop_without_auth(self, client, sample_workshop):
        """Test deleting workshop without authentication."""
        response = client.delete(f'/api/v1/workshops/{sample_workshop}')
        
        assert response.status_code == 401


class TestWorkshopPermissions:
    """Tests for workshop permission checks."""
    
    def test_editor_cannot_see_admin_workshops(self, client, editor_headers, sample_workshop):
        """Test that editor cannot access admin's workshop."""
        response = client.get(f'/api/v1/workshops/{sample_workshop}',
                            headers=editor_headers)
        
        # Editor should not have access to admin's workshop
        assert response.status_code == 404
    
    def test_editor_can_create_own_workshop(self, client, editor_headers):
        """Test that editor can create and access their own workshop."""
        # Create workshop as editor
        create_response = client.post('/api/v1/workshops',
                                      headers=editor_headers,
                                      json={'name': 'Editor Workshop'})
        
        assert create_response.status_code == 201
        workshop_id = create_response.json['id']
        
        # Verify editor can access their own workshop
        get_response = client.get(f'/api/v1/workshops/{workshop_id}',
                                  headers=editor_headers)
        
        assert get_response.status_code == 200
        assert get_response.json['name'] == 'Editor Workshop'

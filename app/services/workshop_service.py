"""Business logic for workshop operations (shared by API and controllers)."""
from app import db
from app.models.workshop import Workshop
from app.models.user import User


class WorkshopService:
    """Workshop business logic layer."""
    
    @staticmethod
    def get_user_workshops(user_id):
        """
        Get all workshops for a user (admins see all).
        
        Args:
            user_id: ID of the requesting user
            
        Returns:
            List of Workshop objects
        """
        user = User.query.get(user_id)
        
        if not user:
            return []
        
        if user.is_admin():
            return Workshop.query.order_by(Workshop.created_at.desc()).all()
        else:
            return Workshop.query.filter_by(user_id=user_id)\
                .order_by(Workshop.created_at.desc()).all()
    
    @staticmethod
    def get_workshop(workshop_id, user_id):
        """
        Get single workshop with permission check.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            
        Returns:
            Workshop object or None if not found / no permission
        """
        workshop = Workshop.query.get(workshop_id)
        
        if not workshop:
            return None
        
        user = User.query.get(user_id)
        
        if not user:
            return None
        
        # Check access permission
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        return workshop
    
    @staticmethod
    def create_workshop(user_id, name, objective=None):
        """
        Create new workshop.
        
        Args:
            user_id: ID of the user creating the workshop
            name: Workshop name
            objective: Workshop objective (optional)
            
        Returns:
            Created Workshop object
        """
        workshop = Workshop(
            name=name,
            objective=objective,
            user_id=user_id
        )
        db.session.add(workshop)
        db.session.commit()
        return workshop
    
    @staticmethod
    def update_workshop(workshop_id, user_id, data):
        """
        Update workshop with permission check.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            data: Dictionary with fields to update (name, objective)
            
        Returns:
            Updated Workshop object or None if not found / no permission
        """
        workshop = WorkshopService.get_workshop(workshop_id, user_id)
        
        if not workshop:
            return None
        
        if 'name' in data and data['name']:
            workshop.name = data['name']
        if 'objective' in data:
            workshop.objective = data['objective']
        
        db.session.commit()
        return workshop
    
    @staticmethod
    def delete_workshop(workshop_id, user_id):
        """
        Delete workshop with permission check.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            
        Returns:
            True if deleted, False if not found / no permission
        """
        workshop = WorkshopService.get_workshop(workshop_id, user_id)
        
        if not workshop:
            return False
        
        db.session.delete(workshop)
        db.session.commit()
        return True

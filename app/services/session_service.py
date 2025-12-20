"""Session service layer for business logic.

This service handles all session-related operations with proper
permission checks and data validation.
"""
from app import db
from app.models.session import Session
from app.models.workshop import Workshop
from app.models.user import User


class SessionService:
    """Session business logic layer."""
    
    @staticmethod
    def get_workshop_sessions(workshop_id, user_id):
        """
        Get all sessions for a workshop with permission check.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            
        Returns:
            List of Session objects or None if no access
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
        
        return workshop.sessions.order_by(Session.created_at.desc()).all()
    
    @staticmethod
    def get_session(session_id, user_id):
        """
        Get single session with permission check.
        
        Args:
            session_id: ID of the session
            user_id: ID of the requesting user
            
        Returns:
            Session object or None if not found / no permission
        """
        session = Session.query.get(session_id)
        
        if not session:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check access permission through workshop
        workshop = session.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        return session
    
    @staticmethod
    def create_session(workshop_id, user_id, prompt, motivation=None, materials=None):
        """
        Create a new session.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            prompt: Session prompt (required)
            motivation: Session motivation (optional)
            materials: Materials as string (comma-separated) or list
            
        Returns:
            Session object or None if no permission
        """
        workshop = Workshop.query.get(workshop_id)
        if not workshop:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check permission
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        # Parse materials if provided as string
        if isinstance(materials, str):
            materials = SessionService._parse_materials(materials)
        
        session = Session(
            workshop_id=workshop_id,
            prompt=prompt,
            motivation=motivation,
            materials=materials
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def update_session(session_id, user_id, data):
        """
        Update a session.
        
        Args:
            session_id: ID of the session
            user_id: ID of the requesting user
            data: Dictionary with fields to update (prompt, motivation, materials)
            
        Returns:
            Session object or None if not found / no permission
        """
        session = Session.query.get(session_id)
        
        if not session:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check permission through workshop
        workshop = session.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        # Update fields
        if 'prompt' in data:
            session.prompt = data['prompt']
        if 'motivation' in data:
            session.motivation = data['motivation']
        if 'materials' in data:
            # Parse if string, otherwise use as-is
            materials = data['materials']
            if isinstance(materials, str):
                materials = SessionService._parse_materials(materials)
            session.materials = materials
        
        db.session.commit()
        
        return session
    
    @staticmethod
    def delete_session(session_id, user_id):
        """
        Delete a session.
        
        Args:
            session_id: ID of the session
            user_id: ID of the requesting user
            
        Returns:
            Dictionary with success status and workshop_id, or None if not found / no permission
        """
        session = Session.query.get(session_id)
        
        if not session:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check permission through workshop
        workshop = session.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        # Store workshop_id before deletion
        workshop_id = session.workshop_id
        
        db.session.delete(session)
        db.session.commit()
        
        return {'workshop_id': workshop_id}
    
    @staticmethod
    def _parse_materials(materials_raw):
        """
        Parse comma-separated materials string into list.
        
        Args:
            materials_raw: Comma-separated string of materials
            
        Returns:
            List of material strings (stripped, non-empty) or None
        """
        if not materials_raw or not materials_raw.strip():
            return None
        
        materials = [m.strip() for m in materials_raw.split(',') if m.strip()]
        return materials if materials else None

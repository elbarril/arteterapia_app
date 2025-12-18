"""Participant service layer for business logic."""
from app import db
from app.models.participant import Participant
from app.models.workshop import Workshop
from app.models.user import User


class ParticipantService:
    """Participant business logic layer."""
    
    @staticmethod
    def get_workshop_participants(workshop_id, user_id):
        """
        Get all participants for a workshop.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            
        Returns:
            List of Participant objects or None if no access
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
        
        return workshop.participants.all()
    
    @staticmethod
    def get_participant(participant_id, user_id):
        """
        Get single participant with permission check.
        
        Args:
            participant_id: ID of the participant
            user_id: ID of the requesting user
            
        Returns:
            Participant object or None if not found / no permission
        """
        participant = Participant.query.get(participant_id)
        
        if not participant:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check access permission through workshop
        workshop = participant.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        return participant
    
    @staticmethod
    def create_participant(workshop_id, user_id, name, extra_data=None):
        """
        Create a new participant.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            name: Participant name
            extra_data: Optional extra data dictionary
            
        Returns:
            Participant object or None if no permission
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
        
        participant = Participant(
            name=name,
            workshop_id=workshop_id,
            extra_data=extra_data or {}
        )
        
        db.session.add(participant)
        db.session.commit()
        
        return participant
    
    @staticmethod
    def update_participant(participant_id, user_id, data):
        """
        Update a participant.
        
        Args:
            participant_id: ID of the participant
            user_id: ID of the requesting user
            data: Dictionary with fields to update
            
        Returns:
            Participant object or None if not found / no permission
        """
        participant = Participant.query.get(participant_id)
        
        if not participant:
            return None
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check permission through workshop
        workshop = participant.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None
        
        # Update fields
        if 'name' in data:
            participant.name = data['name']
        if 'extra_data' in data:
            participant.extra_data = data['extra_data']
        
        db.session.commit()
        
        return participant
    
    @staticmethod
    def delete_participant(participant_id, user_id):
        """
        Delete a participant.
        
        Args:
            participant_id: ID of the participant
            user_id: ID of the requesting user
            
        Returns:
            True if deleted, False if not found / no permission
        """
        participant = Participant.query.get(participant_id)
        
        if not participant:
            return False
        
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Check permission through workshop
        workshop = participant.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return False
        
        db.session.delete(participant)
        db.session.commit()
        
        return True

"""Observation service layer for business logic.

This service handles all observation-related operations including
observation initialization, answer processing, and data persistence.
"""
from app import db
from app.models.observation import ObservationalRecord
from app.models.session import Session
from app.models.participant import Participant
from app.models.workshop import Workshop
from app.models.user import User


class ObservationService:
    """Observation business logic layer."""
    
    @staticmethod
    def validate_observation_context(session_id, participant_id, user_id):
        """
        Validate that session and participant exist and belong to same workshop.
        Also checks user permissions.
        
        Args:
            session_id: ID of the session
            participant_id: ID of the participant
            user_id: ID of the requesting user
            
        Returns:
            Tuple of (session, participant, error_message)
            If error, session and participant will be None
        """
        session_obj = Session.query.get(session_id)
        if not session_obj:
            return None, None, 'Sesión no encontrada'
        
        participant = Participant.query.get(participant_id)
        if not participant:
            return None, None, 'Participante no encontrado'
        
        # Verify participant belongs to same workshop as session
        if participant.workshop_id != session_obj.workshop_id:
            return None, None, 'El participante no pertenece al taller de esta sesión'
        
        # Check user permissions
        user = User.query.get(user_id)
        if not user:
            return None, None, 'Usuario no encontrado'
        
        workshop = session_obj.workshop
        if not user.is_admin() and workshop.user_id != user_id:
            return None, None, 'No tienes permiso para crear observaciones en este taller'
        
        return session_obj, participant, None
    
    @staticmethod
    def initialize_observation(session_id, participant_id, user_id):
        """
        Initialize observation data for a new observation session.
        Gets previous observation if exists for pre-filling.
        
        Args:
            session_id: ID of the session
            participant_id: ID of the participant
            user_id: ID of the requesting user
            
        Returns:
            Tuple of (observation_data: dict or None, error_message: str or None)
            observation_data contains: session_id, participant_id, answers, 
            current_index, is_redo, previous_version
        """
        # Validate context
        session_obj, participant, error = ObservationService.validate_observation_context(
            session_id, participant_id, user_id
        )
        
        if error:
            return None, error
        
        # Check for existing observations and get the latest one
        latest_observation = ObservationalRecord.query.filter_by(
            session_id=session_id,
            participant_id=participant_id
        ).order_by(ObservationalRecord.version.desc()).first()
        
        # Pre-fill answers from latest observation if it exists
        previous_answers = latest_observation.answers if latest_observation else {}
        is_redo = latest_observation is not None
        previous_version = latest_observation.version if latest_observation else 0
        
        # Create observation data dictionary
        observation_data = {
            'session_id': session_id,
            'participant_id': participant_id,
            'answers': previous_answers.copy(),  # Start with previous answers
            'current_index': 0,
            'is_redo': is_redo,
            'previous_version': previous_version
        }
        
        return observation_data, None
    
    @staticmethod
    def process_answer(observation_data, question_id, answer):
        """
        Process an answer and update observation data.
        
        Args:
            observation_data: Current observation data dictionary
            question_id: ID of the question being answered
            answer: Answer value
            
        Returns:
            Updated observation_data dictionary
        """
        if not observation_data:
            return None
        
        # Store answer
        observation_data['answers'][question_id] = answer
        observation_data['current_index'] += 1
        
        return observation_data
    
    @staticmethod
    def save_observation(observation_data, freeform_notes, user_id):
        """
        Save completed observation to database.
        
        Args:
            observation_data: Observation data dictionary from session
            freeform_notes: Optional freeform notes
            user_id: ID of the user saving the observation
            
        Returns:
            Tuple of (record: ObservationalRecord or None, error_message: str or None)
        """
        if not observation_data:
            return None, 'Datos de observación no encontrados'
        
        session_id = observation_data.get('session_id')
        participant_id = observation_data.get('participant_id')
        
        # Validate context again (user might have lost permissions)
        session_obj, participant, error = ObservationService.validate_observation_context(
            session_id, participant_id, user_id
        )
        
        if error:
            return None, error
        
        # Calculate the next version number
        next_version = observation_data.get('previous_version', 0) + 1
        
        # Create observational record with version
        record = ObservationalRecord(
            session_id=session_id,
            participant_id=participant_id,
            answers=observation_data['answers'],
            freeform_notes=freeform_notes if freeform_notes else None,
            version=next_version
        )
        
        db.session.add(record)
        db.session.commit()
        
        return record, None
    
    @staticmethod
    def get_workshop_observations(workshop_id, user_id):
        """
        Get all observations for a workshop with permission check.
        
        Args:
            workshop_id: ID of the workshop
            user_id: ID of the requesting user
            
        Returns:
            Tuple of (observations: list or None, error_message: str or None)
        """
        workshop = Workshop.query.get(workshop_id)
        if not workshop:
            return None, 'Taller no encontrado'
        
        # Check user permissions
        user = User.query.get(user_id)
        if not user:
            return None, 'Usuario no encontrado'
        
        if not user.is_admin() and workshop.user_id != user_id:
            return None, 'No tienes permiso para ver las observaciones de este taller'
        
        # Get all observations for sessions in this workshop
        observations = db.session.query(ObservationalRecord).join(
            ObservationalRecord.session
        ).filter(
            Session.workshop_id == workshop_id
        ).order_by(ObservationalRecord.created_at.desc()).all()
        
        return observations, None
    
    @staticmethod
    def get_observation(observation_id, user_id):
        """
        Get single observation with permission check.
        
        Args:
            observation_id: ID of the observation
            user_id: ID of the requesting user
            
        Returns:
            Tuple of (observation: ObservationalRecord or None, error_message: str or None)
        """
        observation = ObservationalRecord.query.get(observation_id)
        
        if not observation:
            return None, 'Observación no encontrada'
        
        # Check permissions through workshop
        session_obj = observation.session
        workshop = session_obj.workshop
        
        user = User.query.get(user_id)
        if not user:
            return None, 'Usuario no encontrado'
        
        if not user.is_admin() and workshop.user_id != user_id:
            return None, 'No tienes permiso para ver esta observación'
        
        return observation, None
    
    @staticmethod
    def delete_observation(observation_id, user_id):
        """
        Delete an observation with permission check.
        
        Args:
            observation_id: ID of the observation
            user_id: ID of the requesting user
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        observation = ObservationalRecord.query.get(observation_id)
        
        if not observation:
            return False, 'Observación no encontrada'
        
        # Check permissions through workshop
        session_obj = observation.session
        workshop = session_obj.workshop
        
        user = User.query.get(user_id)
        if not user:
            return False, 'Usuario no encontrado'
        
        if not user.is_admin() and workshop.user_id != user_id:
            return False, 'No tienes permiso para eliminar esta observación'
        
        db.session.delete(observation)
        db.session.commit()
        
        return True, None
    
    @staticmethod
    def get_latest_observation(session_id, participant_id):
        """
        Get the latest observation for a participant-session combination.
        
        Args:
            session_id: ID of the session
            participant_id: ID of the participant
            
        Returns:
            ObservationalRecord or None
        """
        return ObservationalRecord.query.filter_by(
            session_id=session_id,
            participant_id=participant_id
        ).order_by(ObservationalRecord.version.desc()).first()
    
    @staticmethod
    def get_observation_count(session_id, participant_id):
        """
        Get the count of observations for a participant-session combination.
        
        Args:
            session_id: ID of the session
            participant_id: ID of the participant
            
        Returns:
            int: Number of observations
        """
        return ObservationalRecord.query.filter_by(
            session_id=session_id,
            participant_id=participant_id
        ).count()

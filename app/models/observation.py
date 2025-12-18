"""Observational record model."""
from datetime import datetime
from app import db


class ObservationalRecord(db.Model):
    """Observational record - captures therapeutic observations for a participant in a session."""
    
    __tablename__ = 'observational_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    
    # Version number for tracking observation history (1, 2, 3, etc.)
    # Allows multiple observations for the same participant-session combination
    version = db.Column(db.Integer, nullable=False, default=1)
    
    # JSON field storing question ID -> answer mappings
    # Example: {"entry_on_time": "yes", "entry_resistance": "no", ...}
    answers = db.Column(db.JSON, nullable=False, default=dict)
    
    # Freeform observation notes
    freeform_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(datetime.UTC), nullable=False)
    
    def __repr__(self):
        return f'<ObservationalRecord {self.id} - Session {self.session_id}, Participant {self.participant_id}, v{self.version}>'
    
    def get_answer(self, question_id):
        """Get the answer for a specific question."""
        return self.answers.get(question_id) if self.answers else None
    
    @staticmethod
    def get_latest_version(session_id, participant_id):
        """Get the latest version number for a participant-session combination."""
        latest = ObservationalRecord.query.filter_by(
            session_id=session_id,
            participant_id=participant_id
        ).order_by(ObservationalRecord.version.desc()).first()
        return latest.version if latest else 0
    
    @staticmethod
    def has_observation(session_id, participant_id):
        """Check if an observation exists for this participant-session combination."""
        return ObservationalRecord.query.filter_by(
            session_id=session_id,
            participant_id=participant_id
        ).first() is not None

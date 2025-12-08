"""Observational record model."""
from datetime import datetime
from app import db


class ObservationalRecord(db.Model):
    """Observational record - captures therapeutic observations for a participant in a session."""
    
    __tablename__ = 'observational_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    
    # JSON field storing question ID -> answer mappings
    # Example: {"entry_on_time": "yes", "entry_resistance": "no", ...}
    answers = db.Column(db.JSON, nullable=False, default=dict)
    
    # Freeform observation notes
    freeform_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ObservationalRecord {self.id} - Session {self.session_id}, Participant {self.participant_id}>'
    
    def get_answer(self, question_id):
        """Get the answer for a specific question."""
        return self.answers.get(question_id) if self.answers else None

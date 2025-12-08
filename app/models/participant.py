"""Participant model."""
from datetime import datetime
from app import db


class Participant(db.Model):
    """Participant entity - people who attend workshops."""
    
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # JSON field for future extensibility (e.g., age, contact, notes)
    extra_data = db.Column(db.JSON, nullable=True)
    
    # Relationship to observational records
    observations = db.relationship(
        'ObservationalRecord',
        backref='participant',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f'<Participant {self.name}>'

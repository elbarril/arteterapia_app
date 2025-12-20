"""Participant model."""
from datetime import datetime, timezone
from app import db


class Participant(db.Model):
    """Participant entity - people who attend workshops."""
    
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # JSON field for future extensibility (e.g., age, contact, notes)
    extra_data = db.Column(db.JSON, nullable=True)
    
    # Relationship to observational records
    observations = db.relationship(
        'ObservationalRecord',
        backref='participant',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        """Convert participant to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'workshop_id': self.workshop_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'extra_data': self.extra_data or {}
        }
    
    def __repr__(self):
        return f'<Participant {self.name}>'

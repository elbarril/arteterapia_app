"""Session model."""
from datetime import datetime, timezone
from app import db


class Session(db.Model):
    """Session entity - therapeutic sessions within a workshop."""
    
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    motivation = db.Column(db.Text, nullable=True)
    materials = db.Column(db.JSON, nullable=True)  # Array of material names
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to observational records
    observations = db.relationship(
        'ObservationalRecord',
        backref='session',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    @property
    def has_observations(self):
        """Check if this session has any observational records."""
        return self.observations.count() > 0
    
    @property
    def observation_count(self):
        """Return the count of observations for this session."""
        return self.observations.count()
    
    def has_observation_for(self, participant_id):
        """Check if this session has an observation for a specific participant."""
        return self.observations.filter_by(participant_id=participant_id).first() is not None
    
    def get_observation_count_for(self, participant_id):
        """Get the number of observation versions for a specific participant."""
        return self.observations.filter_by(participant_id=participant_id).count()
    
    def to_dict(self):
        """Convert session to dictionary for API responses."""
        return {
            'id': self.id,
            'workshop_id': self.workshop_id,
            'prompt': self.prompt,
            'motivation': self.motivation,
            'materials': self.materials or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_observations': self.has_observations,
            'observation_count': self.observation_count
        }
    
    def __repr__(self):
        return f'<Session {self.id} - {self.prompt[:30]}>'

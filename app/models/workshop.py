"""Workshop model."""
from datetime import datetime
from app import db


class Workshop(db.Model):
    """Workshop entity - the central concept of the application."""
    
    __tablename__ = 'workshops'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    objective = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships with cascade delete
    participants = db.relationship(
        'Participant',
        backref='workshop',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    sessions = db.relationship(
        'Session',
        backref='workshop',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    @property
    def participant_count(self):
        """Return the count of participants in this workshop."""
        return self.participants.count()
    
    @property
    def session_count(self):
        """Return the count of sessions in this workshop."""
        return self.sessions.count()
    
    @property
    def has_observations(self):
        """Check if this workshop has any observational records."""
        from app.models.observation import ObservationalRecord
        return db.session.query(ObservationalRecord).join(
            ObservationalRecord.session
        ).filter(
            db.session.query(db.session.query(ObservationalRecord).filter(
                ObservationalRecord.session.has(workshop_id=self.id)
            ).exists()).scalar()
        )
    
    def __repr__(self):
        return f'<Workshop {self.name}>'

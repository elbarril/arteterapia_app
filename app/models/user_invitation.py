"""User invitation model for invitation-based registration."""
from datetime import datetime, timedelta, timezone
import secrets
from app import db


class UserInvitation(db.Model):
    """User invitation entity for secure invitation-based registration."""
    
    __tablename__ = 'user_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, email, created_by_user_id, expiry_days=7):
        """Initialize invitation with auto-generated token and expiry."""
        self.email = email
        self.created_by_user_id = created_by_user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=expiry_days)
    
    def is_valid(self):
        """Check if invitation is valid (not used and not expired)."""
        if self.used_at is not None:
            return False
        # Make expires_at timezone-aware if it's naive (SQLite doesn't store timezone)
        expires_at = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        if datetime.now(timezone.utc) > expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """Mark invitation as used."""
        self.used_at = datetime.now(timezone.utc)
    
    @property
    def status(self):
        """Get the current status of the invitation."""
        if self.used_at:
            return 'used'
        # Make expires_at timezone-aware if it's naive (SQLite doesn't store timezone)
        expires_at = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        if datetime.now(timezone.utc) > expires_at:
            return 'expired'
        return 'pending'
    
    def __repr__(self):
        return f'<UserInvitation {self.email} - {self.status}>'

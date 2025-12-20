"""Tests for UserInvitation model."""
import pytest
from datetime import datetime, timedelta, timezone
from app.models.user_invitation import UserInvitation


class TestUserInvitationModel:
    """Tests for UserInvitation model basic functionality."""
    
    def test_create_invitation(self, db, admin_user):
        """Test creating a new user invitation."""
        invitation = UserInvitation(
            email='newuser@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.id is not None
        assert invitation.email == 'newuser@example.com'
        assert invitation.created_by_user_id == admin_user.id
        assert invitation.token is not None
        assert len(invitation.token) > 20  # URL-safe tokens are reasonably long
        assert invitation.created_at is not None
        assert invitation.expires_at is not None
        assert invitation.used_at is None
    
    def test_invitation_repr(self, db, admin_user):
        """Test invitation string representation."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert 'test@example.com' in repr(invitation)
        assert invitation.status in repr(invitation)
    
    def test_invitation_auto_generates_token(self, db, admin_user):
        """Test that token is automatically generated."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        
        assert invitation.token is not None
        assert len(invitation.token) > 0
    
    def test_invitation_tokens_are_unique(self, db, admin_user):
        """Test that each invitation gets a unique token."""
        inv1 = UserInvitation(email='user1@example.com', created_by_user_id=admin_user.id)
        inv2 = UserInvitation(email='user2@example.com', created_by_user_id=admin_user.id)
        db.session.add_all([inv1, inv2])
        db.session.commit()
        
        assert inv1.token != inv2.token


class TestUserInvitationExpiry:
    """Tests for UserInvitation expiry functionality."""
    
    def test_default_expiry_7_days(self, db, admin_user):
        """Test that invitations expire after 7 days by default."""
        before = datetime.now(timezone.utc)
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        after = datetime.now(timezone.utc)
        
        # Make expires_at timezone-aware if needed
        expires_at = invitation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        expected_min = before + timedelta(days=7)
        expected_max = after + timedelta(days=7)
        
        assert expected_min <= expires_at <= expected_max
    
    def test_custom_expiry(self, db, admin_user):
        """Test invitation with custom expiry days."""
        before = datetime.now(timezone.utc)
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id,
            expiry_days=14
        )
        after = datetime.now(timezone.utc)
        
        # Make expires_at timezone-aware if needed
        expires_at = invitation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        expected_min = before + timedelta(days=14)
        expected_max = after + timedelta(days=14)
        
        assert expected_min <= expires_at <= expected_max


class TestUserInvitationValidation:
    """Tests for UserInvitation validation functionality."""
    
    def test_is_valid_new_invitation(self, db, admin_user):
        """Test that new invitation is valid."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.is_valid() is True
    
    def test_is_valid_used_invitation(self, db, admin_user):
        """Test that used invitation is not valid."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        invitation.mark_as_used()
        db.session.commit()
        
        assert invitation.is_valid() is False
    
    def test_is_valid_expired_invitation(self, db, admin_user):
        """Test that expired invitation is not valid."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id,
            expiry_days=0
        )
        # Manually set expiry to past
        invitation.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.is_valid() is False


class TestUserInvitationMarkAsUsed:
    """Tests for UserInvitation mark_as_used functionality."""
    
    def test_mark_as_used(self, db, admin_user):
        """Test marking invitation as used."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.used_at is None
        
        invitation.mark_as_used()
        db.session.commit()
        
        assert invitation.used_at is not None
        assert isinstance(invitation.used_at, datetime)
    
    def test_mark_as_used_sets_current_time(self, db, admin_user):
        """Test that mark_as_used sets current timestamp."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        before = datetime.now(timezone.utc)
        invitation.mark_as_used()
        after = datetime.now(timezone.utc)
        
        # Make used_at timezone-aware if needed
        used_at = invitation.used_at
        if used_at.tzinfo is None:
            used_at = used_at.replace(tzinfo=timezone.utc)
        
        assert before <= used_at <= after


class TestUserInvitationStatus:
    """Tests for UserInvitation status property."""
    
    def test_status_pending(self, db, admin_user):
        """Test status for pending invitation."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.status == 'pending'
    
    def test_status_used(self, db, admin_user):
        """Test status for used invitation."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        invitation.mark_as_used()
        db.session.commit()
        
        assert invitation.status == 'used'
    
    def test_status_expired(self, db, admin_user):
        """Test status for expired invitation."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id,
            expiry_days=0
        )
        # Manually set expiry to past
        invitation.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.status == 'expired'


class TestUserInvitationRelationships:
    """Tests for UserInvitation relationships."""
    
    def test_invitation_creator_relationship(self, db, admin_user):
        """Test invitation-creator relationship."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation.creator == admin_user
    
    def test_user_invitations_created_relationship(self, db, admin_user):
        """Test user-invitations_created relationship."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=admin_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        assert invitation in admin_user.invitations_created.all()


class TestUserInvitationConstraints:
    """Tests for UserInvitation constraints."""
    
    def test_invitation_requires_email(self, db, admin_user):
        """Test that invitation requires an email."""
        invitation = UserInvitation(
            email=None,
            created_by_user_id=admin_user.id
        )
        
        with pytest.raises(Exception):  # TypeError or validation error
            db.session.add(invitation)
            db.session.commit()
    
    def test_invitation_requires_creator(self, db):
        """Test that invitation requires a creator."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=None
        )
        
        with pytest.raises(Exception):  # TypeError or validation error
            db.session.add(invitation)
            db.session.commit()
    
    @pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
    def test_invitation_invalid_creator_id(self, db):
        """Test that invitation requires valid creator_id."""
        invitation = UserInvitation(
            email='test@example.com',
            created_by_user_id=99999
        )
        db.session.add(invitation)
        
        with pytest.raises(Exception):  # IntegrityError (foreign key)
            db.session.commit()
    
    def test_invitation_unique_token(self, db, admin_user):
        """Test that invitation tokens must be unique."""
        inv1 = UserInvitation(email='user1@example.com', created_by_user_id=admin_user.id)
        db.session.add(inv1)
        db.session.commit()
        
        # Try to create another invitation with same token
        inv2 = UserInvitation(email='user2@example.com', created_by_user_id=admin_user.id)
        inv2.token = inv1.token  # Force same token
        db.session.add(inv2)
        
        with pytest.raises(Exception):  # IntegrityError (unique constraint)
            db.session.commit()

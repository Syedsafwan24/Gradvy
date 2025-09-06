"""
User management service layer.

Handles user creation, profile management, and user-related operations.
"""

from typing import Dict, Optional
import logging
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from ..models import UserProfile

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """Service for handling user management operations."""
    
    @staticmethod
    @transaction.atomic
    def create_user(email: str, password: str, **extra_fields) -> User:
        """
        Create a new user with profile.
        
        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional user fields
            
        Returns:
            User: Created user instance
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            **extra_fields
        )
        
        # Profile is created automatically via signals
        logger.info(f"User created: {user.email}")
        return user
    
    @staticmethod
    @transaction.atomic
    def create_superuser(email: str, password: str, **extra_fields) -> User:
        """
        Create a new superuser.
        
        Args:
            email: Superuser's email address
            password: Superuser's password
            **extra_fields: Additional user fields
            
        Returns:
            User: Created superuser instance
        """
        user = User.objects.create_superuser(
            email=email,
            password=password,
            **extra_fields
        )
        
        logger.info(f"Superuser created: {user.email}")
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def update_user_profile(user: User, profile_data: Dict) -> UserProfile:
        """
        Update user profile information.
        
        Args:
            user: User instance
            profile_data: Profile data to update
            
        Returns:
            UserProfile: Updated profile instance
        """
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        for field, value in profile_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        profile.save()
        
        if created:
            logger.info(f"Profile created for user: {user.email}")
        else:
            logger.info(f"Profile updated for user: {user.email}")
        
        return profile
    
    @staticmethod
    def change_password(user: User, new_password: str) -> bool:
        """
        Change user password and update related fields.
        
        Args:
            user: User instance
            new_password: New password
            
        Returns:
            bool: True if password was changed successfully
        """
        try:
            user.set_password(new_password)
            user.must_change_password = False
            user.last_password_change = timezone.now()
            user.save()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to change password for user {user.email}: {e}")
            return False
    
    @staticmethod
    def deactivate_user(user: User) -> bool:
        """
        Deactivate user account.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user was deactivated successfully
        """
        try:
            user.is_active = False
            user.save()
            
            logger.info(f"User deactivated: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate user {user.email}: {e}")
            return False
    
    @staticmethod
    def activate_user(user: User) -> bool:
        """
        Activate user account.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user was activated successfully
        """
        try:
            user.is_active = True
            user.save()
            
            logger.info(f"User activated: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate user {user.email}: {e}")
            return False
    
    @staticmethod
    def get_user_stats() -> Dict:
        """
        Get user statistics.
        
        Returns:
            Dict: User statistics
        """
        return {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'superuser_count': User.objects.filter(is_superuser=True).count(),
            'mfa_enabled_users': User.objects.filter(mfa_enrolled=True).count(),
        }
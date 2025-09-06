"""
Custom user manager for Gradvy authentication system.
"""

from typing import Any, Optional
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    
    Provides methods to create users and superusers with email as the unique identifier
    instead of username.
    """
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> 'User':
        """
        Create and return a regular user with the given email and password.
        
        Args:
            email (str): The user's email address
            password (Optional[str]): The user's password (can be None for unusable password)
            **extra_fields (Any): Additional fields for the user
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> 'User':
        """
        Create and return a superuser with the given email and password.
        
        Args:
            email (str): The superuser's email address
            password (Optional[str]): The superuser's password
            **extra_fields (Any): Additional fields for the user
            
        Returns:
            User: The created superuser instance
            
        Raises:
            ValueError: If email is not provided or required superuser fields are not set
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('must_change_password', False)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

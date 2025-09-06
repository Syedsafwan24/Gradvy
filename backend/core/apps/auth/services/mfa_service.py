"""
Multi-Factor Authentication service layer.

Handles MFA operations including TOTP device management,
QR code generation, and backup code operations.
"""

from typing import List, Dict, Optional, Tuple
import os
import base64
import qrcode
import logging
from io import BytesIO
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import get_user_model
from ..models import BackupCode
from ..utils import generate_backup_codes

logger = logging.getLogger(__name__)
User = get_user_model()


class MFAService:
    """Service for handling Multi-Factor Authentication operations."""
    
    @staticmethod
    def generate_totp_secret() -> Tuple[str, str]:
        """
        Generate TOTP secret for MFA enrollment.
        
        Returns:
            Tuple[str, str]: (base32_secret, hex_secret)
        """
        raw_secret_bytes = os.urandom(20)  # 20 bytes for a 160-bit key
        base32_secret = base64.b32encode(raw_secret_bytes).decode('utf-8')
        hex_secret = raw_secret_bytes.hex()
        
        return base32_secret, hex_secret
    
    @staticmethod
    def generate_qr_code(user_email: str, secret: str, issuer: str = "Gradvy") -> str:
        """
        Generate QR code for TOTP setup.
        
        Args:
            user_email: User's email address
            secret: Base32 encoded secret
            issuer: Service name for TOTP app
            
        Returns:
            str: Base64 encoded QR code image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"otpauth://totp/{user_email}?secret={secret}&issuer={issuer}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, kind='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def create_totp_device(user, hex_secret: str) -> TOTPDevice:
        """Create unconfirmed TOTP device for user."""
        return TOTPDevice.objects.create(
            user=user,
            key=hex_secret,
            confirmed=False
        )
    
    @staticmethod
    def confirm_totp_device(device: TOTPDevice, code: str) -> bool:
        """
        Confirm TOTP device with verification code.
        
        Args:
            device: TOTP device to confirm
            code: 6-digit verification code
            
        Returns:
            bool: True if code is valid and device confirmed
        """
        if device.verify_token(code):
            device.confirmed = True
            device.save()
            return True
        return False
    
    @staticmethod
    def enroll_mfa(user) -> Dict:
        """
        Complete MFA enrollment process.
        
        Returns:
            Dict: Enrollment data with secret, QR code, and backup codes
        """
        base32_secret, hex_secret = MFAService.generate_totp_secret()
        device = MFAService.create_totp_device(user, hex_secret)
        qr_code = MFAService.generate_qr_code(user.email, base32_secret)
        backup_codes = generate_backup_codes(user)
        
        return {
            'secret': base32_secret,
            'qr_code': f"data:image/png;base64,{qr_code}",
            'backup_codes': backup_codes,
            'device_id': device.id
        }
    
    @staticmethod
    def verify_mfa_code(user, code: str) -> bool:
        """
        Verify MFA code for authenticated user.
        
        Args:
            user: User instance
            code: 6-digit verification code
            
        Returns:
            bool: True if code is valid
        """
        totp_devices = devices_for_user(user, confirmed=True)
        for device in totp_devices:
            if device.verify_token(code):
                return True
        return False
    
    @staticmethod
    def disable_mfa(user) -> bool:
        """
        Disable MFA for user by removing all confirmed TOTP devices.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if MFA was successfully disabled
        """
        try:
            TOTPDevice.objects.filter(user=user, confirmed=True).delete()
            user.mfa_enrolled = False
            user.save()
            return True
        except Exception as e:
            logger.error(f"Failed to disable MFA for user {user.id}: {e}")
            return False
    
    @staticmethod
    def get_user_totp_devices(user) -> List[TOTPDevice]:
        """Get all confirmed TOTP devices for user."""
        return list(devices_for_user(user, confirmed=True))
    
    @staticmethod
    def has_mfa_enabled(user) -> bool:
        """Check if user has MFA enabled."""
        return user.mfa_enrolled and len(MFAService.get_user_totp_devices(user)) > 0
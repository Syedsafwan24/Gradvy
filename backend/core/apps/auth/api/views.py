from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.core.exceptions import PermissionDenied, ValidationError
from axes.exceptions import AxesBackendPermissionDenied
import logging
from .serializers import *
from ..models import User, PasswordResetToken, UserSession, AuthEvent
from ..utils.utils import log_auth_event, generate_backup_codes
from ..utils.device_detection import get_session_info
import qrcode
import base64
from io import BytesIO
import os
from django.utils import timezone
import jwt
from django.conf import settings
from datetime import timedelta
import secrets
import string

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)

            # Check if MFA is required
            if user.mfa_enrolled:
                # Create a temporary MFA token instead of using sessions
                mfa_payload = {
                    'user_id': user.id,
                    'mfa_pending': True,
                    'remember_me': remember_me,  # Store remember_me for after MFA
                    'exp': timezone.now().timestamp() + 300,  # 5 minutes expiry
                    'iat': timezone.now().timestamp(),
                }
                mfa_token = jwt.encode(mfa_payload, settings.SECRET_KEY, algorithm='HS256')
                
                # Log successful authentication (pending MFA)
                log_auth_event(user, 'login_mfa_required', request, success=True)
                
                return Response({
                    'mfa_required': True,
                    'mfa_token': mfa_token,
                    'message': 'MFA verification required'
                }, status=status.HTTP_200_OK)

            # No MFA required, proceed with login
            return self._complete_login(request, user, remember_me)
            
        except AxesBackendPermissionDenied:
            # This is raised by django-axes when user is locked out
            return Response({
                'detail': 'Account temporarily locked due to too many failed login attempts. Please try again later.',
                'error_code': 'ACCOUNT_LOCKED'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        except ValidationError as e:
            # Log failed attempt - axes middleware will handle counting failures
            email = getattr(request.data, 'get', lambda x, default: default)('email', 'unknown')
            try:
                user = User.objects.get(email=email)
                log_auth_event(user, 'login_failed', request, success=False)
            except User.DoesNotExist:
                logger.warning(f"Login attempt with non-existent email: {email}")
            
            return Response({
                'detail': 'Invalid email or password.',
                'error_code': 'INVALID_CREDENTIALS'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        except PermissionDenied as e:
            return Response({
                'detail': str(e),
                'error_code': 'PERMISSION_DENIED'
            }, status=status.HTTP_403_FORBIDDEN)
            
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return Response({
                'detail': 'An error occurred during login. Please try again.',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _complete_login(self, request, user, remember_me=False):
        # Generate tokens with custom expiry for remember_me
        refresh = RefreshToken.for_user(user)
        
        if remember_me:
            # Extend refresh token lifetime for remember_me
            refresh.set_exp(lifetime=timezone.timedelta(days=30))
        
        access = refresh.access_token

        # Log successful login
        log_auth_event(user, 'login_success', request, success=True)

        response_data = {
            'message': 'Login successful',
            'access': str(access),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Set refresh token as HTTP-only cookie
        cookie_max_age = 30 * 24 * 60 * 60 if remember_me else 7 * 24 * 60 * 60  # 30 days or 7 days
        response.set_cookie(
            'refresh_token',
            str(refresh),
            max_age=cookie_max_age,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )
        
        return response

@method_decorator(csrf_exempt, name='dispatch')
class MFAVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Get MFA token from request data
        mfa_token = request.data.get('mfa_token')
        if not mfa_token:
            return Response({'error': 'No pending authentication'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the MFA token
            mfa_payload = jwt.decode(mfa_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = mfa_payload.get('user_id')
            remember_me = mfa_payload.get('remember_me', False)
            
            if not mfa_payload.get('mfa_pending'):
                return Response({'error': 'Invalid MFA token'}, 
                              status=status.HTTP_400_BAD_REQUEST)
                
        except jwt.ExpiredSignatureError:
            return Response({'error': 'MFA token expired. Please login again.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid MFA token'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']

        # Verify TOTP code
        totp_devices = devices_for_user(user, confirmed=True)
        if not totp_devices:
            return Response({'error': 'No MFA device found'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        for device in totp_devices:
            if device.verify_token(code):
                # MFA successful, complete login with remember_me
                # Log successful MFA verification
                log_auth_event(user, 'mfa_verify', request, success=True)
                
                return self._complete_login(request, user, remember_me)

        # MFA failed
        log_auth_event(user, 'mfa_verify', request, success=False)
        return Response({'error': 'Invalid MFA code'}, 
                      status=status.HTTP_400_BAD_REQUEST)

    def _complete_login(self, request, user, remember_me=False):
        # Generate tokens with custom expiry for remember_me
        refresh = RefreshToken.for_user(user)
        
        if remember_me:
            # Extend refresh token lifetime for remember_me
            refresh.set_exp(lifetime=timezone.timedelta(days=30))
        
        access = refresh.access_token

        # Log successful login
        log_auth_event(user, 'login_success', request, success=True)

        response_data = {
            'message': 'Login successful',
            'access': str(access),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Set refresh token as HTTP-only cookie
        cookie_max_age = 30 * 24 * 60 * 60 if remember_me else 7 * 24 * 60 * 60  # 30 days or 7 days
        response.set_cookie(
            'refresh_token',
            str(refresh),
            max_age=cookie_max_age,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )
        
        return response

@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(views.APIView):
    """Enhanced user profile view with comprehensive update support"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user profile data"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Full profile update (replace all fields)"""
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Return updated user data
            response_serializer = UserSerializer(user)
            log_auth_event(user, 'profile_updated', request, success=True, 
                         details={'updated_fields': list(request.data.keys())})
            return Response(response_serializer.data)
        
        log_auth_event(request.user, 'profile_update_failed', request, success=False, 
                      details={'errors': serializer.errors})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Partial profile update (update only provided fields)"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            # Return updated user data
            response_serializer = UserSerializer(user)
            log_auth_event(user, 'profile_updated', request, success=True, 
                         details={'updated_fields': list(request.data.keys())})
            return Response(response_serializer.data)
        
        log_auth_event(request.user, 'profile_update_failed', request, success=False, 
                      details={'errors': serializer.errors})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PasswordChangeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.must_change_password = False
            user.last_password_change = timezone.now()
            user.save()

            # Log password change
            log_auth_event(user, 'password_change', request, success=True)

            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class MFAEnrollmentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # Generate TOTP secret (raw bytes)
        raw_secret_bytes = os.urandom(20) # 20 bytes for a 160-bit key

        # Base32 encode for the QR code URI and for returning to frontend
        base32_secret = base64.b32encode(raw_secret_bytes).decode('utf-8')

        # Hex encode for storing in the database (as django-otp expects a hex string in its CharField)
        hex_secret = raw_secret_bytes.hex()

        # Create TOTP device - store the hex string
        device = TOTPDevice.objects.create(
            user=user,
            key=hex_secret, # Store hex string
            confirmed=False
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"otpauth://totp/{user.email}?secret={base32_secret}&issuer=Gradvy")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, kind='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        # Generate backup codes
        backup_codes = generate_backup_codes(user)

        return Response({
            'secret': base32_secret, # Return base32 secret to frontend
            'qr_code': f"data:image/png;base64,{qr_code}",
            'backup_codes': backup_codes,
            'device_id': device.id
        })

    def put(self, request):
        """Confirm MFA enrollment"""
        device_id = request.data.get('device_id')
        
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        try:
            device = TOTPDevice.objects.get(id=device_id, user=request.user)
        except TOTPDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        is_valid = device.verify_token(code)

        if is_valid:
            device.confirmed = True
            device.save()

            request.user.mfa_enrolled = True
            request.user.save()
            
            # Log MFA enrollment
            log_auth_event(request.user, 'mfa_enroll', request, success=True)

            return Response({'message': 'MFA enrolled successfully'})

        return Response({'error': 'Invalid code'}, 
                      status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CookieTokenRefreshView(views.APIView):
    """
    Custom token refresh view that uses httpOnly cookies instead of request body
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            # Get refresh token from httpOnly cookie
            refresh_token_str = request.COOKIES.get('refresh_token')
            
            if not refresh_token_str:
                return Response({
                    'detail': 'Refresh token not found in cookies',
                    'error_code': 'NO_REFRESH_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                # Validate and refresh the token
                refresh_token = RefreshToken(refresh_token_str)
                new_access_token = str(refresh_token.access_token)
                
                # Check if token rotation is enabled (it is by default in settings)
                if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False):
                    # Generate new refresh token
                    new_refresh_token = str(refresh_token)
                    refresh_token.blacklist()  # Blacklist the old token
                    
                    response_data = {
                        'access': new_access_token,
                        'message': 'Token refreshed successfully'
                    }
                    
                    response = Response(response_data, status=status.HTTP_200_OK)
                    
                    # Set new refresh token as httpOnly cookie
                    response.set_cookie(
                        'refresh_token',
                        new_refresh_token,
                        max_age=7 * 24 * 60 * 60,  # 7 days
                        httponly=True,
                        secure=not settings.DEBUG,
                        samesite='Lax'
                    )
                else:
                    # No token rotation, just return new access token
                    response_data = {
                        'access': new_access_token,
                        'message': 'Token refreshed successfully'
                    }
                    response = Response(response_data, status=status.HTTP_200_OK)
                
                return response
                
            except TokenError as e:
                return Response({
                    'detail': 'Invalid or expired refresh token',
                    'error_code': 'INVALID_REFRESH_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response({
                'detail': 'Token refresh failed',
                'error_code': 'REFRESH_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # Try to get refresh token from cookie first, then from request data
            refresh_token_str = request.COOKIES.get('refresh_token')
            if not refresh_token_str:
                refresh_token_str = request.data.get("refresh")
            
            if refresh_token_str:
                token = RefreshToken(refresh_token_str)
                token.blacklist()
            
            log_auth_event(request.user, 'logout', request, success=True)
            
            # Create response and clear authentication cookies
            response = Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
            # Clear authentication cookies
            response.delete_cookie('refresh_token')
            response.delete_cookie('gradvy_sessionid')
            response.delete_cookie('gradvy_csrftoken')
            
            return response
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            # Even if token blacklisting fails, clear cookies and return success
            response = Response({
                'message': 'Logout completed'
            }, status=status.HTTP_200_OK)
            
            # Clear authentication cookies
            response.delete_cookie('refresh_token')
            response.delete_cookie('gradvy_sessionid')
            response.delete_cookie('gradvy_csrftoken')
            
            return response

@method_decorator(csrf_exempt, name='dispatch')
class MFADisableView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            # Delete all confirmed TOTP devices for the user
            TOTPDevice.objects.filter(user=user, confirmed=True).delete()
            
            # Set mfa_enrolled to False
            user.mfa_enrolled = False
            user.save()

            # Trigger background task to clean up all MFA-related data
            from ..tasks.tasks import cleanup_user_mfa_data
            
            # Check if cleanup should be immediate or delayed
            cleanup_immediate = getattr(settings, 'MFA_CLEANUP_ON_DISABLE_IMMEDIATE', True)
            if cleanup_immediate:
                # Run cleanup immediately
                cleanup_user_mfa_data.delay(user.id)
            else:
                # Delay cleanup by 5 minutes to allow for any recovery actions
                cleanup_user_mfa_data.apply_async(args=[user.id], countdown=300)

            # Log MFA disable event
            log_auth_event(user, 'mfa_disable', request, success=True)

            return Response({'message': 'MFA disabled successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_auth_event(user, 'mfa_disable', request, success=False, details={'error': str(e)})
            return Response({'error': 'Failed to disable MFA'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MFABackupCodesView(views.APIView):
    """Manage MFA backup codes - view current codes and regenerate new ones"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current backup codes for the user"""
        user = request.user
        
        if not user.mfa_enrolled:
            return Response({
                'error': 'MFA not enabled',
                'message': 'Multi-factor authentication must be enabled before accessing backup codes',
                'backup_codes': [],
                'count': 0
            }, status=status.HTTP_200_OK)
        
        try:
            # Get user's unused backup codes from the database
            backup_codes = user.backup_codes.filter(used=False).values_list('code', flat=True)
            if not backup_codes:
                # Generate initial backup codes if none exist
                backup_codes = generate_backup_codes(user)
            
            log_auth_event(user, 'backup_codes_viewed', request, success=True)
            
            return Response({
                'backup_codes': list(backup_codes),
                'count': len(backup_codes)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving backup codes for user {user.email}: {str(e)}")
            log_auth_event(user, 'backup_codes_viewed', request, success=False, details={'error': str(e)})
            return Response({'error': 'Failed to retrieve backup codes'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Regenerate backup codes"""
        user = request.user
        
        if not user.mfa_enrolled:
            return Response({'error': 'MFA not enabled'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Delete existing unused backup codes
            user.backup_codes.filter(used=False).delete()
            
            # Generate new backup codes
            new_backup_codes = generate_backup_codes(user)
            
            log_auth_event(user, 'backup_codes_regenerated', request, success=True)
            
            return Response({
                'message': 'Backup codes regenerated successfully',
                'backup_codes': new_backup_codes,
                'count': len(new_backup_codes)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error regenerating backup codes for user {user.email}: {str(e)}")
            log_auth_event(user, 'backup_codes_regenerated', request, success=False, details={'error': str(e)})
            return Response({'error': 'Failed to regenerate backup codes'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MFAStatusView(views.APIView):
    """Get current MFA status and settings for the user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get comprehensive MFA status"""
        user = request.user
        
        try:
            # Check for active TOTP devices
            totp_devices = TOTPDevice.objects.filter(user=user, confirmed=True)
            unused_backup_codes = user.backup_codes.filter(used=False)
            
            status_data = {
                'is_mfa_enabled': user.mfa_enrolled,
                'has_totp_device': totp_devices.exists(),
                'totp_device_count': totp_devices.count(),
                'has_backup_codes': unused_backup_codes.exists(),
                'backup_codes_count': unused_backup_codes.count(),
                'enrollment_date': totp_devices.first().created_at if totp_devices.exists() else None,
            }
            
            return Response(status_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting MFA status for user {user.email}: {str(e)}")
            return Response({'error': 'Failed to get MFA status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegistrationView(views.APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for immediate login after registration
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Get user data
            user_data = UserSerializer(user).data
            
            response_data = {
                'message': 'Registration successful',
                'user': user_data,
                'access': access_token,
                'refresh': refresh_token
            }
            
            response = Response(response_data, status=status.HTTP_201_CREATED)
            
            # Set refresh token as HTTP-only cookie
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7 days
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            
            # Log successful registration
            log_auth_event(user, 'register', request, success=True)
            
            return response
        
        return Response({
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(views.APIView):
    """Password reset request endpoint - creates reset tokens"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Clean up any existing tokens for this user
                PasswordResetToken.objects.filter(user=user).delete()
                
                # Generate secure token
                token = self._generate_reset_token()
                
                # Create new reset token
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
                )
                
                # Log the reset request
                log_auth_event(user, 'password_reset_requested', request, success=True)
                
                # TODO: Send email with token - for now return token for development
                # In production, this would send an email with a link containing the token
                return Response({
                    'message': f'Password reset instructions have been sent to {email}',
                    'token': token,  # Remove this in production - only for development testing
                    'expires_at': reset_token.expires_at,
                    'note': 'Email functionality will be implemented. Token provided for development testing.'
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # Don't reveal if user exists - return same message
                return Response({
                    'message': f'Password reset instructions have been sent to {email}',
                    'note': 'If this email exists in our system, you will receive reset instructions.'
                }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Password reset failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_reset_token(self):
        """Generate a secure random token for password reset"""
        # Generate a secure random token (64 characters)
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))


class PasswordResetConfirmView(views.APIView):
    """Password reset confirmation endpoint - resets password using token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token_obj = serializer.validated_data['token_obj']
            new_password = serializer.validated_data['new_password']
            user = token_obj.user
            
            try:
                # Update user password
                user.set_password(new_password)
                user.must_change_password = False
                user.last_password_change = timezone.now()
                user.save()
                
                # Mark token as used
                token_obj.mark_as_used()
                
                # Log successful password reset
                log_auth_event(user, 'password_reset_confirmed', request, success=True)
                
                # Clean up any other reset tokens for this user
                PasswordResetToken.objects.filter(user=user, used=False).delete()
                
                return Response({
                    'message': 'Password has been reset successfully. You can now login with your new password.',
                    'success': True
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error resetting password for user {user.email}: {str(e)}")
                log_auth_event(user, 'password_reset_confirmed', request, success=False, details={'error': str(e)})
                return Response({
                    'message': 'Failed to reset password. Please try again.',
                    'errors': ['An unexpected error occurred']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'Password reset failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(views.APIView):
    """
    Endpoint to get CSRF token for frontend applications
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return CSRF token"""
        # The @ensure_csrf_cookie decorator ensures the CSRF cookie is set
        csrf_token = get_token(request)
        return Response({
            'csrf_token': csrf_token,
            'message': 'CSRF token generated successfully'
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class UserSessionsView(views.APIView):
    """
    View and manage user sessions
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List all active sessions for the current user"""
        try:
            sessions = UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-last_activity')
            
            sessions_data = []
            current_session_id = None
            
            # Try to identify current session
            current_ip = get_session_info(request)['ip_address']
            current_user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            for session in sessions:
                # Check if this might be the current session
                is_current = (
                    session.ip_address == current_ip and 
                    session.user_agent == current_user_agent and
                    not session.is_expired()
                )
                
                if is_current:
                    current_session_id = session.session_id
                    session.is_current = True
                    session.save(update_fields=['is_current'])
                
                sessions_data.append({
                    'session_id': session.session_id,
                    'device_name': session.get_device_name(),
                    'location': session.get_location_name(),
                    'ip_address': session.ip_address,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'expires_at': session.expires_at,
                    'is_current': is_current,
                    'is_expired': session.is_expired()
                })
            
            return Response({
                'sessions': sessions_data,
                'current_session_id': current_session_id,
                'total_count': len(sessions_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving sessions for user {request.user.email}: {str(e)}")
            return Response({
                'error': 'Failed to retrieve sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch') 
class RevokeSessionView(views.APIView):
    """
    Revoke a specific session
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Revoke a session by ID"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({
                'error': 'Session ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = UserSession.objects.get(
                session_id=session_id,
                user=request.user,
                is_active=True
            )
            
            # Revoke the session
            session.revoke(revoked_by='user')
            
            # Log the session revocation
            log_auth_event(
                request.user, 
                'session_revoked', 
                request, 
                success=True,
                details={'session_id': session_id, 'revoked_session_ip': session.ip_address}
            )
            
            # If user revoked their current session, they should be logged out
            is_current_session = session.is_current
            
            return Response({
                'message': 'Session revoked successfully',
                'revoked_current_session': is_current_session
            }, status=status.HTTP_200_OK)
            
        except UserSession.DoesNotExist:
            return Response({
                'error': 'Session not found or already revoked'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error revoking session {session_id} for user {request.user.email}: {str(e)}")
            return Response({
                'error': 'Failed to revoke session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RevokeAllSessionsView(views.APIView):
    """
    Revoke all sessions except current one
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Revoke all sessions except the current one"""
        try:
            # Get current session info to avoid revoking current session
            current_session_info = get_session_info(request)
            current_ip = current_session_info['ip_address']
            current_user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Find all active sessions except potential current one
            sessions_to_revoke = UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).exclude(
                ip_address=current_ip,
                user_agent=current_user_agent
            )
            
            revoked_count = sessions_to_revoke.count()
            
            # Revoke all sessions
            for session in sessions_to_revoke:
                session.revoke(revoked_by='user')
            
            # Log the bulk session revocation
            log_auth_event(
                request.user, 
                'session_revoked', 
                request, 
                success=True,
                details={'action': 'revoke_all', 'revoked_count': revoked_count}
            )
            
            return Response({
                'message': f'Successfully revoked {revoked_count} sessions',
                'revoked_count': revoked_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error revoking all sessions for user {request.user.email}: {str(e)}")
            return Response({
                'error': 'Failed to revoke sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class SessionActivityView(views.APIView):
    """
    View authentication events and session activity
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get recent authentication events for the user"""
        try:
            # Get query parameters
            limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100
            event_type = request.GET.get('event_type')
            
            # Build query
            events_query = AuthEvent.objects.filter(user=request.user)
            
            if event_type:
                events_query = events_query.filter(event_type=event_type)
            
            events = events_query.order_by('-created_at')[:limit]
            
            events_data = []
            for event in events:
                events_data.append({
                    'event_type': event.event_type,
                    'event_type_display': event.get_event_type_display(),
                    'success': event.success,
                    'ip_address': event.ip_address,
                    'created_at': event.created_at,
                    'details': event.details
                })
            
            return Response({
                'events': events_data,
                'total_count': len(events_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving session activity for user {request.user.email}: {str(e)}")
            return Response({
                'error': 'Failed to retrieve session activity'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
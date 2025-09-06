from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, ValidationError
from axes.decorators import axes_dispatch
from axes.exceptions import AxesBackendPermissionDenied
import logging
from .serializers import *
from .models import User  # Using standard TOTPDevice from django-otp
from .utils import log_auth_event, generate_backup_codes
import qrcode
import base64
from io import BytesIO
import os # Added for os.urandom
from django_otp.util import random_hex # Keep if still used elsewhere, but not for secret generation
from django.utils import timezone
import jwt
from django.conf import settings

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

            # Check if MFA is required
            if user.mfa_enrolled:
                # Create a temporary MFA token instead of using sessions
                mfa_payload = {
                    'user_id': user.id,
                    'mfa_pending': True,
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
            return self._complete_login(request, user)
            
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

    def _complete_login(self, request, user):
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Log successful login
        log_auth_event(user, 'login_success', request, success=True)

        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })

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
                # MFA successful, complete login
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                # Log successful MFA verification
                log_auth_event(user, 'mfa_verify', request, success=True)

                return Response({
                    'access': str(access),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                })

        # MFA failed
        log_auth_event(user, 'mfa_verify', request, success=False)
        return Response({'error': 'Invalid MFA code'}, 
                      status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

        # --- DEBUGGING START ---
        print(f"DEBUG: MFA Enroll Confirm - User: {request.user.email}")
        print(f"DEBUG: Device ID: {device_id}")
        print(f"DEBUG: Code received: {code}")
        print(f"DEBUG: Device key: {device.key}")
        print(f"DEBUG: Device digits: {device.digits}")
        print(f"DEBUG: Device step: {device.step}")
        print(f"DEBUG: Server time: {timezone.now()}")
        is_valid = device.verify_token(code)
        print(f"DEBUG: device.verify_token({code}) result: {is_valid}")
        # --- DEBUGGING END ---

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
class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_auth_event(request.user, 'logout', request, success=True)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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

            # Log MFA disable event
            log_auth_event(user, 'mfa_disable', request, success=True)

            return Response({'message': 'MFA disabled successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_auth_event(user, 'mfa_disable', request, success=False, details={'error': str(e)})
            return Response({'error': 'Failed to disable MFA'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
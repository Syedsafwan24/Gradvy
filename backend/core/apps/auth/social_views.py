"""
Social Authentication API Views
RESTful endpoints for social OAuth integration and profile data management
"""

import logging
import secrets
from typing import Dict, Any
from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .social_models import (
    SocialProvider, SocialAccount, SocialAuthEvent, 
    SocialDataCollection, SocialProfileEnrichment
)
from .social_services import SocialAuthService, SocialAuthError
from .models import User

logger = logging.getLogger(__name__)


class SocialAuthInitiateView(APIView):
    """
    Initiate OAuth flow for social authentication
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request: Request) -> Response:
        """
        Start OAuth authentication process
        
        Expected payload:
        {
            "provider": "google|github|linkedin",
            "scopes": ["profile", "email"],  // Optional
            "redirect_uri": "http://localhost:3000/auth/callback",
            "collect_extended_data": true  // Optional
        }
        """
        try:
            provider_name = request.data.get('provider')
            redirect_uri = request.data.get('redirect_uri')
            requested_scopes = request.data.get('scopes', [])
            collect_extended = request.data.get('collect_extended_data', True)
            
            if not provider_name or not redirect_uri:
                return Response({
                    'error': 'Provider and redirect_uri are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                provider = SocialProvider.objects.get(name=provider_name, is_active=True)
            except SocialProvider.DoesNotExist:
                return Response({
                    'error': f'Provider {provider_name} not found or inactive'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate state parameter for CSRF protection
            state = secrets.token_urlsafe(32)
            
            # Determine scopes
            if collect_extended and provider.optional_scopes:
                scopes = provider.default_scopes + provider.optional_scopes
            else:
                scopes = requested_scopes or provider.default_scopes
            
            # Store state and redirect_uri in cache
            cache_key = f"oauth_state_{state}"
            cache.set(cache_key, {
                'provider': provider_name,
                'redirect_uri': redirect_uri,
                'scopes': scopes,
                'collect_extended': collect_extended,
                'initiated_at': timezone.now().isoformat(),
            }, timeout=600)  # 10 minutes
            
            # Generate authorization URL
            auth_service = SocialAuthService()
            handler = auth_service.get_handler(provider_name)
            
            auth_url = handler.get_authorization_url(redirect_uri, state, scopes)
            
            return Response({
                'authorization_url': auth_url,
                'state': state,
                'provider': provider_name,
                'scopes': scopes,
            })
            
        except Exception as e:
            logger.error(f"Failed to initiate social auth: {str(e)}")
            return Response({
                'error': 'Failed to initiate authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAuthCallbackView(APIView):
    """
    Handle OAuth callback and complete authentication
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request: Request) -> Response:
        """
        Complete OAuth authentication
        
        Expected payload:
        {
            "code": "oauth_authorization_code",
            "state": "csrf_state_token",
            "create_account": true  // Optional, for new users
        }
        """
        try:
            authorization_code = request.data.get('code')
            state = request.data.get('state')
            create_account = request.data.get('create_account', True)
            
            if not authorization_code or not state:
                return Response({
                    'error': 'Authorization code and state are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate state parameter
            cache_key = f"oauth_state_{state}"
            oauth_data = cache.get(cache_key)
            
            if not oauth_data:
                return Response({
                    'error': 'Invalid or expired state parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clear state from cache
            cache.delete(cache_key)
            
            provider_name = oauth_data['provider']
            redirect_uri = oauth_data['redirect_uri']
            requested_scopes = oauth_data['scopes']
            
            # Connect social account
            auth_service = SocialAuthService()
            
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Connect to existing user account
                social_account = auth_service.connect_social_account(
                    request.user, provider_name, authorization_code, 
                    redirect_uri, requested_scopes
                )
                
                return Response({
                    'success': True,
                    'action': 'connected',
                    'user_id': request.user.id,
                    'provider': provider_name,
                    'profile_completeness': social_account.profile_data.get('data_completeness', 0),
                    'profile_data': self._sanitize_profile_data(social_account.profile_data),
                })
            
            else:
                # Handle authentication/registration
                handler = auth_service.get_handler(provider_name)
                
                # Get token and profile data
                token_data = handler.exchange_code_for_token(authorization_code, redirect_uri)
                
                if hasattr(handler, 'get_enhanced_profile'):
                    profile_data = handler.get_enhanced_profile(token_data['access_token'])
                else:
                    profile_data = handler.get_user_profile(token_data['access_token'])
                
                provider_user_id = auth_service._extract_user_id(provider_name, profile_data)
                email = profile_data.get('email', '')
                
                # Check for existing social account
                existing_social = SocialAccount.objects.filter(
                    provider__name=provider_name,
                    provider_user_id=provider_user_id
                ).first()
                
                if existing_social:
                    # Login with existing account
                    user = existing_social.user
                    
                    # Update profile data
                    existing_social.access_token = token_data['access_token']
                    existing_social.profile_data = profile_data
                    existing_social.last_sync = timezone.now()
                    existing_social.save()
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'success': True,
                        'action': 'login',
                        'user_id': user.id,
                        'email': user.email,
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh),
                        'provider': provider_name,
                        'profile_data': self._sanitize_profile_data(profile_data),
                    })
                
                elif email:
                    # Check for existing user by email
                    try:
                        user = User.objects.get(email=email)
                        
                        # Connect social account to existing user
                        social_account = auth_service.connect_social_account(
                            user, provider_name, authorization_code,
                            redirect_uri, requested_scopes
                        )
                        
                        # Generate JWT tokens
                        refresh = RefreshToken.for_user(user)
                        
                        return Response({
                            'success': True,
                            'action': 'connected_existing',
                            'user_id': user.id,
                            'email': user.email,
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh),
                            'provider': provider_name,
                            'profile_data': self._sanitize_profile_data(social_account.profile_data),
                        })
                        
                    except User.DoesNotExist:
                        if create_account:
                            # Create new user account
                            user_data = {
                                'email': email,
                                'first_name': profile_data.get('first_name', ''),
                                'last_name': profile_data.get('last_name', ''),
                                'is_active': True,
                            }
                            
                            user = User.objects.create_user(**user_data)
                            
                            # Connect social account
                            social_account = auth_service.connect_social_account(
                                user, provider_name, authorization_code,
                                redirect_uri, requested_scopes
                            )
                            
                            # Generate JWT tokens
                            refresh = RefreshToken.for_user(user)
                            
                            return Response({
                                'success': True,
                                'action': 'registered',
                                'user_id': user.id,
                                'email': user.email,
                                'access_token': str(refresh.access_token),
                                'refresh_token': str(refresh),
                                'provider': provider_name,
                                'profile_data': self._sanitize_profile_data(social_account.profile_data),
                                'requires_onboarding': True,
                            }, status=status.HTTP_201_CREATED)
                        
                        else:
                            return Response({
                                'error': 'Account creation not permitted',
                                'action_required': 'create_account',
                                'profile_preview': self._sanitize_profile_data(profile_data),
                            }, status=status.HTTP_403_FORBIDDEN)
                
                else:
                    return Response({
                        'error': 'No email provided by social provider',
                        'provider': provider_name,
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        except SocialAuthError as e:
            logger.error(f"Social auth error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Unexpected error in social auth callback: {str(e)}")
            return Response({
                'error': 'Authentication failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _sanitize_profile_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from profile data for client response"""
        safe_fields = [
            'name', 'first_name', 'last_name', 'email', 'avatar_url',
            'username', 'bio', 'location', 'website', 'company',
            'data_completeness', 'interests', 'skills'
        ]
        
        return {key: value for key, value in profile_data.items() 
                if key in safe_fields and value}


class SocialAccountsView(APIView):
    """
    Manage user's connected social accounts
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Get user's connected social accounts"""
        social_accounts = SocialAccount.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('provider')
        
        accounts_data = []
        for account in social_accounts:
            accounts_data.append({
                'id': account.id,
                'provider': {
                    'name': account.provider.name,
                    'display_name': account.provider.display_name,
                },
                'username': account.username,
                'email': account.email,
                'profile_completeness': account.profile_data.get('data_completeness', 0),
                'last_sync': account.last_sync,
                'sync_frequency': account.sync_frequency,
                'data_collection_consent': account.data_collection_consent,
                'connected_at': account.created_at,
            })
        
        return Response({
            'social_accounts': accounts_data,
            'total_connected': len(accounts_data),
        })
    
    def delete(self, request: Request) -> Response:
        """Disconnect a social account"""
        account_id = request.data.get('account_id')
        
        if not account_id:
            return Response({
                'error': 'account_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            social_account = SocialAccount.objects.get(
                id=account_id,
                user=request.user,
                is_active=True
            )
            
            # Log disconnection event
            SocialAuthEvent.objects.create(
                user=request.user,
                social_account=social_account,
                provider=social_account.provider,
                event_type='disconnect',
                success=True,
                details={'reason': 'user_requested'}
            )
            
            # Deactivate instead of delete to preserve audit trail
            social_account.is_active = False
            social_account.save()
            
            return Response({
                'success': True,
                'message': 'Social account disconnected successfully'
            })
            
        except SocialAccount.DoesNotExist:
            return Response({
                'error': 'Social account not found'
            }, status=status.HTTP_404_NOT_FOUND)


class SocialDataSyncView(APIView):
    """
    Manually sync social account data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        """Trigger manual sync for a social account"""
        account_id = request.data.get('account_id')
        
        if not account_id:
            return Response({
                'error': 'account_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            social_account = SocialAccount.objects.get(
                id=account_id,
                user=request.user,
                is_active=True
            )
            
            # Check if user has data collection consent
            if not social_account.data_collection_consent:
                return Response({
                    'error': 'Data collection consent required for sync'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Trigger sync
            auth_service = SocialAuthService()
            success = auth_service.sync_social_account(social_account)
            
            if success:
                return Response({
                    'success': True,
                    'last_sync': social_account.last_sync,
                    'profile_completeness': social_account.profile_data.get('data_completeness', 0),
                    'updated_fields': list(social_account.profile_data.keys()),
                })
            else:
                return Response({
                    'error': 'Sync failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except SocialAccount.DoesNotExist:
            return Response({
                'error': 'Social account not found'
            }, status=status.HTTP_404_NOT_FOUND)


class SocialPrivacySettingsView(APIView):
    """
    Manage privacy settings for social data collection
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Get current privacy settings for all social accounts"""
        social_accounts = SocialAccount.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('provider')
        
        privacy_settings = []
        for account in social_accounts:
            data_collections = SocialDataCollection.objects.filter(
                user=request.user,
                provider=account.provider
            )
            
            collections_data = [{
                'type': dc.collection_type,
                'purpose': dc.purpose,
                'consent_status': dc.consent_status,
                'consent_expires': dc.consent_expires_at,
                'data_retention_days': dc.data_retention_days,
            } for dc in data_collections]
            
            privacy_settings.append({
                'provider': account.provider.name,
                'display_name': account.provider.display_name,
                'data_collection_consent': account.data_collection_consent,
                'public_profile_allowed': account.public_profile_allowed,
                'analytics_consent': account.analytics_consent,
                'data_collections': collections_data,
            })
        
        return Response({
            'privacy_settings': privacy_settings
        })
    
    def put(self, request: Request) -> Response:
        """Update privacy settings for a social account"""
        account_id = request.data.get('account_id')
        settings_update = request.data.get('settings', {})
        
        if not account_id:
            return Response({
                'error': 'account_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            social_account = SocialAccount.objects.get(
                id=account_id,
                user=request.user,
                is_active=True
            )
            
            # Update privacy settings
            if 'data_collection_consent' in settings_update:
                social_account.data_collection_consent = settings_update['data_collection_consent']
            
            if 'public_profile_allowed' in settings_update:
                social_account.public_profile_allowed = settings_update['public_profile_allowed']
                
            if 'analytics_consent' in settings_update:
                social_account.analytics_consent = settings_update['analytics_consent']
            
            social_account.save()
            
            # Log consent change event
            SocialAuthEvent.objects.create(
                user=request.user,
                social_account=social_account,
                provider=social_account.provider,
                event_type='consent_granted' if social_account.data_collection_consent else 'consent_revoked',
                success=True,
                details={'settings_updated': list(settings_update.keys())}
            )
            
            return Response({
                'success': True,
                'updated_settings': settings_update,
            })
            
        except SocialAccount.DoesNotExist:
            return Response({
                'error': 'Social account not found'
            }, status=status.HTTP_404_NOT_FOUND)


class SocialProfileEnrichmentView(APIView):
    """
    View enriched profile data from social accounts
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Get enriched profile data for user"""
        enrichments = SocialProfileEnrichment.objects.filter(
            user=request.user
        ).select_related('social_account__provider')
        
        enrichment_data = {}
        
        for enrichment in enrichments:
            enrichment_type = enrichment.enrichment_type
            
            if enrichment_type not in enrichment_data:
                enrichment_data[enrichment_type] = {
                    'sources': [],
                    'combined_data': {},
                    'confidence_scores': [],
                }
            
            enrichment_data[enrichment_type]['sources'].append({
                'provider': enrichment.social_account.provider.name,
                'confidence': enrichment.confidence_score,
                'validated': enrichment.is_validated,
                'last_updated': enrichment.updated_at,
            })
            
            enrichment_data[enrichment_type]['confidence_scores'].append(enrichment.confidence_score)
            
            # Merge enrichment data
            enrichment_data[enrichment_type]['combined_data'].update(enrichment.enrichment_data)
        
        # Calculate overall confidence for each type
        for data in enrichment_data.values():
            if data['confidence_scores']:
                data['overall_confidence'] = sum(data['confidence_scores']) / len(data['confidence_scores'])
            else:
                data['overall_confidence'] = 0.0
        
        return Response({
            'enrichment_data': enrichment_data,
            'total_sources': sum(len(data['sources']) for data in enrichment_data.values()),
            'last_updated': max((e.updated_at for e in enrichments), default=None),
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def social_providers_list(request: Request) -> Response:
    """Get list of available social authentication providers"""
    providers = SocialProvider.objects.filter(is_active=True)
    
    providers_data = [{
        'name': provider.name,
        'display_name': provider.display_name,
        'default_scopes': provider.default_scopes,
        'optional_scopes': provider.optional_scopes,
        'auto_register': provider.auto_register,
        'collect_extended_profile': provider.collect_extended_profile,
    } for provider in providers]
    
    return Response({
        'providers': providers_data,
        'total': len(providers_data),
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_batch_sync(request: Request) -> Response:
    """Trigger batch sync for all user's social accounts"""
    from apps.preferences.tasks import sync_social_accounts_batch
    
    # Get user's active social accounts
    account_ids = list(
        SocialAccount.objects.filter(
            user=request.user,
            is_active=True,
            data_collection_consent=True
        ).values_list('id', flat=True)
    )
    
    if not account_ids:
        return Response({
            'message': 'No social accounts available for sync'
        })
    
    # Trigger batch sync task
    task = sync_social_accounts_batch.delay(account_ids)
    
    return Response({
        'success': True,
        'task_id': task.id,
        'accounts_queued': len(account_ids),
        'message': 'Batch sync initiated'
    })
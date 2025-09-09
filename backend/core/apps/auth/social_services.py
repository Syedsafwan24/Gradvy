"""
Social Authentication Services
OAuth handlers and profile data processors for various social platforms
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlencode, parse_qs
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .social_models import SocialProvider, SocialAccount, SocialAuthEvent, SocialProfileEnrichment

logger = logging.getLogger(__name__)
User = get_user_model()


class SocialAuthError(Exception):
    """Custom exception for social authentication errors"""
    pass


class OAuthHandler:
    """Base OAuth handler for social authentication"""
    
    def __init__(self, provider_name: str):
        self.provider = SocialProvider.objects.get(name=provider_name, is_active=True)
        self.session = requests.Session()
        self.session.timeout = 30
    
    def get_authorization_url(self, redirect_uri: str, state: str, scopes: List[str] = None) -> str:
        """Generate OAuth authorization URL"""
        if scopes is None:
            scopes = self.provider.default_scopes
        
        return self.provider.get_authorize_url(state, redirect_uri, scopes)
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        try:
            response = self.session.post(self.provider.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Token exchange failed for {self.provider.name}: {str(e)}")
            raise SocialAuthError(f"Failed to exchange code for token: {str(e)}")
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch user profile data from provider"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = self.session.get(self.provider.user_info_url, headers=headers)
            response.raise_for_status()
            
            profile_data = response.json()
            return profile_data
            
        except requests.RequestException as e:
            logger.error(f"Profile fetch failed for {self.provider.name}: {str(e)}")
            raise SocialAuthError(f"Failed to fetch user profile: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        data = {
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = self.session.post(self.provider.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Token refresh failed for {self.provider.name}: {str(e)}")
            raise SocialAuthError(f"Failed to refresh token: {str(e)}")


class GoogleOAuthHandler(OAuthHandler):
    """Google-specific OAuth handler with enhanced profile data collection"""
    
    def __init__(self):
        super().__init__('google')
        self.people_api_url = 'https://people.googleapis.com/v1/people/me'
    
    def get_enhanced_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch enhanced profile data from Google People API"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Request comprehensive person data
        params = {
            'personFields': 'names,emailAddresses,phoneNumbers,addresses,photos,'
                          'biographies,birthdays,genders,locales,occupations,'
                          'organizations,urls,interests,skills,metadata'
        }
        
        try:
            response = self.session.get(self.people_api_url, headers=headers, params=params)
            response.raise_for_status()
            
            return self._process_google_profile(response.json())
            
        except requests.RequestException as e:
            logger.error(f"Enhanced Google profile fetch failed: {str(e)}")
            # Fallback to basic profile
            return self.get_user_profile(access_token)
    
    def _process_google_profile(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google People API response into normalized format"""
        profile = {
            'provider': 'google',
            'raw_data': raw_data,
            'data_completeness': 0,
        }
        
        # Extract names
        if 'names' in raw_data:
            name = raw_data['names'][0]
            profile.update({
                'name': name.get('displayName', ''),
                'first_name': name.get('givenName', ''),
                'last_name': name.get('familyName', ''),
            })
        
        # Extract emails
        if 'emailAddresses' in raw_data:
            primary_email = raw_data['emailAddresses'][0]
            profile['email'] = primary_email.get('value', '')
            profile['email_verified'] = primary_email.get('metadata', {}).get('verified', False)
        
        # Extract photos
        if 'photos' in raw_data:
            photo = raw_data['photos'][0]
            profile['avatar_url'] = photo.get('url', '')
        
        # Extract additional profile data
        if 'biographies' in raw_data:
            bio = raw_data['biographies'][0]
            profile['bio'] = bio.get('value', '')
        
        if 'addresses' in raw_data:
            address = raw_data['addresses'][0]
            profile['location'] = address.get('formattedValue', '')
            profile['country'] = address.get('country', '')
            profile['city'] = address.get('city', '')
        
        if 'organizations' in raw_data:
            org = raw_data['organizations'][0]
            profile.update({
                'company': org.get('name', ''),
                'job_title': org.get('title', ''),
                'work_location': org.get('location', ''),
            })
        
        if 'interests' in raw_data:
            profile['interests'] = [interest.get('value', '') for interest in raw_data['interests']]
        
        if 'skills' in raw_data:
            profile['skills'] = [skill.get('value', '') for skill in raw_data['skills']]
        
        if 'urls' in raw_data:
            profile['websites'] = [url.get('value', '') for url in raw_data['urls']]
        
        # Calculate completeness
        profile['data_completeness'] = self._calculate_profile_completeness(profile)
        
        return profile


class GitHubOAuthHandler(OAuthHandler):
    """GitHub-specific OAuth handler"""
    
    def __init__(self):
        super().__init__('github')
        self.api_base = 'https://api.github.com'
    
    def get_enhanced_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch enhanced profile data from GitHub API"""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # Get basic user info
            user_response = self.session.get(f"{self.api_base}/user", headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get additional data if available
            repos_response = self.session.get(f"{self.api_base}/user/repos", headers=headers)
            repos_data = repos_response.json() if repos_response.ok else []
            
            # Get organizations
            orgs_response = self.session.get(f"{self.api_base}/user/orgs", headers=headers)
            orgs_data = orgs_response.json() if orgs_response.ok else []
            
            return self._process_github_profile(user_data, repos_data, orgs_data)
            
        except requests.RequestException as e:
            logger.error(f"Enhanced GitHub profile fetch failed: {str(e)}")
            return self.get_user_profile(access_token)
    
    def _process_github_profile(self, user_data: Dict[str, Any], 
                               repos_data: List[Dict], orgs_data: List[Dict]) -> Dict[str, Any]:
        """Process GitHub API responses into normalized format"""
        profile = {
            'provider': 'github',
            'raw_data': {
                'user': user_data,
                'repos': repos_data,
                'organizations': orgs_data
            }
        }
        
        # Basic profile info
        profile.update({
            'name': user_data.get('name', ''),
            'username': user_data.get('login', ''),
            'email': user_data.get('email', ''),
            'avatar_url': user_data.get('avatar_url', ''),
            'bio': user_data.get('bio', ''),
            'location': user_data.get('location', ''),
            'website': user_data.get('blog', ''),
            'company': user_data.get('company', ''),
            'followers_count': user_data.get('followers', 0),
            'following_count': user_data.get('following', 0),
            'public_repos': user_data.get('public_repos', 0),
            'account_created': user_data.get('created_at', ''),
        })
        
        # Analyze repositories for skills and interests
        if repos_data:
            languages = {}
            topics = set()
            
            for repo in repos_data[:50]:  # Limit to first 50 repos
                if repo.get('language'):
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1
                
                if repo.get('topics'):
                    topics.update(repo['topics'])
            
            profile.update({
                'programming_languages': sorted(languages.keys(), key=languages.get, reverse=True),
                'topics_of_interest': list(topics),
                'total_stars': sum(repo.get('stargazers_count', 0) for repo in repos_data),
                'total_forks': sum(repo.get('forks_count', 0) for repo in repos_data),
            })
        
        # Organization memberships
        if orgs_data:
            profile['organizations'] = [org.get('login', '') for org in orgs_data]
        
        profile['data_completeness'] = self._calculate_profile_completeness(profile)
        
        return profile


class LinkedInOAuthHandler(OAuthHandler):
    """LinkedIn-specific OAuth handler"""
    
    def __init__(self):
        super().__init__('linkedin')
        self.api_base = 'https://api.linkedin.com/v2'
    
    def get_enhanced_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch enhanced profile data from LinkedIn API"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            # Get basic profile
            profile_response = self.session.get(
                f"{self.api_base}/people/~:(id,firstName,lastName,profilePicture,"
                f"headline,summary,industry,location,positions,educations)",
                headers=headers
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get email if available
            email_response = self.session.get(
                f"{self.api_base}/emailAddress?q=members&projection=(elements*(handle~))",
                headers=headers
            )
            email_data = email_response.json() if email_response.ok else {}
            
            return self._process_linkedin_profile(profile_data, email_data)
            
        except requests.RequestException as e:
            logger.error(f"Enhanced LinkedIn profile fetch failed: {str(e)}")
            return self.get_user_profile(access_token)
    
    def _process_linkedin_profile(self, profile_data: Dict[str, Any], 
                                 email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process LinkedIn API response into normalized format"""
        profile = {
            'provider': 'linkedin',
            'raw_data': {
                'profile': profile_data,
                'email': email_data
            }
        }
        
        # Basic info
        first_name = profile_data.get('firstName', {}).get('localized', {})
        last_name = profile_data.get('lastName', {}).get('localized', {})
        
        # Get first available locale
        first_locale = list(first_name.keys())[0] if first_name else ''
        last_locale = list(last_name.keys())[0] if last_name else ''
        
        profile.update({
            'first_name': first_name.get(first_locale, '') if first_locale else '',
            'last_name': last_name.get(last_locale, '') if last_locale else '',
            'headline': profile_data.get('headline', ''),
            'summary': profile_data.get('summary', ''),
            'industry': profile_data.get('industry', ''),
        })
        
        profile['name'] = f"{profile['first_name']} {profile['last_name']}".strip()
        
        # Email
        if email_data.get('elements'):
            email = email_data['elements'][0].get('handle~', {}).get('emailAddress', '')
            profile['email'] = email
        
        # Location
        if 'location' in profile_data:
            location = profile_data['location']
            profile['location'] = location.get('name', '')
            profile['country'] = location.get('country', {}).get('code', '')
        
        # Profile picture
        if 'profilePicture' in profile_data:
            pic_data = profile_data['profilePicture']
            display_image = pic_data.get('displayImage~')
            if display_image and display_image.get('elements'):
                # Get largest available image
                images = display_image['elements']
                if images:
                    largest_image = max(images, key=lambda x: x.get('data', {}).get('width', 0))
                    profile['avatar_url'] = largest_image.get('identifiers', [{}])[0].get('identifier', '')
        
        # Work experience
        if 'positions' in profile_data:
            positions = profile_data['positions'].get('values', [])
            if positions:
                current_position = positions[0]  # Most recent
                profile.update({
                    'current_company': current_position.get('company', {}).get('name', ''),
                    'current_title': current_position.get('title', ''),
                })
                
                # All companies
                profile['work_history'] = [{
                    'company': pos.get('company', {}).get('name', ''),
                    'title': pos.get('title', ''),
                    'start_date': pos.get('startDate', {}),
                    'end_date': pos.get('endDate', {}),
                    'summary': pos.get('summary', ''),
                } for pos in positions]
        
        # Education
        if 'educations' in profile_data:
            educations = profile_data['educations'].get('values', [])
            profile['education_history'] = [{
                'school': edu.get('schoolName', ''),
                'degree': edu.get('degreeName', ''),
                'field': edu.get('fieldOfStudy', ''),
                'start_date': edu.get('startDate', {}),
                'end_date': edu.get('endDate', {}),
            } for edu in educations]
        
        profile['data_completeness'] = self._calculate_profile_completeness(profile)
        
        return profile


class SocialAuthService:
    """Main service for managing social authentication and data collection"""
    
    def __init__(self):
        self.handlers = {
            'google': GoogleOAuthHandler(),
            'github': GitHubOAuthHandler(),
            'linkedin': LinkedInOAuthHandler(),
        }
    
    def get_handler(self, provider_name: str) -> OAuthHandler:
        """Get OAuth handler for specific provider"""
        if provider_name not in self.handlers:
            raise SocialAuthError(f"Unsupported provider: {provider_name}")
        return self.handlers[provider_name]
    
    def connect_social_account(self, user: User, provider_name: str, 
                             authorization_code: str, redirect_uri: str,
                             requested_scopes: List[str] = None) -> SocialAccount:
        """Connect a social account for a user"""
        handler = self.get_handler(provider_name)
        provider = handler.provider
        
        try:
            # Exchange code for token
            token_data = handler.exchange_code_for_token(authorization_code, redirect_uri)
            
            # Get user profile data
            if hasattr(handler, 'get_enhanced_profile'):
                profile_data = handler.get_enhanced_profile(token_data['access_token'])
            else:
                profile_data = handler.get_user_profile(token_data['access_token'])
            
            # Extract provider user ID
            provider_user_id = self._extract_user_id(provider_name, profile_data)
            
            # Create or update social account
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
                defaults={
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token', ''),
                    'username': profile_data.get('username', ''),
                    'email': profile_data.get('email', ''),
                    'scopes_granted': requested_scopes or provider.default_scopes,
                    'profile_data': profile_data,
                    'raw_profile_data': profile_data.get('raw_data', {}),
                }
            )
            
            if not created:
                # Update existing account
                social_account.access_token = token_data['access_token']
                social_account.refresh_token = token_data.get('refresh_token', '')
                social_account.profile_data = profile_data
                social_account.raw_profile_data = profile_data.get('raw_data', {})
                social_account.last_sync = timezone.now()
                social_account.save()
            
            # Set token expiration if provided
            if 'expires_in' in token_data:
                expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
                social_account.token_expires_at = expires_at
                social_account.save()
            
            # Log the event
            SocialAuthEvent.objects.create(
                user=user,
                social_account=social_account,
                provider=provider,
                event_type='connect',
                success=True,
                details={
                    'scopes': requested_scopes or provider.default_scopes,
                    'data_completeness': profile_data.get('data_completeness', 0),
                }
            )
            
            # Process profile enrichment
            self._process_profile_enrichment(social_account, profile_data)
            
            return social_account
            
        except Exception as e:
            # Log failed connection
            SocialAuthEvent.objects.create(
                user=user,
                provider=provider,
                event_type='connect',
                success=False,
                error_message=str(e),
                details={'requested_scopes': requested_scopes or []}
            )
            
            logger.error(f"Failed to connect {provider_name} account for user {user.email}: {str(e)}")
            raise SocialAuthError(f"Failed to connect social account: {str(e)}")
    
    def sync_social_account(self, social_account: SocialAccount) -> bool:
        """Sync profile data for an existing social account"""
        if not social_account.data_collection_consent:
            return False
        
        handler = self.get_handler(social_account.provider.name)
        
        try:
            # Refresh token if expired
            if social_account.is_token_expired and social_account.refresh_token:
                token_data = handler.refresh_token(social_account.refresh_token)
                social_account.access_token = token_data['access_token']
                if 'expires_in' in token_data:
                    expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
                    social_account.token_expires_at = expires_at
                social_account.save()
            
            # Get updated profile data
            if hasattr(handler, 'get_enhanced_profile'):
                profile_data = handler.get_enhanced_profile(social_account.access_token)
            else:
                profile_data = handler.get_user_profile(social_account.access_token)
            
            # Update profile data
            social_account.update_profile_data(profile_data)
            
            # Process enrichment
            self._process_profile_enrichment(social_account, profile_data)
            
            # Log sync event
            SocialAuthEvent.objects.create(
                user=social_account.user,
                social_account=social_account,
                provider=social_account.provider,
                event_type='sync',
                success=True,
                details={
                    'data_completeness': profile_data.get('data_completeness', 0),
                    'sync_type': social_account.sync_frequency,
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync social account {social_account.id}: {str(e)}")
            
            # Log failed sync
            SocialAuthEvent.objects.create(
                user=social_account.user,
                social_account=social_account,
                provider=social_account.provider,
                event_type='sync',
                success=False,
                error_message=str(e)
            )
            
            return False
    
    def _extract_user_id(self, provider_name: str, profile_data: Dict[str, Any]) -> str:
        """Extract user ID from profile data based on provider"""
        if provider_name == 'google':
            return profile_data.get('sub') or profile_data.get('id', '')
        elif provider_name == 'github':
            return str(profile_data.get('id', ''))
        elif provider_name == 'linkedin':
            return profile_data.get('id', '')
        else:
            return profile_data.get('id', '')
    
    def _process_profile_enrichment(self, social_account: SocialAccount, profile_data: Dict[str, Any]):
        """Process profile data for enrichment insights"""
        enrichment_processors = {
            'demographic': self._extract_demographic_data,
            'interests': self._extract_interests,
            'skills': self._extract_skills,
            'education': self._extract_education,
            'employment': self._extract_employment,
            'network': self._extract_network_data,
        }
        
        for enrichment_type, processor in enrichment_processors.items():
            try:
                enrichment_data = processor(profile_data, social_account.provider.name)
                if enrichment_data:
                    confidence = self._calculate_enrichment_confidence(enrichment_data, enrichment_type)
                    
                    SocialProfileEnrichment.objects.update_or_create(
                        user=social_account.user,
                        social_account=social_account,
                        enrichment_type=enrichment_type,
                        defaults={
                            'enrichment_data': enrichment_data,
                            'source_data': profile_data,
                            'confidence_score': confidence,
                            'extraction_method': f'{social_account.provider.name}_api',
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to process {enrichment_type} enrichment: {str(e)}")
    
    def _extract_demographic_data(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract demographic information"""
        demographic = {}
        
        if 'location' in profile_data:
            demographic['location'] = profile_data['location']
        if 'city' in profile_data:
            demographic['city'] = profile_data['city']
        if 'country' in profile_data:
            demographic['country'] = profile_data['country']
        if 'account_created' in profile_data:
            demographic['platform_tenure'] = profile_data['account_created']
        
        return demographic if demographic else None
    
    def _extract_interests(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract interests and hobbies"""
        interests = {}
        
        if 'interests' in profile_data:
            interests['declared_interests'] = profile_data['interests']
        if 'topics_of_interest' in profile_data:
            interests['topics'] = profile_data['topics_of_interest']
        if 'bio' in profile_data and profile_data['bio']:
            interests['bio_keywords'] = self._extract_keywords_from_text(profile_data['bio'])
        
        return interests if interests else None
    
    def _extract_skills(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract skills and expertise"""
        skills = {}
        
        if 'skills' in profile_data:
            skills['declared_skills'] = profile_data['skills']
        if 'programming_languages' in profile_data:
            skills['programming_languages'] = profile_data['programming_languages']
        if provider == 'github' and 'raw_data' in profile_data:
            # Analyze repositories for technical skills
            repos = profile_data['raw_data'].get('repos', [])
            if repos:
                skills['github_languages'] = self._analyze_github_languages(repos)
                skills['project_complexity'] = self._assess_project_complexity(repos)
        
        return skills if skills else None
    
    def _extract_education(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract educational background"""
        education = {}
        
        if 'education_history' in profile_data:
            education['education_history'] = profile_data['education_history']
        
        return education if education else None
    
    def _extract_employment(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract employment information"""
        employment = {}
        
        if 'current_company' in profile_data:
            employment['current_company'] = profile_data['current_company']
        if 'current_title' in profile_data:
            employment['current_title'] = profile_data['current_title']
        if 'work_history' in profile_data:
            employment['work_history'] = profile_data['work_history']
        if 'industry' in profile_data:
            employment['industry'] = profile_data['industry']
        
        return employment if employment else None
    
    def _extract_network_data(self, profile_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Extract social network information"""
        network = {}
        
        if 'followers_count' in profile_data:
            network['followers'] = profile_data['followers_count']
        if 'following_count' in profile_data:
            network['following'] = profile_data['following_count']
        if 'organizations' in profile_data:
            network['organizations'] = profile_data['organizations']
        
        if provider == 'github':
            if 'total_stars' in profile_data:
                network['github_stars'] = profile_data['total_stars']
            if 'public_repos' in profile_data:
                network['public_repos'] = profile_data['public_repos']
        
        return network if network else None
    
    def _calculate_enrichment_confidence(self, data: Dict[str, Any], enrichment_type: str) -> float:
        """Calculate confidence score for enrichment data"""
        # Simple confidence calculation based on data completeness
        if not data:
            return 0.0
        
        # Weight different data types
        weights = {
            'demographic': 0.8,
            'interests': 0.6,
            'skills': 0.9,
            'education': 0.8,
            'employment': 0.9,
            'network': 0.7,
        }
        
        base_confidence = weights.get(enrichment_type, 0.5)
        completeness_bonus = min(0.3, len(data) * 0.05)  # Bonus for more data points
        
        return min(1.0, base_confidence + completeness_bonus)
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text (simplified implementation)"""
        import re
        
        # Simple keyword extraction - in production, use NLP libraries
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter common words and return meaningful ones
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their'}
        keywords = [word for word in words if len(word) > 3 and word not in stopwords]
        return list(set(keywords))[:10]  # Return top 10 unique keywords
    
    def _analyze_github_languages(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze programming languages from GitHub repositories"""
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
    
    def _assess_project_complexity(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess project complexity from GitHub repositories"""
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        avg_size = sum(repo.get('size', 0) for repo in repos) / len(repos) if repos else 0
        
        return {
            'total_stars': total_stars,
            'total_forks': total_forks,
            'average_repo_size': avg_size,
            'repo_count': len(repos),
            'complexity_score': min(10, (total_stars * 0.1) + (total_forks * 0.2) + (avg_size * 0.001))
        }
    
    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate profile data completeness percentage"""
        expected_fields = [
            'name', 'email', 'avatar_url', 'bio', 'location',
            'company', 'website', 'interests', 'skills'
        ]
        
        present_fields = sum(1 for field in expected_fields 
                           if profile.get(field) and str(profile[field]).strip())
        
        return round((present_fields / len(expected_fields)) * 100, 2)
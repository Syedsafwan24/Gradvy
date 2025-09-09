# Gradvy Enhanced Social Authentication Guide

## Overview

The Gradvy Enhanced Social Authentication system provides comprehensive OAuth integration with major social platforms, capturing rich profile data for personalized learning experiences while maintaining strict privacy compliance.

## Features

### 🔐 **OAuth Integration**
- **Supported Providers**: Google, GitHub, LinkedIn, Facebook, Microsoft
- **Secure Token Management**: Automatic token refresh and expiration handling
- **CSRF Protection**: State parameter validation for security

### 📊 **Rich Profile Data Collection**
- **Basic Profile**: Name, email, avatar, bio, location
- **Professional Data**: Company, job title, work history, skills
- **Educational Background**: Degrees, certifications, academic history
- **Technical Skills**: Programming languages, project analysis, expertise levels
- **Social Network**: Followers, connections, influence metrics

### 🛡️ **Privacy-First Design**
- **Granular Consent**: Individual consent for each data type
- **GDPR Compliance**: Right to deletion, data export, consent management
- **Data Retention**: Configurable retention policies per data type
- **Audit Trail**: Complete logging of all authentication and data events

### 🤖 **AI-Powered Enrichment**
- **Professional Level Analysis**: Entry to executive level assessment
- **Technical Expertise**: Skill level analysis from GitHub activity
- **Learning Preferences**: Inferred from profile patterns
- **Content Recommendations**: Based on enriched profile data

## Architecture

```
Frontend → OAuth Flow → Backend API → Social Providers
    ↓         ↓           ↓              ↓
User Auth → Token Mgmt → Data Processing → Profile Enrichment
    ↓                        ↓               ↓
  JWT Tokens → User Preferences ← AI Analysis ← Celery Tasks
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Add to requirements.txt
pip install -r social_auth_requirements.txt
```

### 2. Database Migration

```bash
# Create and apply migrations
python manage.py makemigrations auth
python manage.py migrate
```

### 3. Load Initial Data

```bash
# Load social provider configurations
python manage.py loaddata social_providers
```

### 4. Configure Social Providers

Update the social provider configurations with your OAuth credentials:

```python
# In Django Admin or via management command
SocialProvider.objects.filter(name='google').update(
    client_id='your_google_client_id',
    client_secret='your_google_client_secret'
)
```

### 5. Environment Variables

```env
# OAuth Credentials
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GITHUB_OAUTH_CLIENT_ID=your_github_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_github_client_secret
LINKEDIN_OAUTH_CLIENT_ID=your_linkedin_client_id
LINKEDIN_OAUTH_CLIENT_SECRET=your_linkedin_client_secret
```

## API Documentation

### Authentication Flow

#### 1. Initiate OAuth
```http
POST /api/auth/social/initiate/
Content-Type: application/json

{
    "provider": "google",
    "redirect_uri": "http://localhost:3000/auth/callback",
    "scopes": ["profile", "email"],
    "collect_extended_data": true
}
```

**Response:**
```json
{
    "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
    "state": "csrf_token",
    "provider": "google",
    "scopes": ["openid", "profile", "email"]
}
```

#### 2. Handle OAuth Callback
```http
POST /api/auth/social/callback/
Content-Type: application/json

{
    "code": "oauth_authorization_code",
    "state": "csrf_token",
    "create_account": true
}
```

**Response (New User):**
```json
{
    "success": true,
    "action": "registered",
    "user_id": 123,
    "email": "user@example.com",
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "provider": "google",
    "profile_data": {
        "name": "John Doe",
        "avatar_url": "https://...",
        "data_completeness": 85.5
    },
    "requires_onboarding": true
}
```

### Account Management

#### Get Connected Accounts
```http
GET /api/auth/social/accounts/
Authorization: Bearer jwt_token
```

**Response:**
```json
{
    "social_accounts": [
        {
            "id": 1,
            "provider": {
                "name": "google",
                "display_name": "Google"
            },
            "username": "john.doe",
            "email": "john@gmail.com",
            "profile_completeness": 92.3,
            "last_sync": "2023-10-15T10:30:00Z",
            "sync_frequency": "daily",
            "data_collection_consent": true,
            "connected_at": "2023-10-01T09:15:00Z"
        }
    ],
    "total_connected": 1
}
```

#### Sync Account Data
```http
POST /api/auth/social/accounts/sync/
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "account_id": 1
}
```

### Privacy Management

#### Get Privacy Settings
```http
GET /api/auth/social/privacy/
Authorization: Bearer jwt_token
```

#### Update Privacy Settings
```http
PUT /api/auth/social/privacy/
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "account_id": 1,
    "settings": {
        "data_collection_consent": true,
        "public_profile_allowed": false,
        "analytics_consent": true
    }
}
```

### Profile Enrichment

#### Get Enriched Profile Data
```http
GET /api/auth/social/enrichment/
Authorization: Bearer jwt_token
```

**Response:**
```json
{
    "enrichment_data": {
        "professional_level": {
            "sources": [
                {
                    "provider": "linkedin",
                    "confidence": 0.89,
                    "validated": true,
                    "last_updated": "2023-10-15T10:30:00Z"
                }
            ],
            "combined_data": {
                "primary_level": "senior_level",
                "confidence": 0.89,
                "total_experience_years": 8
            },
            "overall_confidence": 0.89
        },
        "technical_expertise": {
            "sources": [
                {
                    "provider": "github",
                    "confidence": 0.92,
                    "validated": false,
                    "last_updated": "2023-10-15T11:00:00Z"
                }
            ],
            "combined_data": {
                "expertise_level": "advanced",
                "primary_languages": ["Python", "JavaScript", "Go"],
                "project_complexity": 1250,
                "confidence": 0.92
            },
            "overall_confidence": 0.92
        }
    },
    "total_sources": 2,
    "last_updated": "2023-10-15T11:00:00Z"
}
```

## Provider-Specific Features

### Google Integration
- **Enhanced Scopes**: Birthday, addresses, detailed profile
- **People API**: Comprehensive profile data including interests and skills
- **Data Quality**: High confidence due to verified information

### GitHub Integration
- **Repository Analysis**: Programming language detection and expertise assessment
- **Project Complexity**: Star count and fork analysis for skill evaluation
- **Contribution Patterns**: Activity analysis for learning behavior insights

### LinkedIn Integration
- **Professional Focus**: Work history, education, industry connections
- **Experience Analysis**: Career level assessment and skill validation
- **Network Insights**: Professional network size and influence metrics

## Celery Background Tasks

### Automated Data Processing

```python
# Sync all user's social accounts
from apps.preferences.tasks import sync_social_accounts_batch

# Get user's social account IDs
account_ids = [1, 2, 3]
task = sync_social_accounts_batch.delay(account_ids)
```

### Profile Enrichment

```python
# Enrich user profile from social data
from apps.preferences.tasks import enrich_user_profile_from_social

task = enrich_user_profile_from_social.delay(user_id=123)
```

### Token Maintenance

```python
# Clean up expired tokens
from apps.preferences.tasks import cleanup_expired_social_tokens

task = cleanup_expired_social_tokens.delay()
```

## Data Models

### SocialProvider
- Provider configuration and OAuth settings
- Scope management and field mappings
- Privacy and collection settings

### SocialAccount
- User's connected social accounts
- OAuth tokens and profile data
- Privacy consent and sync settings

### SocialProfileEnrichment
- AI-generated insights from profile data
- Confidence scores and validation status
- Enrichment type categorization

### SocialAuthEvent
- Complete audit trail of authentication events
- Success/failure tracking and error logging
- Privacy consent change tracking

## Privacy and Compliance

### GDPR Features

1. **Consent Management**
   - Granular consent for each data type
   - Easy consent withdrawal
   - Consent expiration and renewal

2. **Data Rights**
   - Right to access collected data
   - Right to data portability (export)
   - Right to deletion (forget me)

3. **Audit Trail**
   - All data collection events logged
   - Consent changes tracked
   - Data processing activities recorded

### Data Retention

```python
# Configure retention policies
SocialDataCollection.objects.create(
    user=user,
    provider=provider,
    collection_type='profile',
    purpose='Personalized learning recommendations',
    data_retention_days=365,
    consent_status='granted'
)
```

## Frontend Integration

### React Hook Example

```javascript
// useSocialAuth.js
import { useState } from 'react';
import axios from 'axios';

export const useSocialAuth = () => {
    const [loading, setLoading] = useState(false);
    
    const initiateAuth = async (provider, redirectUri) => {
        setLoading(true);
        try {
            const response = await axios.post('/api/auth/social/initiate/', {
                provider,
                redirect_uri: redirectUri,
                collect_extended_data: true
            });
            
            // Redirect to OAuth provider
            window.location.href = response.data.authorization_url;
        } catch (error) {
            console.error('Auth initiation failed:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const handleCallback = async (code, state) => {
        try {
            const response = await axios.post('/api/auth/social/callback/', {
                code,
                state,
                create_account: true
            });
            
            // Store tokens and user data
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
            
            return response.data;
        } catch (error) {
            throw new Error('Authentication failed');
        }
    };
    
    return { initiateAuth, handleCallback, loading };
};
```

### Social Login Button Component

```javascript
// SocialLoginButton.jsx
import React from 'react';
import { useSocialAuth } from './useSocialAuth';

const SocialLoginButton = ({ provider, children }) => {
    const { initiateAuth, loading } = useSocialAuth();
    
    const handleLogin = () => {
        const redirectUri = `${window.location.origin}/auth/callback`;
        initiateAuth(provider, redirectUri);
    };
    
    return (
        <button 
            onClick={handleLogin} 
            disabled={loading}
            className="social-login-btn"
        >
            {loading ? 'Connecting...' : children}
        </button>
    );
};

export default SocialLoginButton;
```

## Security Best Practices

### Token Security
- Access tokens encrypted at rest
- Refresh tokens stored securely
- Automatic token rotation
- Token expiration monitoring

### OAuth Security
- CSRF protection with state parameter
- Secure redirect URI validation
- Scope validation and restriction
- Rate limiting on auth endpoints

### Privacy Protection
- Data minimization principles
- Consent-based data collection
- Regular consent renewal
- Secure data transmission

## Monitoring and Analytics

### Key Metrics
- Authentication success rates by provider
- Data collection consent rates
- Profile enrichment accuracy
- Token refresh success rates

### Alerts
- Failed authentication attempts
- Expired tokens requiring attention
- Privacy consent violations
- Data sync failures

## Testing

### Unit Tests
```python
# test_social_auth.py
from django.test import TestCase
from apps.auth.social_services import SocialAuthService

class SocialAuthTest(TestCase):
    def test_google_profile_processing(self):
        service = SocialAuthService()
        handler = service.get_handler('google')
        
        # Mock profile data
        profile_data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        processed = handler._process_google_profile(profile_data)
        self.assertEqual(processed['name'], 'Test User')
```

### Integration Tests
```python
def test_oauth_flow(self):
    # Test complete OAuth flow
    response = self.client.post('/api/auth/social/initiate/', {
        'provider': 'google',
        'redirect_uri': 'http://localhost:3000/callback'
    })
    
    self.assertEqual(response.status_code, 200)
    self.assertIn('authorization_url', response.json())
```

## Troubleshooting

### Common Issues

1. **OAuth Redirect Mismatch**
   - Ensure redirect URIs match exactly in provider settings
   - Check for trailing slashes and protocol differences

2. **Token Expiration**
   - Implement automatic token refresh
   - Monitor token expiration logs

3. **Scope Permissions**
   - Verify requested scopes are approved by provider
   - Check scope availability for different provider tiers

4. **Rate Limiting**
   - Implement backoff strategies for API calls
   - Monitor provider rate limit headers

### Debug Commands

```bash
# Check social provider configurations
python manage.py shell -c "
from apps.auth.social_models import SocialProvider
for provider in SocialProvider.objects.all():
    print(f'{provider.name}: {provider.is_active}')
"

# Test OAuth handler
python manage.py shell -c "
from apps.auth.social_services import SocialAuthService
service = SocialAuthService()
handler = service.get_handler('google')
print(handler.provider.default_scopes)
"
```

## Performance Optimization

### Caching Strategy
- Cache OAuth tokens with appropriate TTL
- Cache profile data for quick access
- Implement Redis-based session storage

### Database Optimization
- Index frequently queried fields
- Use database-level JSON queries for profile data
- Implement connection pooling

### API Rate Limiting
- Implement exponential backoff
- Batch API requests where possible
- Use webhooks for real-time updates

## Future Enhancements

### Planned Features
- **Additional Providers**: Twitter/X, Discord, Slack integration
- **Real-time Updates**: Webhook support for profile changes
- **Advanced Analytics**: ML-based user segmentation
- **Enterprise SSO**: SAML and OpenID Connect support

### Roadmap
- **Q1 2024**: Additional social providers and webhook support
- **Q2 2024**: Advanced AI-based profile analysis
- **Q3 2024**: Enterprise SSO integration
- **Q4 2024**: Advanced privacy controls and data portability

## Support

For questions or issues:

1. Check the logs: `tail -f logs/social_auth.log`
2. Review provider API documentation
3. Test with OAuth debugging tools
4. Verify HTTPS configuration for production

## Contributing

When adding new social providers:

1. Create provider-specific OAuth handler
2. Define field mappings in fixtures
3. Implement profile data processing
4. Add comprehensive tests
5. Update documentation

The enhanced social authentication system provides a solid foundation for collecting rich user profile data while maintaining the highest standards of privacy and security.
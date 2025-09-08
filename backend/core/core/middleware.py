"""
Security middleware for enhanced cookie and header security
"""
import uuid
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add comprehensive security headers for cookie protection
    and general web application security
    """
    
    def process_response(self, request, response):
        """Add security headers to all responses"""
        
        # Content Security Policy - prevents XSS and other injection attacks
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 ws: wss:",
            "media-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
        
        # Add development origins if in debug mode
        if settings.DEBUG:
            csp_directives.append("connect-src 'self' http://localhost:3000 http://127.0.0.1:3000 http://localhost:8000 http://127.0.0.1:8000 ws: wss:")
        
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # X-Frame-Options - prevents clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options - prevents MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer Policy - controls referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # X-XSS-Protection - enables XSS filtering
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Permissions Policy - controls browser features
        permissions_policy_directives = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]
        response['Permissions-Policy'] = ', '.join(permissions_policy_directives)
        
        # Only add HTTPS-related headers in production
        if not settings.DEBUG:
            # Strict-Transport-Security - enforces HTTPS
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            
            # Expect-CT - Certificate Transparency
            response['Expect-CT'] = 'max-age=86400, enforce'
        
        return response


class CookieSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance cookie security and add cookie-related headers
    """
    
    def process_response(self, request, response):
        """Enhance cookie security"""
        
        # Add secure cookie policy header
        response['Set-Cookie-Policy'] = 'secure; samesite=lax; httponly'
        
        # For authentication cookies, add additional security
        for cookie_name in ['gradvy_sessionid', 'refresh_token', 'gradvy_csrftoken']:
            if cookie_name in response.cookies:
                cookie = response.cookies[cookie_name]
                
                # Ensure secure flag in production
                if not settings.DEBUG:
                    cookie['secure'] = True
                
                # Set SameSite for CSRF protection
                if cookie_name == 'gradvy_csrftoken':
                    cookie['samesite'] = 'Lax'
                    cookie['httponly'] = False  # CSRF needs to be accessible to JS
                else:
                    cookie['samesite'] = 'Lax'
                    cookie['httponly'] = True
                
                # Add Path for security
                cookie['path'] = '/'
        
        return response


class SessionFingerprintMiddleware(MiddlewareMixin):
    """
    Add session fingerprinting for enhanced security
    """
    
    def process_request(self, request):
        """Add session fingerprinting data"""
        # Check if user attribute exists and is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Create a session fingerprint based on user agent and IP
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]  # Limit length
            remote_addr = self.get_client_ip(request)
            
            session_fingerprint = f"{user_agent}:{remote_addr}"
            
            # Store fingerprint in session
            if 'session_fingerprint' not in request.session:
                request.session['session_fingerprint'] = session_fingerprint
                request.session['fingerprint_created'] = str(uuid.uuid4())
            else:
                # Verify fingerprint matches
                stored_fingerprint = request.session.get('session_fingerprint')
                if stored_fingerprint != session_fingerprint:
                    # Fingerprint mismatch - potential session hijacking
                    request.session.flush()
                    # Could also log this security event
    
    def get_client_ip(self, request):
        """Get client IP address considering proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip[:45]  # Limit length for IPv6


class CookieConsentMiddleware(MiddlewareMixin):
    """
    Middleware to handle cookie consent tracking
    """
    
    def process_request(self, request):
        """Track cookie consent status"""
        # Check for cookie consent
        consent_given = request.COOKIES.get('gradvy_cookie_consent', 'false')
        request.cookie_consent_given = consent_given.lower() == 'true'
        
        # Store consent level if available
        consent_level = request.COOKIES.get('gradvy_cookie_preferences', 'essential')
        request.cookie_consent_level = consent_level
    
    def process_response(self, request, response):
        """Set cookie consent tracking if not already set"""
        if not request.COOKIES.get('gradvy_cookie_consent_set'):
            # Mark that we need to show cookie consent banner
            response['X-Cookie-Consent-Required'] = 'true'
        
        return response
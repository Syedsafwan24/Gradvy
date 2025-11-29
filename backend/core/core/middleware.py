"""
Security middleware for enhanced cookie and header security
"""
import uuid
import time
import json
import logging
from datetime import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.db import connection


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
            "connect-src 'self' http://localhost:8030 http://127.0.0.1:8030 ws: wss:",
            "media-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
        
        # Add development origins if in debug mode
        if settings.DEBUG:
            csp_directives.append("connect-src 'self' http://localhost:3000 http://127.0.0.1:3000 http://localhost:8030 http://127.0.0.1:8030 ws: wss:")
        
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


class APIRequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    backend/core/core/middleware.py
    Comprehensive API request/response logging middleware
    Logs all API calls with full request/response details and performance metrics
    RELEVANT FILES: settings.py, utils/responses.py, apps/*/api/views.py
    """

    def __init__(self, get_response):
        """Initialize the middleware with logger."""
        super().__init__(get_response)
        self.logger = logging.getLogger('api')

        # Paths to skip logging (static files, health checks, etc.)
        self.skip_paths = [
            '/static/',
            '/media/',
            '/admin/jsi18n/',
        ]

    def __call__(self, request):
        """
        Main middleware entry point.
        Captures request, processes it, captures response, and logs everything.
        """
        # Skip if not in DEBUG mode (development only)
        if not settings.DEBUG:
            return self.get_response(request)

        # Skip static files and excluded paths
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)

        # Capture request start time and initial state
        start_time = time.time()
        start_query_count = len(connection.queries)

        try:
            # Get memory usage before request (if psutil available)
            start_memory = self._get_memory_usage()
        except:
            start_memory = None

        # Capture request details BEFORE processing
        request_data = self._capture_request(request)

        # Process the request and get response
        response = self.get_response(request)

        # Calculate performance metrics
        duration_ms = (time.time() - start_time) * 1000
        end_query_count = len(connection.queries)
        query_count = end_query_count - start_query_count

        # Get SQL queries that were executed
        queries = connection.queries[start_query_count:end_query_count] if query_count > 0 else []

        # Calculate total query time
        query_time_ms = sum(float(q.get('time', 0)) * 1000 for q in queries)

        try:
            end_memory = self._get_memory_usage()
            memory_delta = end_memory - start_memory if (start_memory and end_memory) else None
        except:
            memory_delta = None

        # Capture response details AFTER processing
        response_data = self._capture_response(response)

        # Build metrics dictionary
        metrics = {
            'duration_ms': duration_ms,
            'query_count': query_count,
            'query_time_ms': query_time_ms,
            'queries': queries,
            'memory_delta_mb': memory_delta
        }

        # Log the complete API call
        self._log_api_call(request_data, response_data, metrics)

        return response

    def _capture_request(self, request):
        """
        Capture all request details.

        Returns dictionary with:
        - HTTP method, path, query params
        - Headers
        - Request body (JSON/form data)
        - User info
        - IP address, user agent
        """
        # Extract request body
        body = self._get_request_body(request)

        # Extract user info
        user_info = self._get_user_info(request)

        # Extract headers
        headers = self._get_headers(request)

        return {
            'method': request.method,
            'path': request.path,
            'full_path': request.get_full_path(),
            'query_params': dict(request.GET) if request.GET else None,
            'headers': headers,
            'body': body,
            'user': user_info,
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        }

    def _capture_response(self, response):
        """
        Capture all response details.

        Returns dictionary with:
        - Status code
        - Response headers
        - Response body (JSON)
        """
        # Extract response body
        body = self._get_response_body(response)

        # Extract headers
        headers = dict(response.items())

        return {
            'status_code': response.status_code,
            'status_text': self._get_status_text(response.status_code),
            'headers': headers,
            'body': body,
            'content_type': response.get('Content-Type', ''),
        }

    def _get_request_body(self, request):
        """Extract and parse request body."""
        try:
            if request.body:
                content_type = request.META.get('CONTENT_TYPE', '')

                if 'application/json' in content_type:
                    return json.loads(request.body.decode('utf-8'))
                elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
                    return dict(request.POST) if request.POST else None
                else:
                    # Return truncated raw body for other types
                    body_str = request.body.decode('utf-8', errors='ignore')
                    return body_str[:500] + '...' if len(body_str) > 500 else body_str
            return None
        except Exception as e:
            return f"<Error parsing body: {str(e)}>"

    def _get_response_body(self, response):
        """Extract and parse response body."""
        try:
            if hasattr(response, 'content'):
                content_type = response.get('Content-Type', '')

                if 'application/json' in content_type:
                    content = response.content.decode('utf-8')
                    return json.loads(content) if content else None
                elif 'text/' in content_type:
                    content = response.content.decode('utf-8', errors='ignore')
                    # Truncate long text responses
                    return content[:1000] + '...' if len(content) > 1000 else content
                else:
                    return f"<Binary content: {len(response.content)} bytes>"
            return None
        except Exception as e:
            return f"<Error parsing response: {str(e)}>"

    def _get_headers(self, request):
        """Extract HTTP headers from request."""
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_AUTHORIZATION to Authorization
                header_name = key[5:].replace('_', '-').title()
                # Truncate authorization tokens for security
                if 'AUTHORIZATION' in key or 'TOKEN' in key:
                    headers[header_name] = value[:50] + '...' if len(value) > 50 else value
                else:
                    headers[header_name] = value
        return headers

    def _get_user_info(self, request):
        """Extract authenticated user information."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return {
                'id': request.user.id,
                'email': getattr(request.user, 'email', ''),
                'username': request.user.username,
                'is_authenticated': True
            }
        return {'is_authenticated': False}

    def _get_client_ip(self, request):
        """Get client IP address considering proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

    def _get_status_text(self, status_code):
        """Get human-readable status text."""
        status_texts = {
            200: 'OK',
            201: 'Created',
            202: 'Accepted',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            409: 'Conflict',
            422: 'Unprocessable Entity',
            429: 'Too Many Requests',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
        }
        return status_texts.get(status_code, 'Unknown')

    def _get_memory_usage(self):
        """Get current process memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            return round(memory_mb, 2)
        except ImportError:
            return None

    def _log_api_call(self, request_data, response_data, metrics):
        """
        Format and log the complete API call with beautiful formatting.

        Creates a comprehensive log entry with:
        - Request details
        - Response details
        - Performance metrics
        - Database queries
        """
        # Determine log level based on status code
        status_code = response_data['status_code']
        if status_code >= 500:
            log_level = logging.ERROR
            status_emoji = '❌'
        elif status_code >= 400:
            log_level = logging.WARNING
            status_emoji = '⚠️ '
        else:
            log_level = logging.INFO
            status_emoji = '✅'

        # Build formatted log message
        separator = "=" * 80
        log_lines = [
            "",
            separator,
            f"[API REQUEST] {request_data['method']} {request_data['path']}",
            separator,
            f"🕐 Timestamp: {request_data['timestamp']}",
        ]

        # User info
        if request_data['user']['is_authenticated']:
            user = request_data['user']
            log_lines.append(f"👤 User: {user.get('email', user.get('username', 'Unknown'))} (ID: {user['id']}) [Authenticated: True]")
        else:
            log_lines.append(f"👤 User: Anonymous [Authenticated: False]")

        # Request metadata
        log_lines.extend([
            f"🌐 IP: {request_data['ip']}",
            f"🖥️  User-Agent: {request_data['user_agent'][:100]}{'...' if len(request_data['user_agent']) > 100 else ''}",
        ])

        if request_data['content_type']:
            log_lines.append(f"📋 Content-Type: {request_data['content_type']}")

        # Request headers
        if request_data['headers']:
            log_lines.append("\n📨 REQUEST HEADERS:")
            for key, value in request_data['headers'].items():
                log_lines.append(f"   {key}: {value}")

        # Request body
        if request_data['body']:
            log_lines.append("\n📦 REQUEST BODY:")
            if isinstance(request_data['body'], dict):
                log_lines.append(json.dumps(request_data['body'], indent=2))
            else:
                log_lines.append(f"   {request_data['body']}")

        # Query params
        if request_data['query_params']:
            log_lines.append("\n📥 QUERY PARAMS:")
            for key, value in request_data['query_params'].items():
                log_lines.append(f"   {key}: {value}")

        # Performance metrics
        log_lines.append(f"\n⏱️  PROCESSING TIME: {metrics['duration_ms']:.2f}ms")

        # Database queries
        if metrics['query_count'] > 0:
            log_lines.append(f"\n💾 DATABASE QUERIES: {metrics['query_count']} queries in {metrics['query_time_ms']:.2f}ms")
            for idx, query in enumerate(metrics['queries'][:10], 1):  # Show first 10 queries
                sql = query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql']
                query_time = float(query.get('time', 0)) * 1000
                log_lines.append(f"   {idx}. {sql} ({query_time:.2f}ms)")
            if len(metrics['queries']) > 10:
                log_lines.append(f"   ... and {len(metrics['queries']) - 10} more queries")

        # Memory usage
        if metrics['memory_delta_mb'] is not None:
            log_lines.append(f"\n📊 MEMORY DELTA: {metrics['memory_delta_mb']:+.2f} MB")

        # Response status
        log_lines.append(f"\n{status_emoji} RESPONSE STATUS: {response_data['status_code']} {response_data['status_text']}")

        # Response headers
        if response_data['headers']:
            log_lines.append("\n📤 RESPONSE HEADERS:")
            for key, value in list(response_data['headers'].items())[:10]:  # Show first 10 headers
                log_lines.append(f"   {key}: {value}")

        # Response body
        if response_data['body']:
            log_lines.append("\n📦 RESPONSE BODY:")
            if isinstance(response_data['body'], dict):
                # Pretty print JSON with indentation
                body_str = json.dumps(response_data['body'], indent=2)
                # Truncate very long responses
                if len(body_str) > 3000:
                    body_str = body_str[:3000] + '\n   ... (truncated)'
                log_lines.append(body_str)
            else:
                log_lines.append(f"   {response_data['body']}")

        log_lines.append(separator)

        # Log everything as a single message
        self.logger.log(log_level, '\n'.join(log_lines))
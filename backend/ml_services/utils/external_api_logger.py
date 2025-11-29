# File: backend/ml_services/utils/external_api_logger.py
# Description: Centralized decorator for logging all external API calls (YouTube, Groq, roadmap.sh, Udemy, OAuth)
# Purpose: Provides comprehensive logging with request/response details, performance metrics, and quota tracking
# RELEVANT FILES: ml_services/integrations/course_search_service.py, ml_services/models/api_text_generation_model.py, ml_services/services/ai_goal_analyzer.py, ml_services/integrations/roadmap_service.py

import functools
import time
import logging
import json
from typing import Callable, Any
from datetime import datetime

# Get the external_api logger configured in settings.py
logger = logging.getLogger('external_api')


def log_external_api_call(
    api_name: str,
    include_headers: bool = True,
    include_request_body: bool = True,
    include_response_body: bool = True,
    truncate_response_at: int = 5000,
    sanitize_auth: bool = True,
    quota_units: int = 0,  # For YouTube API quota tracking
    include_tokens: bool = False  # For LLM token tracking
):
    """
    Decorator to log external API calls with full details.

    This decorator wraps external API methods to provide comprehensive logging including:
    - Request parameters and headers (with auth sanitization)
    - Response data and status
    - Duration and performance metrics
    - Quota usage (for YouTube API)
    - Token usage (for LLM APIs)
    - Error details with full exception info

    Args:
        api_name: Name of the external API (e.g., "YouTube Video Search", "Groq LLM")
        include_headers: Log request/response headers (default: True)
        include_request_body: Log request body/params (default: True)
        include_response_body: Log response body (default: True)
        truncate_response_at: Max response body size to log in chars (default: 5000)
        sanitize_auth: Redact authorization tokens for security (default: True)
        quota_units: YouTube API quota units consumed by this call (default: 0)
        include_tokens: Log LLM token usage if available (default: False)

    Returns:
        Decorated function that logs API calls while maintaining original behavior

    Example:
        @log_external_api_call(api_name="YouTube Video Search", quota_units=100)
        def _search_youtube_videos(self, query, max_results=5):
            # Existing API call code
            pass

    Security:
        - Automatically sanitizes sensitive keys: access_token, api_key, password, secret, authorization
        - Truncates sensitive values to first 10 + last 4 characters
        - Set sanitize_auth=True for OAuth methods to protect user tokens
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Capture start time for performance tracking
            start_time = time.time()

            # Generate unique request ID for correlation
            request_id = f"{api_name}_{int(time.time() * 1000)}"

            # ====================================================================
            # REQUEST LOGGING
            # ====================================================================
            logger.info(f"\n{'='*80}\n[{api_name}] API REQUEST - {func.__name__}\n{'='*80}")
            logger.info(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"🔑 Request ID: {request_id}")

            # Log function arguments (sanitized if auth data present)
            if include_request_body:
                # Sanitize sensitive auth data before logging
                sanitized_kwargs = _sanitize_auth_data(kwargs) if sanitize_auth else kwargs

                # Also sanitize args if they contain sensitive data
                sanitized_args = args
                if sanitize_auth and len(args) > 0:
                    # Convert args to dict for sanitization (skip 'self' if present)
                    args_dict = {f"arg_{i}": arg for i, arg in enumerate(args) if not (i == 0 and hasattr(arg, '__class__'))}
                    sanitized_args_dict = _sanitize_auth_data(args_dict)
                    sanitized_args_str = f", positional_args: {json.dumps(sanitized_args_dict, indent=2, default=str)}"
                else:
                    sanitized_args_str = ""

                logger.info(f"📦 Request Parameters: {json.dumps(sanitized_kwargs, indent=2, default=str)}{sanitized_args_str}")

            try:
                # ============================================================
                # EXECUTE THE ACTUAL API CALL
                # ============================================================
                result = func(*args, **kwargs)

                # Calculate duration in milliseconds
                duration_ms = (time.time() - start_time) * 1000

                # ============================================================
                # RESPONSE LOGGING - SUCCESS
                # ============================================================
                logger.info(f"\n✅ [{api_name}] API RESPONSE - SUCCESS")
                logger.info(f"⏱️  Duration: {duration_ms:.2f}ms")

                # Log response body if enabled
                if include_response_body:
                    response_str = str(result)
                    if len(response_str) > truncate_response_at:
                        response_str = response_str[:truncate_response_at] + f"... (truncated, total length: {len(response_str)} chars)"
                    logger.info(f"📥 Response Data: {response_str}")

                # Log YouTube quota usage if applicable
                if quota_units > 0:
                    logger.info(f"📊 YouTube Quota Used: {quota_units} units")

                # Log LLM token usage if available and enabled
                if include_tokens:
                    if hasattr(result, 'tokens_generated'):
                        logger.info(f"🔢 Tokens Generated: {result.tokens_generated}")
                    elif isinstance(result, dict) and 'usage' in result:
                        logger.info(f"🔢 Token Usage: {json.dumps(result['usage'], indent=2)}")

                logger.info(f"{'='*80}\n")

                return result

            except Exception as e:
                # Calculate duration even on error
                duration_ms = (time.time() - start_time) * 1000

                # ============================================================
                # RESPONSE LOGGING - ERROR
                # ============================================================
                logger.error(f"\n❌ [{api_name}] API RESPONSE - ERROR")
                logger.error(f"⏱️  Duration: {duration_ms:.2f}ms")
                logger.error(f"🚨 Exception Type: {type(e).__name__}")
                logger.error(f"💬 Error Message: {str(e)}")

                # Log additional error details if available
                if hasattr(e, 'response'):
                    logger.error(f"📛 HTTP Status Code: {getattr(e.response, 'status_code', 'N/A')}")
                    if hasattr(e.response, 'text'):
                        error_text = e.response.text[:500]  # Truncate error response
                        logger.error(f"📄 Error Response: {error_text}")

                # Log rate limit or quota exceeded errors
                if 'quota' in str(e).lower() or 'rate limit' in str(e).lower():
                    logger.error(f"⚠️  QUOTA/RATE LIMIT ERROR DETECTED")

                logger.error(f"{'='*80}\n")

                # Re-raise exception to maintain original behavior
                # This ensures the calling code handles the error as expected
                raise

        return wrapper
    return decorator


def _sanitize_auth_data(data: dict) -> dict:
    """
    Remove or truncate sensitive authentication data before logging.

    This helper function identifies sensitive keys and sanitizes their values
    to prevent logging full API keys, OAuth tokens, passwords, or secrets.

    Args:
        data: Dictionary potentially containing sensitive data

    Returns:
        Dictionary with sensitive values truncated to first 10 + last 4 chars

    Security:
        - Sensitive keys: access_token, api_key, password, secret, authorization
        - Values longer than 10 chars are truncated to: "first10...last4"
        - Shorter values are fully redacted to: "***REDACTED***"
    """
    # Create a shallow copy to avoid modifying the original
    sanitized = data.copy()

    # List of sensitive key patterns to look for (case-insensitive)
    sensitive_keys = ['access_token', 'api_key', 'password', 'secret', 'authorization', 'token', 'key']

    for key in sanitized:
        # Check if this key contains any sensitive pattern
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            # Only sanitize string values
            if isinstance(sanitized[key], str):
                value_len = len(sanitized[key])

                # Truncate long values to first 10 + last 4 chars
                if value_len > 14:
                    sanitized[key] = sanitized[key][:10] + "..." + sanitized[key][-4:]
                # Fully redact shorter sensitive values
                elif value_len > 0:
                    sanitized[key] = "***REDACTED***"

    return sanitized

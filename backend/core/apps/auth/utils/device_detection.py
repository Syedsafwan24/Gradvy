"""
Device detection and utility functions for session management
"""

import re
from typing import Dict, Optional
from user_agents import parse


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    # Limit length for security
    return ip[:45]


def parse_user_agent(user_agent_string: str) -> Dict[str, str]:
    """
    Parse user agent string to extract device information.
    
    Args:
        user_agent_string: Raw user agent string from browser
        
    Returns:
        dict: Parsed device information
    """
    if not user_agent_string:
        return {
            'browser': 'Unknown Browser',
            'browser_version': 'Unknown',
            'os': 'Unknown OS',
            'os_version': 'Unknown',
            'device_type': 'Unknown Device',
            'device_brand': 'Unknown',
            'device_model': 'Unknown'
        }
    
    try:
        # Use user-agents library for parsing
        user_agent = parse(user_agent_string)
        
        # Determine device type
        if user_agent.is_mobile:
            device_type = 'Mobile'
        elif user_agent.is_tablet:
            device_type = 'Tablet'  
        elif user_agent.is_pc:
            device_type = 'Desktop'
        else:
            device_type = 'Unknown Device'
        
        # Get browser info
        browser = user_agent.browser.family or 'Unknown Browser'
        browser_version = user_agent.browser.version_string or 'Unknown'
        
        # Get OS info
        os_name = user_agent.os.family or 'Unknown OS'
        os_version = user_agent.os.version_string or 'Unknown'
        
        # Get device info (mainly for mobile)
        device_brand = getattr(user_agent.device, 'brand', None) or 'Unknown'
        device_model = getattr(user_agent.device, 'model', None) or 'Unknown'
        
        return {
            'browser': browser,
            'browser_version': browser_version,
            'os': os_name,
            'os_version': os_version,
            'device_type': device_type,
            'device_brand': device_brand,
            'device_model': device_model
        }
        
    except Exception as e:
        # Fallback to basic parsing if user-agents library fails
        return parse_user_agent_fallback(user_agent_string)


def parse_user_agent_fallback(user_agent_string: str) -> Dict[str, str]:
    """
    Fallback user agent parser using regex patterns.
    
    Args:
        user_agent_string: Raw user agent string
        
    Returns:
        dict: Basic parsed device information
    """
    # Basic browser detection
    browser = 'Unknown Browser'
    if 'Chrome' in user_agent_string and 'Safari' in user_agent_string:
        browser = 'Chrome'
    elif 'Firefox' in user_agent_string:
        browser = 'Firefox'
    elif 'Safari' in user_agent_string and 'Chrome' not in user_agent_string:
        browser = 'Safari'
    elif 'Edge' in user_agent_string:
        browser = 'Edge'
    elif 'Opera' in user_agent_string:
        browser = 'Opera'
    
    # Basic OS detection
    os_name = 'Unknown OS'
    if 'Windows NT' in user_agent_string:
        os_name = 'Windows'
    elif 'Mac OS X' in user_agent_string or 'macOS' in user_agent_string:
        os_name = 'macOS'
    elif 'Linux' in user_agent_string:
        os_name = 'Linux'
    elif 'Android' in user_agent_string:
        os_name = 'Android'
    elif 'iPhone OS' in user_agent_string or 'iOS' in user_agent_string:
        os_name = 'iOS'
    
    # Basic device type detection
    device_type = 'Desktop'
    if 'Mobile' in user_agent_string or 'Android' in user_agent_string:
        device_type = 'Mobile'
    elif 'iPad' in user_agent_string or 'Tablet' in user_agent_string:
        device_type = 'Tablet'
    
    return {
        'browser': browser,
        'browser_version': 'Unknown',
        'os': os_name,
        'os_version': 'Unknown',
        'device_type': device_type,
        'device_brand': 'Unknown',
        'device_model': 'Unknown'
    }


def get_location_info(ip_address: str) -> Dict[str, str]:
    """
    Get location information from IP address.
    
    Note: This is a placeholder implementation. In production,
    you might want to use a service like MaxMind GeoIP2 or similar.
    
    Args:
        ip_address: IP address to look up
        
    Returns:
        dict: Location information
    """
    # Placeholder implementation
    # In production, integrate with a geolocation service
    
    # Skip private/local IPs
    if is_private_ip(ip_address):
        return {
            'country': 'Local Network',
            'country_code': 'LN',
            'city': 'Local',
            'region': 'Local',
            'latitude': None,
            'longitude': None
        }
    
    # For demo purposes, return unknown location
    # In production, use a service like:
    # - MaxMind GeoIP2
    # - IPInfo.io
    # - GeoJS
    # - etc.
    return {
        'country': 'Unknown',
        'country_code': 'XX',
        'city': 'Unknown',
        'region': 'Unknown',
        'latitude': None,
        'longitude': None
    }


def is_private_ip(ip_address: str) -> bool:
    """
    Check if an IP address is private/local.
    
    Args:
        ip_address: IP address to check
        
    Returns:
        bool: True if IP is private/local
    """
    try:
        import ipaddress
        ip = ipaddress.ip_address(ip_address)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        # Invalid IP address
        return True


def generate_device_fingerprint(request) -> str:
    """
    Generate a device fingerprint for additional security.
    
    Args:
        request: Django request object
        
    Returns:
        str: Device fingerprint hash
    """
    import hashlib
    
    # Collect fingerprinting data
    fingerprint_data = []
    
    # User agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    fingerprint_data.append(user_agent)
    
    # Accept headers
    accept = request.META.get('HTTP_ACCEPT', '')
    fingerprint_data.append(accept)
    
    # Accept language
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    fingerprint_data.append(accept_language)
    
    # Accept encoding
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    fingerprint_data.append(accept_encoding)
    
    # DNT header
    dnt = request.META.get('HTTP_DNT', '')
    fingerprint_data.append(dnt)
    
    # Create hash
    fingerprint_string = '|'.join(fingerprint_data)
    fingerprint_hash = hashlib.sha256(fingerprint_string.encode('utf-8')).hexdigest()
    
    return fingerprint_hash[:32]  # First 32 characters


def get_session_info(request) -> Dict[str, str]:
    """
    Get comprehensive session information from request.
    
    Args:
        request: Django request object
        
    Returns:
        dict: Session information
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_info = parse_user_agent(user_agent)
    location_info = get_location_info(ip_address)
    fingerprint = generate_device_fingerprint(request)
    
    return {
        'ip_address': ip_address,
        'user_agent': user_agent,
        'device_info': device_info,
        'location_info': location_info,
        'fingerprint': fingerprint
    }
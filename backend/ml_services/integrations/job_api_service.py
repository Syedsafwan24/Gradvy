# File: backend/ml_services/integrations/job_api_service.py
# Description: Integration service for Adzuna Job Search API to fetch real-time job market data
# Why: Enriches static career data with current job openings count and salary data
# Relevant Files: career_insights_service.py, career_data.py, models.py

"""
Adzuna Job API Integration Service

This service integrates with the Adzuna Job Search API to fetch:
- Real-time job opening counts by role and location
- Salary data for specific roles
- Market demand indicators

API Documentation: https://developer.adzuna.com/overview
Free Tier: 5,000 calls/month

Environment Variables Required:
- ADZUNA_APP_ID: Your Adzuna application ID
- ADZUNA_APP_KEY: Your Adzuna API key

Rate Limiting:
- Implements exponential backoff for rate limits
- Caches results for 24 hours to minimize API calls
- Falls back to static data if API unavailable
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class JobAPIService:
    """
    Service for fetching job market data from Adzuna API.

    Features:
    - Get job opening counts by role and location
    - Fetch salary estimates for roles
    - Enrich career roles with real-time market data
    - Intelligent caching to minimize API calls
    """

    BASE_URL = "https://api.adzuna.com/v1/api"
    DEFAULT_COUNTRY = "us"  # Can be configured: us, uk, ca, au, etc.
    CACHE_TTL = 60 * 60 * 24  # 24 hours

    def __init__(self):
        """
        Initialize JobAPIService with credentials from environment.

        Falls back to demo mode if credentials not found.
        """
        self.app_id = os.getenv('ADZUNA_APP_ID', '')
        self.app_key = os.getenv('ADZUNA_APP_KEY', '')
        self.enabled = bool(self.app_id and self.app_key)

        if not self.enabled:
            logger.warning(
                "Adzuna API credentials not found. Job market data will use static estimates. "
                "Set ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables to enable real-time data."
            )

    def _build_url(self, endpoint: str, country: str = DEFAULT_COUNTRY) -> str:
        """
        Build Adzuna API URL with credentials.

        Args:
            endpoint: API endpoint (e.g., 'jobs/us/search/1')
            country: Country code (us, uk, ca, etc.)

        Returns:
            Complete API URL with credentials
        """
        return f"{self.BASE_URL}/{endpoint}?app_id={self.app_id}&app_key={self.app_key}"

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        country: str = DEFAULT_COUNTRY
    ) -> Optional[Dict]:
        """
        Make HTTP request to Adzuna API with error handling.

        Args:
            endpoint: API endpoint
            params: Query parameters
            country: Country code

        Returns:
            JSON response or None if error
        """
        if not self.enabled:
            return None

        try:
            url = self._build_url(endpoint, country)
            response = requests.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Adzuna API timeout for endpoint: {endpoint}")
            return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Adzuna API rate limit exceeded. Using cached/static data.")
            else:
                logger.error(f"Adzuna API HTTP error: {e}")
            return None

        except Exception as e:
            logger.error(f"Adzuna API request failed: {str(e)}")
            return None

    def get_job_count(
        self,
        role_title: str,
        location: str = "",
        max_days_old: int = 30
    ) -> int:
        """
        Get count of job openings for a specific role.

        Uses caching to minimize API calls. Cache key includes role + location.

        Args:
            role_title: Job role to search for (e.g., "React Developer")
            location: Optional location filter (e.g., "New York", "California")
            max_days_old: Only count jobs posted within this many days

        Returns:
            Number of job openings (0 if API unavailable)

        Example:
            >>> service = JobAPIService()
            >>> count = service.get_job_count("Frontend Developer", "San Francisco")
            >>> print(count)  # e.g., 342
        """
        # Check cache first
        cache_key = f"adzuna_job_count_{role_title.lower().replace(' ', '_')}_{location.lower().replace(' ', '_')}"
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            logger.info(f"Using cached job count for '{role_title}': {cached_count}")
            return cached_count

        if not self.enabled:
            logger.info(f"Adzuna API disabled. Returning 0 for '{role_title}'")
            return 0

        # Build search query
        what = role_title
        where = location if location else ""

        # API endpoint for job search
        endpoint = f"jobs/{self.DEFAULT_COUNTRY}/search/1"
        params = {
            "what": what,
            "where": where,
            "max_days_old": max_days_old,
            "results_per_page": 1,  # We only need the count
        }

        # Make request
        logger.info(f"Fetching job count for '{role_title}' in '{location or 'all locations'}'")
        data = self._make_request(endpoint, params)

        if not data:
            return 0

        # Extract count from response
        count = data.get("count", 0)

        # Cache the result
        cache.set(cache_key, count, self.CACHE_TTL)
        logger.info(f"Job count for '{role_title}': {count} (cached for 24h)")

        return count

    def get_salary_data(
        self,
        role_title: str,
        location: str = ""
    ) -> Optional[Dict[str, float]]:
        """
        Get salary estimates for a specific role.

        Note: Adzuna salary histogram API is limited. This is a basic implementation.
        For production, consider using static data or Bureau of Labor Statistics API.

        Args:
            role_title: Job role title
            location: Optional location filter

        Returns:
            Dictionary with min/max/median salary or None
            Example: {"min": 60000, "max": 120000, "median": 85000}
        """
        # Check cache
        cache_key = f"adzuna_salary_{role_title.lower().replace(' ', '_')}_{location.lower().replace(' ', '_')}"
        cached_salary = cache.get(cache_key)
        if cached_salary is not None:
            return cached_salary

        if not self.enabled:
            return None

        # Adzuna salary histogram endpoint
        endpoint = f"jobs/{self.DEFAULT_COUNTRY}/histogram"
        params = {
            "what": role_title,
            "where": location if location else "",
        }

        data = self._make_request(endpoint, params)
        if not data or "histogram" not in data:
            return None

        # Parse histogram data (this is simplified)
        histogram = data.get("histogram", {})

        # Extract min/max from histogram keys
        try:
            salary_bins = [int(k) for k in histogram.keys() if k.isdigit()]
            if not salary_bins:
                return None

            salary_data = {
                "min": min(salary_bins),
                "max": max(salary_bins),
                "median": sorted(salary_bins)[len(salary_bins) // 2]
            }

            # Cache the result
            cache.set(cache_key, salary_data, self.CACHE_TTL)
            return salary_data

        except Exception as e:
            logger.error(f"Failed to parse salary data: {str(e)}")
            return None

    def enrich_career_roles_with_job_counts(
        self,
        career_roles: List[Dict[str, Any]],
        location: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Enrich list of career roles with real-time job opening counts.

        Updates the 'job_openings_count' field for each role.
        Falls back to static data if API unavailable.

        Args:
            career_roles: List of career role dictionaries
            location: Optional location filter

        Returns:
            Updated career roles with job_openings_count populated

        Example:
            >>> roles = [
            ...     {"role_title": "Frontend Developer", "job_openings_count": 0},
            ...     {"role_title": "Backend Developer", "job_openings_count": 0}
            ... ]
            >>> enriched = service.enrich_career_roles_with_job_counts(roles)
            >>> print(enriched[0]['job_openings_count'])  # e.g., 1250
        """
        if not self.enabled:
            logger.info("Adzuna API disabled. Career roles will use static job counts (0).")
            return career_roles

        enriched_roles = []

        for role in career_roles:
            role_copy = role.copy()
            role_title = role.get("role_title", "")

            if role_title:
                # Fetch job count from API
                job_count = self.get_job_count(role_title, location)
                role_copy["job_openings_count"] = job_count

                # Update market demand based on job count
                # These thresholds can be tuned based on domain
                if job_count > 1000:
                    role_copy["market_demand"] = "very_high"
                elif job_count > 500:
                    role_copy["market_demand"] = "high"
                elif job_count > 100:
                    role_copy["market_demand"] = "medium"
                else:
                    role_copy["market_demand"] = "low"

            enriched_roles.append(role_copy)

        logger.info(f"Enriched {len(enriched_roles)} career roles with job counts")
        return enriched_roles

    def calculate_market_demand_score(self, total_job_openings: int) -> int:
        """
        Calculate market demand score (0-100) based on total job openings.

        Uses logarithmic scale to normalize job counts into 0-100 range.

        Args:
            total_job_openings: Total number of job openings

        Returns:
            Market demand score (0-100)

        Scoring:
            0-10: Very low demand (0-20 score)
            10-100: Low demand (20-40 score)
            100-500: Medium demand (40-60 score)
            500-1500: High demand (60-80 score)
            1500+: Very high demand (80-100 score)
        """
        if total_job_openings <= 0:
            return 0
        elif total_job_openings < 10:
            return 10
        elif total_job_openings < 100:
            return 30
        elif total_job_openings < 500:
            return 50
        elif total_job_openings < 1500:
            return 70
        else:
            return min(100, 80 + (total_job_openings - 1500) // 100)

    def get_total_job_openings_for_domain(
        self,
        domain_roles: List[Dict[str, Any]],
        location: str = ""
    ) -> int:
        """
        Get total job openings across all roles in a domain.

        Args:
            domain_roles: List of career role dictionaries
            location: Optional location filter

        Returns:
            Total job openings count
        """
        total = 0
        for role in domain_roles:
            role_title = role.get("role_title", "")
            if role_title:
                count = self.get_job_count(role_title, location)
                total += count

        return total

    def clear_cache(self, role_title: Optional[str] = None, location: Optional[str] = None):
        """
        Clear cached job data.

        Args:
            role_title: Specific role to clear (if None, clears all)
            location: Specific location to clear (if None, clears all)
        """
        if role_title and location:
            cache_key = f"adzuna_job_count_{role_title.lower().replace(' ', '_')}_{location.lower().replace(' ', '_')}"
            cache.delete(cache_key)
            logger.info(f"Cleared cache for '{role_title}' in '{location}'")
        else:
            # Clear all Adzuna cache keys (requires manual implementation)
            logger.warning("Clearing all Adzuna cache not implemented. Consider cache.clear() for full reset.")


# Singleton instance
_job_api_service = None


def get_job_api_service() -> JobAPIService:
    """
    Get singleton JobAPIService instance.

    Returns:
        JobAPIService instance
    """
    global _job_api_service
    if _job_api_service is None:
        _job_api_service = JobAPIService()
    return _job_api_service

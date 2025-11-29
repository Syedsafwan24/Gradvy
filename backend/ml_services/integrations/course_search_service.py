"""
backend/ml_services/integrations/course_search_service.py
Course search and ranking service for YouTube, Udemy, and other platforms
Why: Finds and ranks real courses based on user preferences and roadmap topics
RELEVANT FILES: roadmap_service.py, learning_path_service.py, settings.py
"""

import logging
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import urlencode
from django.conf import settings

# Import external API logger for comprehensive API call tracking
from ml_services.utils.external_api_logger import log_external_api_call


logger = logging.getLogger(__name__)


@dataclass
class Course:
    """
    Represents a single course/learning resource.
    """
    title: str
    url: str
    platform: str  # 'youtube', 'udemy', 'coursera', 'preview', etc.
    description: str = ""
    instructor: str = ""
    duration_hours: float = 0.0
    rating: float = 0.0
    num_ratings: int = 0
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    price: str = "free"  # 'free', 'paid', or actual price
    thumbnail_url: str = ""
    published_date: str = ""
    language: str = "english"
    tags: List[str] = field(default_factory=list)
    is_mock: bool = False  # True if this is preview/mock data
    source: str = "youtube"  # 'youtube', 'udemy', 'coursera', 'preview'


@dataclass
class ScoredCourse:
    """
    Course with relevance score based on user preferences.
    """
    course: Course
    relevance_score: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)


class CourseSearchService:
    """
    Service for searching and ranking courses from multiple platforms.

    Integrations:
    1. YouTube Data API v3 - Free video tutorials
    2. Udemy Affiliate API - Paid structured courses
    3. Future: Coursera, edX, Pluralsight, etc.

    Ranking Algorithm:
    - Platform preference match (30 points)
    - Rating quality (25 points)
    - Difficulty match (20 points)
    - Duration preference (15 points)
    - Content type match (10 points)
    Total: 100 points
    """

    def __init__(self):
        """Initialize course search service with API credentials."""
        # YouTube API configuration
        self.youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
        self.youtube_api_url = "https://www.googleapis.com/youtube/v3/search"

        # Udemy API configuration
        self.udemy_client_id = getattr(settings, 'UDEMY_CLIENT_ID', '')
        self.udemy_client_secret = getattr(settings, 'UDEMY_CLIENT_SECRET', '')
        self.udemy_affiliate_id = getattr(settings, 'UDEMY_AFFILIATE_ID', '')
        self.udemy_api_url = "https://www.udemy.com/api-2.0/courses/"

        # HTTP session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Gradvy-Learning-Platform/1.0'
        })

        # Simple in-memory cache
        self._cache = {}

        # Configuration flags for course search behavior
        self.use_mock = getattr(settings, 'USE_MOCK_COURSES', True)
        self.require_real = getattr(settings, 'REQUIRE_REAL_COURSES', False)

        # Log configuration status
        logger.info(f"📚 Course Search Config: Mock={self.use_mock}, Require Real={self.require_real}")
        logger.info(f"🔑 YouTube API: {'✓ Configured' if self.youtube_api_key else '✗ Not configured'}")

        # Udemy configuration status with affiliate tracking
        if self.udemy_client_id and self.udemy_client_secret:
            affiliate_status = "with affiliate tracking" if self.udemy_affiliate_id else "without affiliate tracking"
            logger.info(f"🔑 Udemy API: ✓ Configured ({affiliate_status})")
        else:
            logger.info(f"🔑 Udemy API: ✗ Not configured (apply at https://www.udemy.com/affiliate/)")

    def enrich_search_query(
        self,
        base_topic: str,
        user_preferences: Dict,
        learning_goal: Optional[str] = None,
        node_context: Optional[Dict] = None
    ) -> str:
        """
        Enrich search query with user preferences to get more relevant course results.

        Applies 4 enrichment layers:
        1. Learning goal context for generic titles (e.g., "Introduction" → "Introduction to Mobile Development")
        2. Difficulty level keywords (e.g., "beginner tutorial", "advanced")
        3. Learning style keywords (e.g., "project", "course", "tutorial")
        4. Duration hints (e.g., "quick", "complete")

        Args:
            base_topic: Base topic from roadmap node (e.g., "React Hooks", "Introduction")
            user_preferences: User's basic_info and content_preferences
            learning_goal: User's primary learning goal (e.g., "mobile_dev", "web_dev")
            node_context: Additional context about the roadmap node (difficulty, category)

        Returns:
            Enriched query string for YouTube/Udemy search

        Examples:
            "Introduction" + mobile_dev + beginner → "Introduction to Mobile Development beginner tutorial"
            "React Hooks" + advanced + hands_on → "React Hooks advanced project"
            "Python Basics" + beginner + short → "Python Basics beginner course quick"
        """
        query_parts = []

        # ENRICHMENT 1: Generic title fix - Add learning goal context for vague titles
        # Generic keywords that need context from the user's learning goal
        generic_keywords = ['introduction', 'getting started', 'basics', 'fundamentals', 'overview']

        if learning_goal and any(kw in base_topic.lower() for kw in generic_keywords):
            # Add learning goal context to make query specific
            goal_text = self._format_learning_goal(learning_goal)
            query_parts.append(f"{base_topic} to {goal_text}")
        else:
            # Use base topic as-is
            query_parts.append(base_topic)

        basic_info = user_preferences.get('basic_info', {})
        content_prefs = user_preferences.get('content_preferences', {})

        # ENRICHMENT 2: Difficulty level keywords
        # Add difficulty keywords to match user's experience level
        experience = basic_info.get('experience_level', 'intermediate')
        difficulty_map = {
            'complete_beginner': 'beginner tutorial',
            'some_basics': 'beginner',
            'intermediate': '',  # Don't add keyword for intermediate (most common)
            'advanced': 'advanced'
        }
        difficulty_keyword = difficulty_map.get(experience)
        if difficulty_keyword:
            query_parts.append(difficulty_keyword)

        # ENRICHMENT 3: Learning style keywords
        # Add keywords based on preferred learning style
        styles = basic_info.get('learning_style', [])
        if 'hands_on' in styles:
            query_parts.append('project')  # Prefer project-based content
        elif 'videos' in styles or 'visual' in styles:
            query_parts.append('course')  # Prefer structured courses
        elif 'reading' in styles:
            query_parts.append('tutorial')  # Prefer text-based tutorials

        # ENRICHMENT 4: Duration preference hints
        # Add duration keywords based on user's content preference
        duration = content_prefs.get('duration_preference', 'mixed')
        if duration == 'short':
            query_parts.append('quick')  # Prefer shorter content
        elif duration == 'long':
            query_parts.append('complete')  # Prefer comprehensive content

        # Build final enriched query
        enriched = ' '.join(query_parts)

        # Log enrichment for debugging and transparency
        if enriched != base_topic:
            logger.info(f"🔍 Query enriched: '{base_topic}' → '{enriched}'")

        return enriched

    def _format_learning_goal(self, learning_goal: str) -> str:
        """
        Format learning goal slug to human-readable text for query enrichment.

        Args:
            learning_goal: Goal slug (e.g., "web_dev", "ai_ml")

        Returns:
            Formatted goal text (e.g., "Web Development", "AI and Machine Learning")
        """
        # Mapping of goal slugs to natural language
        goal_mapping = {
            'web_dev': 'Web Development',
            'mobile_dev': 'Mobile Development',
            'ai_ml': 'AI and Machine Learning',
            'data_science': 'Data Science',
            'devops': 'DevOps',
            'cybersecurity': 'Cybersecurity',
            'blockchain': 'Blockchain',
            'backend_dev': 'Backend Development',
            'full_stack': 'Full Stack Development',
            'game_dev': 'Game Development'
        }
        return goal_mapping.get(learning_goal, learning_goal.replace('_', ' ').title())

    def search_courses(
        self,
        topic: str,
        user_preferences: Dict,
        max_results: int = 10
    ) -> List[ScoredCourse]:
        """
        Search for courses across multiple platforms and rank by relevance.

        Args:
            topic: Topic/skill to search for (e.g., "React Hooks", "Python OOP")
            user_preferences: User's learning preferences
            max_results: Maximum number of courses to return

        Returns:
            List of ScoredCourse objects sorted by relevance
        """
        # Check cache
        cache_key = f"{topic}_{max_results}"
        if cache_key in self._cache:
            logger.info(f"📦 Using cached courses for topic: {topic}")
            return self._rank_courses(self._cache[cache_key], user_preferences)[:max_results]

        all_courses = []

        # Try real APIs first
        if self.youtube_api_key:
            youtube_courses = self._search_youtube(topic, user_preferences, max_results=5)
            all_courses.extend(youtube_courses)
        else:
            logger.warning("⚠️ YouTube API key not configured - skipping YouTube search")

        if self.udemy_client_id and self.udemy_client_secret:
            udemy_courses = self._search_udemy(topic, max_results=5)
            all_courses.extend(udemy_courses)
        else:
            logger.warning("⚠️ Udemy API credentials not configured - skipping Udemy search")

        # Smart fallback logic based on configuration
        if not all_courses:
            if self.require_real:
                # Production mode - fail if no real courses found
                error_msg = f"No real courses found for '{topic}'. Configure API keys or set REQUIRE_REAL_COURSES=False"
                logger.error(f"❌ REQUIRE_REAL_COURSES=True but no API courses found for '{topic}'")
                raise ValueError(error_msg)

            # ALWAYS provide fallback courses to prevent empty lists and validation errors
            # This ensures learning path generation never fails due to empty course lists
            logger.warning(f"⚠️ No real courses found for '{topic}' - using fallback preview data to prevent validation errors")
            all_courses = self._create_mock_courses(topic)

        # Cache results
        self._cache[cache_key] = all_courses

        # Rank and return top courses
        ranked_courses = self._rank_courses(all_courses, user_preferences)
        return ranked_courses[:max_results]

    def _search_youtube(self, topic: str, user_preferences: Dict, max_results: int = 5) -> List[Course]:
        """
        Search for video tutorials and playlists on YouTube.

        Uses YouTube Data API v3 to search for educational content.
        Respects user's content_structure preference to control video/playlist mix.

        Args:
            topic: Search query topic
            user_preferences: User's learning preferences
            max_results: Maximum number of results

        Returns:
            List of Course objects from YouTube (videos and/or playlists)
        """
        all_courses = []

        # Get content_structure preference from user preferences
        content_structure = user_preferences.get('content_preferences', {}).get('content_structure', 'mixed')

        if content_structure == 'videos_only':
            # Search only individual videos
            video_courses = self._search_youtube_videos(topic, max_results=max_results)
            all_courses.extend(video_courses)
            logger.info(f"✅ Found {len(all_courses)} YouTube videos (videos_only mode) for '{topic}'")
        elif content_structure == 'playlists_preferred':
            # Search only playlists
            playlist_courses = self._search_youtube_playlists(topic, max_results=max_results)
            all_courses.extend(playlist_courses)
            logger.info(f"✅ Found {len(all_courses)} YouTube playlists (playlists_preferred mode) for '{topic}'")
        else:  # 'mixed' (default)
            # Search for individual videos (60% of results)
            video_count = int(max_results * 0.6)
            if video_count > 0:
                video_courses = self._search_youtube_videos(topic, max_results=video_count)
                all_courses.extend(video_courses)

            # Search for playlists (40% of results)
            playlist_count = int(max_results * 0.4)
            if playlist_count > 0:
                playlist_courses = self._search_youtube_playlists(topic, max_results=playlist_count)
                all_courses.extend(playlist_courses)

            logger.info(f"✅ Found {len(all_courses)} YouTube courses ({len([c for c in all_courses if '📚' not in c.title])} videos, {len([c for c in all_courses if '📚' in c.title])} playlists) for '{topic}'")

        return all_courses

    @log_external_api_call(
        api_name="YouTube Video Search",
        quota_units=100,  # Video search costs 100 quota units
        include_headers=False,  # Headers not needed for YouTube API
        truncate_response_at=3000  # Truncate large video response data
    )
    def _search_youtube_videos(self, topic: str, max_results: int = 5) -> List[Course]:
        """
        Search for individual video tutorials on YouTube.

        Args:
            topic: Search query topic
            max_results: Maximum number of results

        Returns:
            List of Course objects from YouTube videos
        """
        try:
            # Build search parameters
            params = {
                'part': 'snippet',
                'q': topic,  # Direct topic search, no hardcoded suffix
                'type': 'video',
                'videoDefinition': 'high',
                'maxResults': max_results,
                'key': self.youtube_api_key,
                'relevanceLanguage': 'en',
                'order': 'relevance'
            }

            # Make API request
            logger.info(f"🔍 Searching YouTube videos for: {topic}")
            response = self.session.get(self.youtube_api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            courses = []

            # Parse YouTube video results
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId', '')

                # Get video details for duration and ratings
                video_details = self._get_youtube_video_details(video_id)

                course = Course(
                    title=snippet.get('title', ''),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    platform='youtube',
                    description=snippet.get('description', ''),
                    instructor=snippet.get('channelTitle', ''),
                    duration_hours=video_details.get('duration_hours', 0.5),
                    rating=video_details.get('rating', 4.5),
                    num_ratings=video_details.get('like_count', 0),  # Use likes as rating count (semantic match)
                    difficulty='intermediate',
                    price='free',
                    thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    published_date=snippet.get('publishedAt', ''),
                    language='english',
                    tags=[topic]
                )
                courses.append(course)

            return courses

        except requests.RequestException as e:
            # Check for YouTube API quota exceeded error
            if hasattr(e.response, 'status_code') and e.response.status_code == 403:
                try:
                    error_data = e.response.json()
                    if 'quotaExceeded' in str(error_data):
                        logger.error(f"⚠️ YouTube API quota exceeded! Daily limit reached (10,000 units/day)")
                        logger.info(f"ℹ️ Falling back to mock data for topic: '{topic}'")
                        return []
                except:
                    pass

            logger.error(f"❌ YouTube API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing YouTube results: {e}")
            return []

    @log_external_api_call(
        api_name="YouTube Playlist Search",
        quota_units=100,  # Playlist search costs 100 quota units
        include_headers=False,
        truncate_response_at=3000
    )
    def _search_youtube_playlists(self, topic: str, max_results: int = 3) -> List[Course]:
        """
        Search for structured course playlists on YouTube.

        Playlists are preferred for learning as they provide structured, sequential content.

        Args:
            topic: Search query topic
            max_results: Maximum number of playlists to return

        Returns:
            List of Course objects from YouTube playlists (marked with 📚 emoji)
        """
        try:
            # Build search parameters for playlists
            # Dynamic query - no hardcoded suffixes, let YouTube ranking find best matches
            params = {
                'part': 'snippet',
                'q': topic,  # Use topic directly for dynamic, personalized search
                'type': 'playlist',
                'maxResults': max_results,
                'key': self.youtube_api_key,
                'relevanceLanguage': 'en',
                'order': 'relevance'
            }

            # Make API request
            logger.info(f"🔍 Searching YouTube playlists for: {topic}")
            response = self.session.get(self.youtube_api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            courses = []

            # Parse YouTube playlist results
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                playlist_id = item.get('id', {}).get('playlistId', '')

                # Get playlist details (video count, total duration)
                playlist_details = self._get_youtube_playlist_details(playlist_id)

                # Mark playlists with 📚 emoji for visual distinction
                course = Course(
                    title=f"📚 {snippet.get('title', '')}",
                    url=f"https://www.youtube.com/playlist?list={playlist_id}",
                    platform='youtube',
                    description=snippet.get('description', ''),
                    instructor=snippet.get('channelTitle', ''),
                    duration_hours=playlist_details.get('total_duration_hours', 5.0),
                    rating=4.5,  # Playlists don't have individual ratings, use default
                    num_ratings=playlist_details.get('video_count', 10),
                    difficulty='intermediate',
                    price='free',
                    thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    published_date=snippet.get('publishedAt', ''),
                    language='english',
                    tags=[topic, 'playlist']
                )
                courses.append(course)

            return courses

        except requests.RequestException as e:
            logger.error(f"❌ YouTube playlist search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing YouTube playlist results: {e}")
            return []

    @log_external_api_call(
        api_name="YouTube Video Details",
        quota_units=1,  # Video details costs 1 quota unit per video
        include_headers=False,
        truncate_response_at=1000
    )
    def _get_youtube_video_details(self, video_id: str) -> Dict:
        """
        Get detailed information about a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with duration, rating, and view count
        """
        try:
            params = {
                'part': 'contentDetails,statistics',
                'id': video_id,
                'key': self.youtube_api_key
            }

            response = self.session.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params=params,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            if not data.get('items'):
                return {}

            item = data['items'][0]
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})

            # Parse ISO 8601 duration (e.g., PT15M33S)
            duration = content_details.get('duration', 'PT0M')
            duration_hours = self._parse_youtube_duration(duration)

            # Calculate engagement-based rating from likes, comments, and views
            engagement_rating = self._calculate_engagement_score(statistics)

            return {
                'duration_hours': duration_hours,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'rating': engagement_rating  # Dynamic rating based on engagement metrics
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to get YouTube video details: {e}")
            return {}

    @log_external_api_call(
        api_name="YouTube Playlist Details",
        quota_units=1,  # Playlist details costs 1 quota unit
        include_headers=False,
        truncate_response_at=1000
    )
    def _get_youtube_playlist_details(self, playlist_id: str) -> Dict:
        """
        Get detailed information about a YouTube playlist.

        Fetches video count and estimates total duration for the playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            Dictionary with video_count and total_duration_hours
        """
        try:
            # Get playlist information
            params = {
                'part': 'contentDetails',
                'id': playlist_id,
                'key': self.youtube_api_key
            }

            response = self.session.get(
                "https://www.googleapis.com/youtube/v3/playlists",
                params=params,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            if not data.get('items'):
                return {'video_count': 10, 'total_duration_hours': 5.0}

            item = data['items'][0]
            content_details = item.get('contentDetails', {})
            video_count = content_details.get('itemCount', 10)

            # Estimate total duration: assume average 15 minutes per video
            # This avoids making additional API calls for each video in playlist
            estimated_hours = (video_count * 15) / 60.0  # Convert minutes to hours

            return {
                'video_count': video_count,
                'total_duration_hours': round(estimated_hours, 1)
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to get YouTube playlist details: {e}")
            # Return reasonable defaults
            return {
                'video_count': 10,
                'total_duration_hours': 5.0
            }

    def _parse_youtube_duration(self, duration_str: str) -> float:
        """
        Parse YouTube ISO 8601 duration to hours.

        Example: PT15M33S -> 0.26 hours

        Args:
            duration_str: ISO 8601 duration string

        Returns:
            Duration in hours
        """
        import re

        # Extract hours, minutes, seconds
        hours_match = re.search(r'(\d+)H', duration_str)
        minutes_match = re.search(r'(\d+)M', duration_str)
        seconds_match = re.search(r'(\d+)S', duration_str)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

        total_hours = hours + (minutes / 60.0) + (seconds / 3600.0)
        return round(total_hours, 2)

    def _calculate_engagement_score(self, statistics: dict) -> float:
        """
        Calculate engagement-based rating from YouTube video statistics.

        Uses likes, comments, and views to estimate video quality on 0-5 scale.
        Formula: (Like_Ratio * 0.5) + (Comment_Engagement * 0.3) + (View_Popularity * 0.2)
        Result scaled to 2.5-5.0 range for realistic ratings.

        Args:
            statistics: YouTube video statistics dict with viewCount, likeCount, commentCount

        Returns:
            Engagement score between 2.5 and 5.0
        """
        import math

        # Extract metrics (default to 0 if not available)
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))

        # Default score for videos with no views
        if view_count == 0:
            return 3.0

        # 1. Like Ratio (0-1): likes per 100 views
        # High-quality videos typically get 5-10 likes per 100 views
        like_ratio = min(like_count / max(view_count / 100, 1), 1.0)

        # 2. Comment Engagement (0-1): comments per 1000 views
        # Engaging videos get 1-3 comments per 1000 views
        comment_engagement = min(comment_count / max(view_count / 1000, 1), 1.0)

        # 3. View Popularity (0-1): logarithmic scale
        # Videos with 1M+ views score near 1.0, 1K views score ~0.5
        view_popularity = min(math.log10(view_count + 1) / 6.0, 1.0)

        # Weighted score (like ratio most important, then comments, then popularity)
        engagement_score = (like_ratio * 0.5) + (comment_engagement * 0.3) + (view_popularity * 0.2)

        # Convert 0-1 scale to 2.5-5.0 rating scale
        # This ensures minimum rating of 2.5 (poor) and max of 5.0 (excellent)
        rating = 2.5 + (engagement_score * 2.5)

        return round(rating, 1)

    def _generate_udemy_affiliate_link(self, course_url: str) -> str:
        """
        Generate Udemy affiliate link with tracking parameters.

        Adds affiliate tracking to Udemy course URLs for commission tracking.
        If affiliate ID is not configured, returns the original URL.

        Args:
            course_url: Original Udemy course URL (e.g., "/course/python-bootcamp/")

        Returns:
            Full Udemy URL with affiliate tracking if configured, otherwise standard URL
        """
        # Build base URL
        base_url = f"https://www.udemy.com{course_url}"

        # Add affiliate tracking if configured
        if self.udemy_affiliate_id:
            # Udemy affiliate links use referralCode parameter
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}referralCode={self.udemy_affiliate_id}"

        return base_url

    @log_external_api_call(
        api_name="Udemy Course Search",
        sanitize_auth=True,  # Sanitize Basic Auth credentials
        include_headers=False,
        truncate_response_at=3000
    )
    def _search_udemy(self, topic: str, max_results: int = 5) -> List[Course]:
        """
        Search for courses on Udemy.

        Uses Udemy Affiliate API to search for paid courses.

        Args:
            topic: Search query topic
            max_results: Maximum number of results

        Returns:
            List of Course objects from Udemy
        """
        try:
            # Build search parameters
            params = {
                'search': topic,
                'page_size': max_results,
                'ordering': 'relevance',
                'price': 'price-free,price-paid'
            }

            # Make API request with Basic Auth
            logger.info(f"🔍 Searching Udemy for: {topic}")
            response = self.session.get(
                self.udemy_api_url,
                params=params,
                auth=(self.udemy_client_id, self.udemy_client_secret),
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            courses = []

            # Parse Udemy course results
            for item in data.get('results', []):
                # Determine price
                price = 'free' if item.get('is_free', False) else item.get('price', 'paid')

                # Map Udemy difficulty level
                difficulty_map = {
                    'Beginner Level': 'beginner',
                    'Intermediate Level': 'intermediate',
                    'Expert Level': 'advanced',
                    'All Levels': 'intermediate'
                }
                difficulty = difficulty_map.get(
                    item.get('instructional_level', 'All Levels'),
                    'intermediate'
                )

                # Generate affiliate link for commission tracking
                course_url = self._generate_udemy_affiliate_link(item.get('url', ''))

                course = Course(
                    title=item.get('title', ''),
                    url=course_url,  # Use affiliate link with tracking
                    platform='udemy',
                    description=item.get('headline', ''),
                    instructor=', '.join([i.get('display_name', '') for i in item.get('visible_instructors', [])]),
                    duration_hours=item.get('content_info_short', '').replace(' total hours', '').strip() or 0,
                    rating=item.get('avg_rating', 0.0),
                    num_ratings=item.get('num_reviews', 0),
                    difficulty=difficulty,
                    price=str(price),
                    thumbnail_url=item.get('image_480x270', ''),
                    published_date=item.get('published_time', ''),
                    language=item.get('locale', {}).get('english_title', 'english'),
                    tags=[topic]
                )
                courses.append(course)

            logger.info(f"✅ Found {len(courses)} Udemy courses for '{topic}'")
            return courses

        except requests.RequestException as e:
            logger.error(f"❌ Udemy API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing Udemy results: {e}")
            return []

    def _create_mock_courses(self, topic: str) -> List[Course]:
        """
        Create preview mock courses for development when APIs are not configured.

        These courses are clearly labeled as preview data and use example.com URLs
        to avoid confusion with real course platforms.

        Args:
            topic: Topic to create mock courses for

        Returns:
            List of mock Course objects with clear preview indicators
        """
        topic_slug = topic.lower().replace(' ', '-')

        mock_courses = [
            Course(
                title=f"🎓 PREVIEW: {topic} - Complete Tutorial",
                url=f"https://example.com/preview/{topic_slug}-complete",
                platform='preview',
                description=f"[Preview Data] Comprehensive tutorial covering {topic} fundamentals and advanced concepts. Configure YouTube/Udemy API keys for real courses.",
                instructor="Preview Instructor",
                duration_hours=2.5,
                rating=4.5,
                num_ratings=1500,
                difficulty='intermediate',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"🎓 PREVIEW: Mastering {topic}",
                url=f"https://example.com/preview/{topic_slug}-mastery",
                platform='preview',
                description=f"[Preview Data] In-depth course on {topic} with hands-on projects. Configure YouTube/Udemy API keys for real courses.",
                instructor="Preview Expert",
                duration_hours=8.0,
                rating=4.7,
                num_ratings=5000,
                difficulty='intermediate',
                price='$49.99',
                thumbnail_url='',
                language='english',
                tags=[topic, 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"🎓 PREVIEW: {topic} Crash Course for Beginners",
                url=f"https://example.com/preview/{topic_slug}-beginner",
                platform='preview',
                description=f"[Preview Data] Quick introduction to {topic} for complete beginners. Configure YouTube/Udemy API keys for real courses.",
                instructor="Preview Channel",
                duration_hours=1.0,
                rating=4.3,
                num_ratings=800,
                difficulty='beginner',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'beginner', 'preview'],
                is_mock=True,
                source='preview'
            )
        ]

        return mock_courses

    def _rank_courses(
        self,
        courses: List[Course],
        user_preferences: Dict
    ) -> List[ScoredCourse]:
        """
        Rank courses based on user preferences using ENHANCED dynamic scoring algorithm.

        FULLY PERSONALIZED - Uses ALL user preferences, no hardcoded patterns.

        Enhanced Scoring breakdown:
        - Platform preference match (25 points)
        - Rating quality (20 points)
        - Difficulty match (20 points)
        - Duration preference (15 points)
        - Content type/learning style match (10 points)
        - Language preference match (5 points)
        - Instructor rating threshold (5 points)
        Total: 100 points

        Args:
            courses: List of courses to rank
            user_preferences: User's learning preferences

        Returns:
            List of ScoredCourse objects sorted by relevance score
        """
        content_prefs = user_preferences.get('content_preferences', {})
        basic_info = user_preferences.get('basic_info', {})

        # Extract ALL user preferences (fully dynamic - no hardcoded defaults)
        preferred_platforms = content_prefs.get('preferred_platforms', [])
        user_difficulty = basic_info.get('experience_level', 'intermediate')
        duration_pref = content_prefs.get('duration_preference', 'mixed')
        learning_styles = basic_info.get('learning_style', [])

        # NEW: Additional preference-based scoring factors
        language_preference = content_prefs.get('language_preference', ['english'])
        min_instructor_rating = content_prefs.get('instructor_ratings_min', 3.0)

        # Map experience level to difficulty
        difficulty_map = {
            'complete_beginner': 'beginner',
            'some_basics': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }
        preferred_difficulty = difficulty_map.get(user_difficulty, 'intermediate')

        scored_courses = []

        for course in courses:
            score = 0.0
            breakdown = {}

            # 1. Platform preference (25 points) - REDUCED to balance new factors
            if course.platform in preferred_platforms:
                platform_score = 25.0
            elif not preferred_platforms:  # No preference
                platform_score = 12.5
            else:
                platform_score = 5.0
            score += platform_score
            breakdown['platform'] = platform_score

            # 2. Rating quality (20 points) - REDUCED, more balanced
            # Scale rating from 0-5 to 0-20
            rating_score = (course.rating / 5.0) * 20.0
            # Boost for high number of ratings (reliability)
            if course.num_ratings > 1000:
                rating_score += 2.0
            elif course.num_ratings > 5000:
                rating_score += 3.0
            score += rating_score
            breakdown['rating'] = rating_score

            # 3. Difficulty match (20 points) - UNCHANGED
            if course.difficulty == preferred_difficulty:
                difficulty_score = 20.0
            elif (course.difficulty == 'intermediate' and preferred_difficulty in ['beginner', 'advanced']):
                difficulty_score = 10.0
            else:
                difficulty_score = 5.0
            score += difficulty_score
            breakdown['difficulty'] = difficulty_score

            # 4. Duration preference (15 points) - UNCHANGED
            duration_score = self._score_duration(course.duration_hours, duration_pref)
            score += duration_score
            breakdown['duration'] = duration_score

            # 5. Content type/learning style match (10 points) - ENHANCED with more styles
            content_score = 5.0  # Base score
            if 'videos' in learning_styles and course.platform == 'youtube':
                content_score = 10.0
            elif 'hands_on' in learning_styles and course.platform in ['udemy', 'coursera']:
                content_score = 9.0
            elif 'reading' in learning_styles and course.platform in ['medium', 'dev_to']:
                content_score = 10.0
            elif 'visual' in learning_styles and course.platform == 'youtube':
                content_score = 10.0
            score += content_score
            breakdown['content_type'] = content_score

            # 6. Language preference match (5 points) - NEW!
            language_score = 0.0
            if course.language.lower() in [lang.lower() for lang in language_preference]:
                language_score = 5.0
            elif not language_preference or course.language.lower() == 'english':
                language_score = 2.5  # Default partial score for English
            score += language_score
            breakdown['language'] = language_score

            # 7. Instructor rating threshold (5 points) - NEW!
            # Reward courses that meet user's minimum instructor rating requirement
            instructor_score = 0.0
            if course.rating >= min_instructor_rating:
                # Scale based on how much it exceeds minimum
                excess = course.rating - min_instructor_rating
                instructor_score = min(5.0, 2.5 + (excess * 1.0))  # Base 2.5 + bonus
            score += instructor_score
            breakdown['instructor_rating'] = instructor_score

            # 8. Playlist/structure bonus (5 points) - KEPT for structured learning
            # Playlists provide structured, sequential learning paths
            playlist_bonus = 0
            if '📚' in course.title or 'playlist' in course.tags:
                playlist_bonus = 5.0
                score += playlist_bonus
                breakdown['playlist_bonus'] = playlist_bonus

            scored_course = ScoredCourse(
                course=course,
                relevance_score=round(score, 2),
                score_breakdown=breakdown
            )
            scored_courses.append(scored_course)

        # Sort by relevance score (descending)
        scored_courses.sort(key=lambda x: x.relevance_score, reverse=True)

        return scored_courses

    def _score_duration(self, duration_hours: float, duration_pref: str) -> float:
        """
        Score course based on duration preference.

        Args:
            duration_hours: Course duration in hours
            duration_pref: User's duration preference ('short', 'medium', 'long', 'mixed')

        Returns:
            Score between 0 and 15
        """
        if duration_pref == 'short' and duration_hours < 3:
            return 15.0
        elif duration_pref == 'medium' and 3 <= duration_hours <= 10:
            return 15.0
        elif duration_pref == 'long' and duration_hours > 10:
            return 15.0
        elif duration_pref == 'mixed':
            return 10.0  # Neutral score for mixed preference
        else:
            return 5.0  # Partial score for mismatch

    def clear_cache(self):
        """Clear the course search cache."""
        self._cache.clear()
        logger.info("🗑️ Course search cache cleared")

"""
backend/ml_services/integrations/course_search_service.py
Course search and ranking service for YouTube, Udemy, and other platforms
Why: Finds and ranks real courses based on user preferences and roadmap topics
RELEVANT FILES: roadmap_service.py, learning_path_service.py, settings.py
"""

import logging
import requests
import feedparser
import time
from functools import wraps
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import urlencode
from django.conf import settings
from datetime import datetime, timedelta

# Import external API logger for comprehensive API call tracking
from ml_services.utils.external_api_logger import log_external_api_call


logger = logging.getLogger(__name__)


def rate_limit(calls_per_second: float = 1.0):
    """
    Rate limiting decorator to ensure ethical API usage.

    Prevents overwhelming third-party APIs by limiting request rate.
    Uses a simple time-based throttling mechanism.

    Args:
        calls_per_second: Maximum API calls per second (default: 1.0)

    Usage:
        @rate_limit(calls_per_second=0.5)  # Max 1 call every 2 seconds
        def api_call():
            pass
    """
    min_interval = 1.0 / calls_per_second

    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Calculate time since last call
            elapsed = time.time() - last_called[0]

            # Wait if needed to respect rate limit
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"⏱️ Rate limiting: waiting {sleep_time:.2f}s before {func.__name__}")
                time.sleep(sleep_time)

            # Update last called time and execute
            last_called[0] = time.time()
            return func(*args, **kwargs)

        return wrapper
    return decorator


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

    def _get_platforms_for_learning_styles(self, learning_styles: List[str]) -> Dict[str, bool]:
        """
        Determine which platforms to search based on user's selected learning styles.

        Maps learning styles to content types and platforms:
        - videos/visual → YouTube, Udemy video courses
        - hands_on → Udemy, interactive platforms
        - reading → Article platforms, documentation
        - interactive → Coding challenge platforms

        Args:
            learning_styles: User's selected learning styles

        Returns:
            Dict with platform search flags (e.g., {'search_youtube': True, 'search_udemy': False})
        """
        # Default: search nothing if no styles selected
        search_flags = {
            'search_youtube': False,
            'search_udemy': False,
            'search_articles': False,
            'search_interactive': False
        }

        # If no learning styles specified, search all platforms (backward compatibility)
        if not learning_styles:
            logger.info("📋 No learning styles specified - searching all platforms")
            search_flags['search_youtube'] = True
            search_flags['search_udemy'] = True
            return search_flags

        # Map learning styles to platform searches
        for style in learning_styles:
            if style in ['videos', 'visual']:
                # User wants video content → search YouTube and video-based Udemy courses
                search_flags['search_youtube'] = True
                search_flags['search_udemy'] = True  # Udemy has video courses
                logger.info(f"✅ '{style}' learning style → Enabling YouTube + Udemy search")

            elif style == 'hands_on':
                # User wants hands-on/project-based → search Udemy (structured courses with projects)
                search_flags['search_udemy'] = True
                logger.info(f"✅ '{style}' learning style → Enabling Udemy search")

            elif style == 'reading':
                # User wants text-based content → search article platforms
                search_flags['search_articles'] = True
                logger.info(f"✅ '{style}' learning style → Enabling article search")

            elif style == 'interactive':
                # User wants interactive content → search coding platforms
                search_flags['search_interactive'] = True
                logger.info(f"✅ '{style}' learning style → Enabling interactive platform search")

        # Log final search strategy
        active_platforms = [k.replace('search_', '') for k, v in search_flags.items() if v]
        logger.info(f"🎯 Content Type Filter: Searching {', '.join(active_platforms) if active_platforms else 'NO PLATFORMS (no matching content types)'}")

        return search_flags

    def search_courses(
        self,
        topic: str,
        user_preferences: Dict,
        max_results: int = 10
    ) -> List[ScoredCourse]:
        """
        Search for courses across multiple platforms and rank by relevance.

        NEW: Filters platforms based on user's selected learning_styles (content types).
        - Only searches YouTube if 'videos' or 'visual' is selected
        - Only searches Udemy if 'videos', 'visual', or 'hands_on' is selected
        - Skips video platforms entirely if user doesn't want video content

        Args:
            topic: Topic/skill to search for (e.g., "React Hooks", "Python OOP")
            user_preferences: User's learning preferences (must include basic_info.learning_style)
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

        # NEW: Get user's learning styles to filter platform searches
        basic_info = user_preferences.get('basic_info', {})
        learning_styles = basic_info.get('learning_style', [])

        # Determine which platforms to search based on content type preferences
        platform_flags = self._get_platforms_for_learning_styles(learning_styles)

        # Search YouTube ONLY if user wants video content
        if platform_flags['search_youtube'] and self.youtube_api_key:
            youtube_courses = self._search_youtube(topic, user_preferences, max_results=5)
            all_courses.extend(youtube_courses)
            logger.info(f"✅ YouTube search completed: {len(youtube_courses)} courses found")
        elif platform_flags['search_youtube'] and not self.youtube_api_key:
            logger.warning("⚠️ YouTube API key not configured - skipping YouTube search")
        elif not platform_flags['search_youtube']:
            logger.info("⏭️ Skipping YouTube search - 'videos' or 'visual' not in learning styles")

        # Search Udemy ONLY if user wants video or hands-on content
        if platform_flags['search_udemy'] and self.udemy_client_id and self.udemy_client_secret:
            udemy_courses = self._search_udemy(topic, max_results=5)
            all_courses.extend(udemy_courses)
            logger.info(f"✅ Udemy search completed: {len(udemy_courses)} courses found")
        elif platform_flags['search_udemy'] and not (self.udemy_client_id and self.udemy_client_secret):
            logger.warning("⚠️ Udemy API credentials not configured - skipping Udemy search")
        elif not platform_flags['search_udemy']:
            logger.info("⏭️ Skipping Udemy search - 'videos', 'visual', or 'hands_on' not in learning styles")

        # NEW: Search article platforms ONLY if user wants reading content
        if platform_flags['search_articles']:
            logger.info("📄 Searching article platforms for reading content...")

            # Dev.to - Developer articles and tutorials
            devto_articles = self._search_devto(topic, max_results=5)
            all_courses.extend(devto_articles)
            logger.info(f"✅ Dev.to search completed: {len(devto_articles)} articles found")

            # Hashnode - Developer blogs
            hashnode_articles = self._search_hashnode(topic, max_results=5)
            all_courses.extend(hashnode_articles)
            logger.info(f"✅ Hashnode search completed: {len(hashnode_articles)} articles found")

            # freeCodeCamp RSS - Beginner-friendly tutorials
            fcc_articles = self._search_freecodecamp_rss(topic, max_results=5)
            all_courses.extend(fcc_articles)
            logger.info(f"✅ freeCodeCamp RSS search completed: {len(fcc_articles)} articles found")

            # Medium RSS - Tech articles
            medium_articles = self._search_medium_rss(topic, max_results=5)
            all_courses.extend(medium_articles)
            logger.info(f"✅ Medium RSS search completed: {len(medium_articles)} articles found")
        elif not platform_flags['search_articles']:
            logger.info("⏭️ Skipping article platforms - 'reading' not in learning styles")

        # NEW: Search interactive platforms ONLY if user wants interactive content
        if platform_flags['search_interactive']:
            logger.info("💻 Searching interactive coding platforms...")

            # Exercism - Coding exercises for programming languages
            exercism_exercises = self._search_exercism(topic, max_results=5)
            all_courses.extend(exercism_exercises)
            logger.info(f"✅ Exercism search completed: {len(exercism_exercises)} exercises found")
        elif not platform_flags['search_interactive']:
            logger.info("⏭️ Skipping interactive platforms - 'interactive' not in learning styles")

        # NEW: Search GitHub for hands-on tutorials and projects
        if platform_flags.get('search_udemy') or 'hands_on' in learning_styles:
            logger.info("🛠️ Searching GitHub for tutorial repositories...")

            # GitHub - Tutorial repos and awesome lists
            github_repos = self._search_github_tutorials(topic, max_results=5)
            all_courses.extend(github_repos)
            logger.info(f"✅ GitHub search completed: {len(github_repos)} tutorial repos found")

        # NO MOCK DATA - Return empty list if no real courses found
        # User explicitly requested: "it should not mock those things!"
        if not all_courses:
            logger.warning(f"⚠️ No real courses found for '{topic}' - returning empty list (NO MOCK DATA)")
            # Return empty list instead of mock data - caller should handle gracefully
            return []

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
        Search for individual video tutorials on YouTube with quality filtering.

        NEW BEHAVIOR (Quality Filtering):
        - Fetches 2x requested amount to account for filtering
        - Applies freshness, length, authority, and engagement filters
        - Returns only high-quality videos that meet all criteria

        Args:
            topic: Search query topic
            max_results: Maximum number of quality results to return

        Returns:
            List of Course objects from YouTube videos that pass quality filters
        """
        try:
            # Fetch 2x amount to account for quality filtering
            # If we want 5 results, fetch 10 so after filtering we still have ~5
            max_results_with_buffer = min(max_results * 2, 50)  # YouTube max is 50

            # Build search parameters
            params = {
                'part': 'snippet',
                'q': topic,  # Direct topic search, no hardcoded suffix
                'type': 'video',
                'videoDefinition': 'high',
                'maxResults': max_results_with_buffer,
                'key': self.youtube_api_key,
                'relevanceLanguage': 'en',
                'order': 'relevance'
            }

            # Make API request
            logger.info(f"🔍 Searching YouTube videos for: {topic} (fetching {max_results_with_buffer}, target: {max_results})")
            response = self.session.get(self.youtube_api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            courses = []
            filtered_count = 0

            # Parse YouTube video results with quality filtering
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId', '')

                # Get video details WITH channel info for quality filtering
                video_details = self._get_youtube_video_details(video_id, include_channel=True)

                # Skip if video details fetch failed
                if not video_details:
                    logger.debug(f"⏭️ Skipping video {video_id}: failed to fetch details")
                    filtered_count += 1
                    continue

                # NEW: Apply quality filters
                video_metadata = {
                    'published_at': snippet.get('publishedAt', ''),
                    'title': snippet.get('title', '')
                }

                if not self._meets_quality_criteria(
                    video_details,
                    video_metadata,
                    video_details.get('channel_details')
                ):
                    filtered_count += 1
                    continue  # Skip low-quality videos

                # Video passed all quality checks - create Course object
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

                # Stop if we've reached target count
                if len(courses) >= max_results:
                    break

            logger.info(f"✅ Found {len(courses)} quality videos for '{topic}' (filtered {filtered_count})")
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
            import traceback
            logger.error(traceback.format_exc())
            return []

    @log_external_api_call(
        api_name="YouTube Playlist Search",
        quota_units=100,  # Playlist search costs 100 quota units
        include_headers=False,
        truncate_response_at=3000
    )
    def _search_youtube_playlists(self, topic: str, max_results: int = 3) -> List[Course]:
        """
        Search for YouTube playlists and EXPAND into individual video lessons.

        NEW BEHAVIOR (Playlist Expansion):
        - Searches for playlists (100 quota units)
        - Expands each playlist into individual videos (1 quota per playlist)
        - Fetches video details for quality filtering (1 quota per video)
        - Returns Course objects for individual videos (not entire playlists)

        This provides granular lesson tracking and better lesson sizing (5-20 min videos
        vs 5-hour playlists).

        Args:
            topic: Search query topic
            max_results: Maximum number of playlists to search (NOT final video count)

        Returns:
            List of Course objects for individual videos from playlists

        Quota Cost Example (3 playlists, ~5 videos each after filtering):
        - Playlist search: 100 units
        - Playlist items: 1 × 3 = 3 units
        - Video details: 1 × 15 = 15 units
        - Channel details: 1 × 15 = 15 units (if enabled)
        - Total: ~133 units
        """
        try:
            # Load playlist configuration
            playlist_config = settings.YOUTUBE_PLAYLIST_CONFIG

            # Check if playlist expansion is enabled
            if not playlist_config['expand_playlists']:
                logger.info("⚙️ Playlist expansion disabled, skipping playlist search")
                return []

            # Build search parameters for playlists
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
            all_video_courses = []  # Will contain Course objects for individual videos

            # Process each playlist found
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                playlist_id = item.get('id', {}).get('playlistId', '')

                # Get playlist metadata (video count)
                playlist_details = self._get_youtube_playlist_details(playlist_id)
                video_count = playlist_details.get('video_count', 0)

                # Skip small playlists (less than configured minimum)
                if video_count < playlist_config['min_playlist_size']:
                    logger.debug(f"⏭️ Skipping playlist {playlist_id}: only {video_count} videos (min: {playlist_config['min_playlist_size']})")
                    continue

                # EXPANSION: Fetch individual videos from this playlist
                logger.info(f"📋 Expanding playlist '{snippet.get('title', '')}' ({video_count} videos)")
                playlist_items = self._get_youtube_playlist_items(
                    playlist_id,
                    max_items=playlist_config['max_videos_per_playlist']
                )

                # Convert each playlist video into a Course object
                for idx, video_item in enumerate(playlist_items):
                    video_id = video_item['video_id']

                    # Fetch full video details for quality filtering
                    video_details = self._get_youtube_video_details(
                        video_id,
                        include_channel=True  # For authority check
                    )

                    # Skip if video details fetch failed
                    if not video_details:
                        logger.debug(f"⏭️ Skipping video {video_id}: failed to fetch details")
                        continue

                    # NEW: Apply quality filters
                    video_metadata = {
                        'published_at': video_item.get('published_at', video_details.get('published_at', '')),
                        'title': video_item['title']
                    }

                    if not self._meets_quality_criteria(
                        video_details,
                        video_metadata,
                        video_details.get('channel_details')
                    ):
                        logger.debug(f"⏭️ Video '{video_item['title'][:50]}...' filtered out (quality criteria)")
                        continue

                    # Create Course object for individual video (preserving playlist context)
                    course = Course(
                        title=video_item['title'],  # No 📚 emoji (it's a video, not a playlist)
                        url=f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}",  # Preserves playlist context
                        platform='youtube',
                        description=video_item['description'],
                        instructor=video_item.get('channel_title', snippet.get('channelTitle', '')),
                        duration_hours=video_details.get('duration_hours', 0.25),
                        rating=video_details.get('rating', 4.5),
                        num_ratings=video_details.get('like_count', 0),
                        difficulty='intermediate',
                        price='free',
                        thumbnail_url=video_item['thumbnail'],
                        published_date=video_item.get('published_at', ''),
                        language='english',
                        tags=[
                            topic,
                            'playlist_video',  # Identifies this as from a playlist
                            f'playlist:{playlist_id}',  # Tracks which playlist
                            f'position:{idx + 1}'  # Original position in playlist
                        ]
                    )
                    all_video_courses.append(course)

            logger.info(f"✅ Expanded {len(data.get('items', []))} playlists → {len(all_video_courses)} quality videos for '{topic}'")
            return all_video_courses

        except requests.RequestException as e:
            logger.error(f"❌ YouTube playlist search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error during playlist expansion: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @log_external_api_call(
        api_name="YouTube Video Details",
        quota_units=1,  # Video details costs 1 quota unit per video
        include_headers=False,
        truncate_response_at=1000
    )
    def _get_youtube_video_details(self, video_id: str, include_channel: bool = False) -> Dict:
        """
        Get detailed information about a YouTube video.

        Now supports optional channel data fetching for authority filtering.

        Args:
            video_id: YouTube video ID
            include_channel: If True, fetch channel details for authority check (+1 quota unit)

        Returns:
            Dictionary with duration, rating, view count, published_at, and optionally channel_details
        """
        try:
            params = {
                'part': 'contentDetails,statistics,snippet',  # Added snippet for published_at and channel_id
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
            snippet = item.get('snippet', {})  # NEW: Get snippet for published date and channel

            # Parse ISO 8601 duration (e.g., PT15M33S)
            duration = content_details.get('duration', 'PT0M')
            duration_hours = self._parse_youtube_duration(duration)

            # Calculate engagement-based rating from likes, comments, and views
            engagement_rating = self._calculate_engagement_score(statistics)

            result = {
                'duration_hours': duration_hours,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'rating': engagement_rating,  # Dynamic rating based on engagement metrics
                'published_at': snippet.get('publishedAt', '')  # NEW: For freshness filter
            }

            # NEW: Optionally fetch channel details for authority verification
            if include_channel:
                channel_id = snippet.get('channelId', '')
                if channel_id:
                    channel_details = self._get_youtube_channel_details(channel_id)
                    result['channel_details'] = channel_details

            return result

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

    @log_external_api_call(
        api_name="YouTube Playlist Items",
        quota_units=1,
        include_headers=False,
        truncate_response_at=2000
    )
    def _get_youtube_playlist_items(self, playlist_id: str, max_items: int = 10) -> List[Dict]:
        """
        Fetch individual videos from a YouTube playlist.

        Expands playlists into individual video objects for granular lesson tracking.
        This allows each video in a playlist to be a separate lesson with its own
        progress tracking, rather than treating the entire playlist as one lesson.

        Args:
            playlist_id: YouTube playlist ID
            max_items: Maximum videos to fetch (default: 10)

        Returns:
            List of dicts with video_id, title, description, position, thumbnail, published_at

        API Endpoint: youtube/v3/playlistItems
        Quota Cost: 1 unit (fetches up to 50 videos per request)
        """
        try:
            params = {
                'part': 'snippet,contentDetails',
                'playlistId': playlist_id,
                'maxResults': min(max_items, 50),  # YouTube max = 50
                'key': self.youtube_api_key
            }

            response = self.session.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            playlist_items = []

            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})

                # Skip private/deleted videos
                if snippet.get('title') in ['Private video', 'Deleted video']:
                    logger.debug(f"⏭️ Skipping private/deleted video in playlist {playlist_id}")
                    continue

                playlist_items.append({
                    'video_id': content_details.get('videoId', ''),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'position': snippet.get('position', 0),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'channel_id': snippet.get('channelId', '')
                })

            logger.info(f"📋 Fetched {len(playlist_items)} videos from playlist {playlist_id}")
            return playlist_items

        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch playlist items: {e}")
            return []

    @log_external_api_call(
        api_name="YouTube Channel Details",
        quota_units=1,
        include_headers=False,
        truncate_response_at=500
    )
    def _get_youtube_channel_details(self, channel_id: str) -> Dict:
        """
        Fetch channel information for authority verification.

        Channel authority is determined primarily by subscriber count, which is
        a reliable indicator of content quality and creator credibility.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dict with subscriber_count, created_at, country

        Quota Cost: 1 unit per channel
        Cache Strategy: Should implement Redis 7-day cache (channels rarely change)
        """
        try:
            # TODO: Add Redis caching in future optimization
            # cache_key = f"yt_channel:{channel_id}"
            # cached = redis_client.get(cache_key)
            # if cached: return json.loads(cached)

            params = {
                'part': 'snippet,statistics',
                'id': channel_id,
                'key': self.youtube_api_key
            }

            response = self.session.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params=params,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            if not data.get('items'):
                return {'subscriber_count': 0}

            item = data['items'][0]
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})

            result = {
                'channel_id': channel_id,
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'created_at': snippet.get('publishedAt', ''),
                'country': snippet.get('country', '')
            }

            # TODO: Cache for 7 days in future optimization
            # redis_client.setex(cache_key, 604800, json.dumps(result))

            return result

        except Exception as e:
            logger.warning(f"⚠️ Channel fetch failed for {channel_id}: {e}")
            return {'subscriber_count': 0}

    def _meets_quality_criteria(
        self,
        video_details: Dict,
        video_metadata: Dict,
        channel_details: Dict = None
    ) -> bool:
        """
        Check if video meets quality standards for learning content.

        Quality Filters (ALL must pass):
        1. Freshness: Published within configured days (default: last 2 years)
        2. Optimal length: Video duration in configured range (default: 5-20 minutes)
        3. Channel authority: Minimum subscribers OR high engagement (fallback)
        4. Minimum engagement: Minimum rating and view count

        Args:
            video_details: From _get_youtube_video_details() - duration, rating, views
            video_metadata: Published date, title from playlist/search
            channel_details: Subscriber count, verification status (optional)

        Returns:
            True if ALL criteria met, False otherwise with debug logging
        """
        from datetime import datetime, timedelta

        # Load filter configuration from settings
        quality_filters = settings.YOUTUBE_QUALITY_FILTERS

        # FILTER 1: Freshness (last N years)
        published_str = video_metadata.get('published_at', '')
        if published_str:
            try:
                published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                cutoff_date = datetime.now(published_date.tzinfo) - timedelta(days=quality_filters['freshness_days'])

                if published_date < cutoff_date:
                    logger.debug(f"❌ Freshness: {published_date.strftime('%Y-%m-%d')} > {quality_filters['freshness_days']} days old")
                    return False
            except Exception as e:
                logger.warning(f"⚠️ Date parse error: {e}")

        # FILTER 2: Optimal video length (bite-sized learning)
        duration_mins = video_details.get('duration_hours', 0) * 60

        if duration_mins < quality_filters['min_length_minutes']:
            logger.debug(f"❌ Length: {duration_mins:.1f} min < {quality_filters['min_length_minutes']} min (too short)")
            return False

        if duration_mins > quality_filters['max_length_minutes']:
            logger.debug(f"❌ Length: {duration_mins:.1f} min > {quality_filters['max_length_minutes']} min (too long)")
            return False

        # FILTER 3: Channel authority (if enabled and available)
        if quality_filters['enable_channel_check'] and channel_details:
            subscriber_count = channel_details.get('subscriber_count', 0)

            # Pass if meets subscriber threshold
            if subscriber_count >= quality_filters['min_subscribers']:
                logger.debug(f"✅ Authority: {subscriber_count:,} subscribers")
            else:
                # Fallback: require high engagement if low subscribers
                engagement = video_details.get('rating', 0)
                if engagement < 4.0:
                    logger.debug(f"❌ Authority: {subscriber_count} subs < {quality_filters['min_subscribers']}, engagement {engagement} < 4.0")
                    return False

        # FILTER 4: Minimum engagement metrics
        rating = video_details.get('rating', 0)
        views = video_details.get('view_count', 0)

        if rating < quality_filters['min_engagement_score']:
            logger.debug(f"❌ Engagement: rating {rating} < {quality_filters['min_engagement_score']}")
            return False

        if views < quality_filters['min_views']:
            logger.debug(f"❌ Engagement: {views} views < {quality_filters['min_views']}")
            return False

        # All filters passed!
        logger.debug(f"✅ Quality: {duration_mins:.1f}min, {views:,} views, rating {rating:.1f}")
        return True

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

    @rate_limit(calls_per_second=1.0)
    @log_external_api_call(
        api_name="Dev.to Articles",
        include_headers=False,
        truncate_response_at=2000
    )
    def _search_devto(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL articles from Dev.to API - NO MOCK DATA.

        Dev.to provides a free, no-authentication API for accessing
        developer articles and tutorials.

        API Documentation: https://developers.forem.com/api/v1

        Args:
            topic: Topic to search for (e.g., "React Hooks", "Python")
            max_results: Maximum number of articles to return (default: 10)

        Returns:
            List of Course objects representing real Dev.to articles with is_mock=False
        """
        try:
            # Dev.to API endpoint for articles by tag
            # We'll search by tag (topic converted to tag format)
            tag = topic.lower().replace(' ', '-').replace('.', '')

            logger.info(f"🔍 Searching Dev.to for articles tagged: {tag}")

            # Make API request - NO authentication required!
            response = self.session.get(
                'https://dev.to/api/articles',
                params={
                    'tag': tag,
                    'per_page': max_results,
                    'top': 7  # Get popular articles from last week
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            articles = []

            # Parse Dev.to article results
            for item in data:
                # Calculate reading time in hours (Dev.to provides minutes)
                reading_minutes = item.get('reading_time_minutes', 10)
                duration_hours = reading_minutes / 60.0

                # Calculate rating from positive reactions (0-5 scale)
                # Dev.to articles with 100+ reactions are excellent
                reactions = item.get('positive_reactions_count', 0)
                rating = min(5.0, 2.5 + (reactions / 100.0))  # Scale: 2.5-5.0

                # Parse published date
                published_date = item.get('published_at', '')

                article = Course(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    platform='dev_to',
                    description=item.get('description', ''),
                    instructor=item.get('user', {}).get('name', 'Dev.to Author'),
                    duration_hours=duration_hours,
                    rating=rating,
                    num_ratings=reactions,  # Use reactions as rating count
                    difficulty='intermediate',  # Dev.to articles are typically intermediate
                    price='free',
                    thumbnail_url=item.get('cover_image', ''),
                    published_date=published_date,
                    language='english',
                    tags=[topic, 'article', 'dev_to'],
                    is_mock=False,  # ✅ REAL CONTENT
                    source='dev_to'
                )
                articles.append(article)

            logger.info(f"✅ Found {len(articles)} REAL articles from Dev.to for '{topic}'")
            return articles

        except requests.RequestException as e:
            logger.error(f"❌ Dev.to API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing Dev.to results: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @rate_limit(calls_per_second=0.5)
    def _search_hashnode(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL developer blog articles from Hashnode GraphQL API - NO MOCK DATA.

        Hashnode provides a free GraphQL API for accessing developer blogs
        and technical articles.

        API Documentation: https://gql.hashnode.com

        Args:
            topic: Topic to search for
            max_results: Maximum number of articles to return (default: 10)

        Returns:
            List of Course objects representing real Hashnode articles with is_mock=False
        """
        try:
            # Hashnode GraphQL API endpoint
            url = 'https://gql.hashnode.com'

            # UPDATED GraphQL query using Hashnode's public feed API
            # Note: Hashnode API has changed - using feed query instead of search
            query = """
            query GetFeed($first: Int!) {
                feed(first: $first) {
                    edges {
                        node {
                            title
                            brief
                            url
                            slug
                            coverImage {
                                url
                            }
                            author {
                                name
                            }
                            publishedAt
                            readTimeInMinutes
                            views
                            reactionCount
                        }
                    }
                }
            }
            """

            logger.info(f"🔍 Fetching Hashnode feed articles (topic filtering happens client-side)")

            # Make GraphQL API request
            response = self.session.post(
                url,
                json={
                    'query': query,
                    'variables': {
                        'first': max_results * 5  # Get more to filter by topic
                    }
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            articles = []

            # Parse Hashnode GraphQL results
            topic_lower = topic.lower()
            edges = data.get('data', {}).get('feed', {}).get('edges', [])

            for edge in edges:
                node = edge.get('node', {})

                # Client-side filtering: check if topic appears in title or brief
                title = node.get('title', '')
                brief = node.get('brief', '')

                if topic_lower not in title.lower() and topic_lower not in brief.lower():
                    continue  # Skip articles that don't match topic

                # Calculate reading time in hours
                reading_minutes = node.get('readTimeInMinutes', 10)
                duration_hours = reading_minutes / 60.0

                # Calculate rating from views and reactions
                views = node.get('views', 0)
                reactions = node.get('reactionCount', 0)
                # High-quality Hashnode posts have good view-to-reaction ratios
                rating = min(5.0, 3.0 + (reactions / max(views / 100, 1)))

                # Get cover image URL
                cover_image = node.get('coverImage', {})
                thumbnail_url = cover_image.get('url', '') if cover_image else ''

                article = Course(
                    title=title,
                    url=node.get('url', ''),
                    platform='hashnode',
                    description=brief,
                    instructor=node.get('author', {}).get('name', 'Hashnode Author'),
                    duration_hours=duration_hours,
                    rating=rating,
                    num_ratings=reactions,
                    difficulty='intermediate',
                    price='free',
                    thumbnail_url=thumbnail_url,
                    published_date=node.get('publishedAt', ''),
                    language='english',
                    tags=[topic, 'article', 'hashnode'],
                    is_mock=False,  # ✅ REAL CONTENT
                    source='hashnode'
                )
                articles.append(article)

                if len(articles) >= max_results:
                    break  # Stop once we have enough articles

            logger.info(f"✅ Found {len(articles)} REAL articles from Hashnode for '{topic}'")
            return articles

        except requests.RequestException as e:
            logger.error(f"❌ Hashnode API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing Hashnode results: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @rate_limit(calls_per_second=1.0)
    @log_external_api_call(
        api_name="GitHub Repositories",
        include_headers=False,
        truncate_response_at=2000
    )
    def _search_github_tutorials(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL tutorial repositories from GitHub - NO MOCK DATA.

        Searches for high-quality tutorial repositories and awesome lists
        related to the topic using GitHub's search API (no auth required).

        API Documentation: https://docs.github.com/en/rest/search

        Args:
            topic: Topic to search for
            max_results: Maximum number of repositories to return (default: 10)

        Returns:
            List of Course objects representing real GitHub tutorial repos with is_mock=False
        """
        try:
            # GitHub search query for tutorial repositories
            # Search for repos with "tutorial" OR "awesome" in name/description
            search_query = f"{topic} tutorial OR awesome-{topic.replace(' ', '-')}"

            logger.info(f"🔍 Searching GitHub for tutorial repos: {search_query}")

            # Make API request to GitHub Search API (no auth required, but lower rate limit)
            response = self.session.get(
                'https://api.github.com/search/repositories',
                params={
                    'q': search_query,
                    'sort': 'stars',  # Sort by popularity
                    'order': 'desc',
                    'per_page': max_results
                },
                headers={
                    'Accept': 'application/vnd.github.v3+json'
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            repos = []

            # Parse GitHub repository results
            for item in data.get('items', []):
                # Calculate rating from stars (normalized to 0-5 scale)
                stars = item.get('stargazers_count', 0)
                # Repos with 1000+ stars are excellent, scale accordingly
                rating = min(5.0, 2.5 + (stars / 500.0))

                # Estimate completion time based on repo size (rough estimate)
                # Larger repos = more content = longer learning time
                # This is a rough heuristic
                duration_hours = min(20.0, 2.0 + (stars / 200.0))

                repo = Course(
                    title=item.get('name', '').replace('-', ' ').title(),
                    url=item.get('html_url', ''),
                    platform='github',
                    description=item.get('description', ''),
                    instructor=item.get('owner', {}).get('login', 'GitHub User'),
                    duration_hours=duration_hours,
                    rating=rating,
                    num_ratings=stars,  # Use stars as rating count
                    difficulty='intermediate',
                    price='free',
                    thumbnail_url=item.get('owner', {}).get('avatar_url', ''),
                    published_date=item.get('created_at', ''),
                    language=item.get('language', 'Multiple'),
                    tags=[topic, 'github', 'tutorial', 'hands-on'],
                    is_mock=False,  # ✅ REAL CONTENT
                    source='github'
                )
                repos.append(repo)

            logger.info(f"✅ Found {len(repos)} REAL tutorial repos from GitHub for '{topic}'")
            return repos

        except requests.RequestException as e:
            logger.error(f"❌ GitHub API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing GitHub results: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @rate_limit(calls_per_second=0.5)
    def _search_freecodecamp_rss(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL tutorials from freeCodeCamp RSS feed - NO MOCK DATA.

        freeCodeCamp provides free RSS feeds for their blog/tutorials.
        Uses feedparser library to parse RSS feed.

        RSS Feed: https://www.freecodecamp.org/news/rss/

        Args:
            topic: Topic to filter articles for
            max_results: Maximum number of articles to return (default: 10)

        Returns:
            List of Course objects representing real freeCodeCamp tutorials with is_mock=False
        """
        try:
            logger.info(f"🔍 Parsing freeCodeCamp RSS feed for: {topic}")

            # Parse freeCodeCamp RSS feed
            feed = feedparser.parse('https://www.freecodecamp.org/news/rss/')

            articles = []
            topic_lower = topic.lower()

            # Filter articles by topic relevance
            for entry in feed.entries[:50]:  # Check first 50 entries
                title = entry.get('title', '')
                summary = entry.get('summary', '')

                # Check if topic appears in title or summary
                if topic_lower in title.lower() or topic_lower in summary.lower():
                    # Estimate reading time (freeCodeCamp articles are typically long)
                    # Rough estimate: 1000 words = 5 minutes reading
                    description_length = len(summary)
                    reading_minutes = max(10, description_length / 200)  # Rough heuristic
                    duration_hours = reading_minutes / 60.0

                    article = Course(
                        title=title,
                        url=entry.get('link', ''),
                        platform='freecodecamp',
                        description=summary[:500],  # Truncate long summaries
                        instructor='freeCodeCamp',
                        duration_hours=duration_hours,
                        rating=4.5,  # freeCodeCamp content is consistently high-quality
                        num_ratings=100,  # Placeholder (RSS doesn't provide this)
                        difficulty='beginner',  # freeCodeCamp focuses on beginners
                        price='free',
                        thumbnail_url='',
                        published_date=entry.get('published', ''),
                        language='english',
                        tags=[topic, 'article', 'tutorial', 'freecodecamp'],
                        is_mock=False,  # ✅ REAL CONTENT
                        source='freecodecamp'
                    )
                    articles.append(article)

                    if len(articles) >= max_results:
                        break

            logger.info(f"✅ Found {len(articles)} REAL articles from freeCodeCamp RSS for '{topic}'")
            return articles

        except Exception as e:
            logger.error(f"❌ Error parsing freeCodeCamp RSS feed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @rate_limit(calls_per_second=0.5)
    def _search_medium_rss(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL articles from Medium RSS feeds - NO MOCK DATA.

        Medium provides RSS feeds for tags. We construct the RSS URL
        based on the topic/tag.

        RSS Pattern: https://medium.com/feed/tag/{tag}

        Args:
            topic: Topic to search for (will be converted to tag)
            max_results: Maximum number of articles to return (default: 10)

        Returns:
            List of Course objects representing real Medium articles with is_mock=False
        """
        try:
            # Convert topic to Medium tag format
            tag = topic.lower().replace(' ', '-')
            rss_url = f'https://medium.com/feed/tag/{tag}'

            logger.info(f"🔍 Parsing Medium RSS feed for tag: {tag}")

            # Parse Medium RSS feed
            feed = feedparser.parse(rss_url)

            articles = []

            # Parse Medium entries
            for entry in feed.entries[:max_results]:
                # Estimate reading time (Medium articles vary in length)
                summary = entry.get('summary', '')
                description_length = len(summary)
                reading_minutes = max(5, description_length / 200)
                duration_hours = reading_minutes / 60.0

                # Extract author from entry
                author = entry.get('author', 'Medium Writer')

                article = Course(
                    title=entry.get('title', ''),
                    url=entry.get('link', ''),
                    platform='medium',
                    description=summary[:500],  # Truncate long summaries
                    instructor=author,
                    duration_hours=duration_hours,
                    rating=4.0,  # Medium content quality varies
                    num_ratings=50,  # Placeholder (RSS doesn't provide this)
                    difficulty='intermediate',
                    price='free',  # Some Medium articles are paywalled, but we mark as free
                    thumbnail_url='',
                    published_date=entry.get('published', ''),
                    language='english',
                    tags=[topic, 'article', 'medium'],
                    is_mock=False,  # ✅ REAL CONTENT
                    source='medium'
                )
                articles.append(article)

            logger.info(f"✅ Found {len(articles)} REAL articles from Medium RSS for '{topic}'")
            return articles

        except Exception as e:
            logger.error(f"❌ Error parsing Medium RSS feed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    @rate_limit(calls_per_second=1.0)
    @log_external_api_call(
        api_name="Exercism Exercises",
        include_headers=False,
        truncate_response_at=2000
    )
    def _search_exercism(self, topic: str, max_results: int = 10) -> List[Course]:
        """
        Fetch REAL coding exercises from Exercism - NO MOCK DATA.

        Exercism provides free coding exercises for learning programming.
        We search for exercises related to the topic/language.

        Note: Exercism's API is primarily for their platform, but we can
        search for track/exercise information.

        Args:
            topic: Programming language or topic to search for
            max_results: Maximum number of exercises to return (default: 10)

        Returns:
            List of Course objects representing real Exercism exercises with is_mock=False
        """
        try:
            # Exercism tracks (programming languages)
            # Map common topics to Exercism track slugs
            topic_to_track = {
                'python': 'python',
                'javascript': 'javascript',
                'java': 'java',
                'c++': 'cpp',
                'cpp': 'cpp',
                'ruby': 'ruby',
                'go': 'go',
                'rust': 'rust',
                'typescript': 'typescript',
                'php': 'php',
                'c#': 'csharp',
                'csharp': 'csharp',
                'swift': 'swift',
                'kotlin': 'kotlin',
            }

            # Try to map topic to Exercism track
            track_slug = topic_to_track.get(topic.lower())

            if not track_slug:
                logger.info(f"⏭️ No Exercism track found for topic: {topic}")
                return []

            logger.info(f"🔍 Searching Exercism for {track_slug} exercises")

            # Exercism API endpoint (v2)
            # Note: This returns track information, exercises are nested
            response = self.session.get(
                f'https://exercism.org/api/v2/tracks/{track_slug}',
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            track_data = data.get('track', {})

            # Create a Course object representing the Exercism track
            # (we can't easily get individual exercises without auth)
            num_exercises = track_data.get('num_exercises', 0)

            if num_exercises == 0:
                logger.info(f"⏭️ No exercises found for {track_slug}")
                return []

            # Create a single Course representing the entire Exercism track
            exercise = Course(
                title=f"{track_data.get('title', topic.title())} Practice Exercises",
                url=f"https://exercism.org/tracks/{track_slug}",
                platform='exercism',
                description=f"Learn {topic} through {num_exercises} coding exercises. Practice with real-world problems and get automated feedback.",
                instructor='Exercism',
                duration_hours=num_exercises * 0.5,  # Estimate 30 min per exercise
                rating=4.8,  # Exercism is highly rated
                num_ratings=1000,  # Placeholder
                difficulty='beginner',
                price='free',
                thumbnail_url=track_data.get('icon_url', ''),
                published_date='',
                language='english',
                tags=[topic, 'interactive', 'coding', 'exercism'],
                is_mock=False,  # ✅ REAL CONTENT
                source='exercism'
            )

            logger.info(f"✅ Found Exercism track for {topic} with {num_exercises} exercises")
            return [exercise]

        except requests.RequestException as e:
            logger.error(f"❌ Exercism API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing Exercism results: {e}")
            import traceback
            logger.error(traceback.format_exc())
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

    def _create_mock_articles(self, topic: str) -> List[Course]:
        """
        Create preview mock ARTICLES for users with 'reading' learning style.

        These articles are clearly labeled as preview data and use example.com URLs.
        They have article-specific characteristics:
        - Shorter duration (reading time)
        - article_preview platform
        - Article-focused titles and descriptions

        Args:
            topic: Topic to create mock articles for

        Returns:
            List of mock Course objects representing articles
        """
        topic_slug = topic.lower().replace(' ', '-')

        mock_articles = [
            Course(
                title=f"📄 PREVIEW: Understanding {topic} - Deep Dive",
                url=f"https://example.com/article/{topic_slug}-deep-dive",
                platform='article_preview',
                description=f"[Preview Article] In-depth written guide covering {topic} concepts, best practices, and real-world examples. Configure Dev.to API for real articles.",
                instructor="Dev Community Author",
                duration_hours=0.33,  # ~20 minute read
                rating=4.6,
                num_ratings=245,
                difficulty='intermediate',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'article', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"📄 PREVIEW: {topic} Best Practices Guide",
                url=f"https://example.com/article/{topic_slug}-best-practices",
                platform='article_preview',
                description=f"[Preview Article] Comprehensive article on {topic} best practices, patterns, and anti-patterns. Configure Dev.to or Hashnode API for real content.",
                instructor="Tech Blog Writer",
                duration_hours=0.25,  # ~15 minute read
                rating=4.4,
                num_ratings=180,
                difficulty='intermediate',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'article', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"📄 PREVIEW: {topic} Quick Start Tutorial",
                url=f"https://example.com/article/{topic_slug}-quickstart",
                platform='article_preview',
                description=f"[Preview Article] Quick-start guide for {topic} beginners. Step-by-step tutorial with code examples. Configure article API for real content.",
                instructor="Tutorial Writer",
                duration_hours=0.17,  # ~10 minute read
                rating=4.5,
                num_ratings=320,
                difficulty='beginner',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'beginner', 'article', 'preview'],
                is_mock=True,
                source='preview'
            )
        ]

        return mock_articles

    def _create_mock_interactive(self, topic: str) -> List[Course]:
        """
        Create preview mock INTERACTIVE coding challenges for users with 'interactive' learning style.

        These challenges are clearly labeled as preview data.
        They have interactive-specific characteristics:
        - Coding challenge format
        - interactive_preview platform
        - Practice-focused titles and descriptions

        Args:
            topic: Topic to create mock challenges for

        Returns:
            List of mock Course objects representing interactive challenges
        """
        topic_slug = topic.lower().replace(' ', '-')

        mock_challenges = [
            Course(
                title=f"💻 PREVIEW: {topic} Coding Challenge - Level 1",
                url=f"https://example.com/challenge/{topic_slug}-level-1",
                platform='interactive_preview',
                description=f"[Preview Challenge] Practice {topic} with hands-on coding exercises. Solve 10 problems to master the basics. Configure Exercism or freeCodeCamp API for real challenges.",
                instructor="Code Practice Platform",
                duration_hours=1.5,  # Time to complete challenges
                rating=4.7,
                num_ratings=890,
                difficulty='beginner',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'interactive', 'coding', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"💻 PREVIEW: {topic} Advanced Problem Set",
                url=f"https://example.com/challenge/{topic_slug}-advanced",
                platform='interactive_preview',
                description=f"[Preview Challenge] Advanced {topic} coding problems with automated testing. Improve your skills through practice. Configure LeetCode or HackerRank API for real challenges.",
                instructor="Coding Challenge Platform",
                duration_hours=3.0,  # Time to complete advanced challenges
                rating=4.6,
                num_ratings=560,
                difficulty='advanced',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'interactive', 'advanced', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"💻 PREVIEW: {topic} Interactive Exercises",
                url=f"https://example.com/challenge/{topic_slug}-exercises",
                platform='interactive_preview',
                description=f"[Preview Challenge] Learn {topic} by doing with step-by-step interactive exercises. Get instant feedback on your code. Configure interactive platform API for real content.",
                instructor="Interactive Learning",
                duration_hours=2.0,
                rating=4.5,
                num_ratings=430,
                difficulty='intermediate',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'interactive', 'exercises', 'preview'],
                is_mock=True,
                source='preview'
            )
        ]

        return mock_challenges

    def _create_mock_projects(self, topic: str) -> List[Course]:
        """
        Create preview mock PROJECT-BASED content for users with 'hands_on' learning style.

        These projects are clearly labeled as preview data.
        They have project-specific characteristics:
        - Project-based format
        - project_preview platform
        - Build-something-focused titles and descriptions

        Args:
            topic: Topic to create mock projects for

        Returns:
            List of mock Course objects representing hands-on projects
        """
        topic_slug = topic.lower().replace(' ', '-')

        mock_projects = [
            Course(
                title=f"🛠️ PREVIEW: Build a {topic} Application",
                url=f"https://example.com/project/{topic_slug}-app",
                platform='project_preview',
                description=f"[Preview Project] Learn {topic} by building a real-world application from scratch. Includes starter code and step-by-step guidance. Configure GitHub API for real project repos.",
                instructor="Project-Based Learning",
                duration_hours=6.0,  # Time to complete project
                rating=4.8,
                num_ratings=670,
                difficulty='intermediate',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'project', 'hands-on', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"🛠️ PREVIEW: {topic} Mini Projects Collection",
                url=f"https://example.com/project/{topic_slug}-mini-projects",
                platform='project_preview',
                description=f"[Preview Project] Collection of 5 mini-projects to practice {topic} skills. Each project builds on the previous one. Configure project repository API for real content.",
                instructor="Hands-On Learning",
                duration_hours=4.0,
                rating=4.6,
                num_ratings=520,
                difficulty='beginner',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'project', 'beginner', 'preview'],
                is_mock=True,
                source='preview'
            ),
            Course(
                title=f"🛠️ PREVIEW: Advanced {topic} Portfolio Project",
                url=f"https://example.com/project/{topic_slug}-portfolio",
                platform='project_preview',
                description=f"[Preview Project] Build an impressive {topic} project for your portfolio. Production-ready code with best practices. Configure GitHub trending repos API for real projects.",
                instructor="Portfolio Projects",
                duration_hours=10.0,
                rating=4.9,
                num_ratings=340,
                difficulty='advanced',
                price='free',
                thumbnail_url='',
                language='english',
                tags=[topic, 'project', 'advanced', 'portfolio', 'preview'],
                is_mock=True,
                source='preview'
            )
        ]

        return mock_projects

    @staticmethod
    def _get_career_content_weights(career_stage: str) -> Dict[str, float]:
        """
        Get content type multipliers based on career stage.

        Different career stages have different learning needs:
        - Students: Need foundational theory and structured video courses
        - Career changers: Need hands-on projects and practical experience
        - Skill upgraders: Need quick, focused tutorials
        - Professionals: Need advanced content and case studies

        Args:
            career_stage: One of 'student', 'career_change', 'skill_upgrade', 'professional'

        Returns:
            Dict mapping content types to multiplier values (0.6-2.0)
        """
        weights = {
            'student': {
                'video': 1.5,         # Theory-heavy video courses
                'interactive': 1.2,   # Interactive learning helps retention
                'article': 0.8,       # Less emphasis on reading
                'project': 1.0        # Some hands-on, but theory first
            },
            'career_change': {
                'project': 2.0,       # MAXIMUM emphasis on portfolio projects
                'interactive': 1.5,   # Hands-on coding challenges
                'video': 1.0,         # Standard video courses
                'article': 0.6        # Minimal reading, focus on doing
            },
            'skill_upgrade': {
                'video': 1.4,         # Quick video tutorials
                'interactive': 1.3,   # Practice-based learning
                'article': 1.1,       # Articles for best practices
                'project': 1.0        # Some projects
            },
            'professional': {
                'article': 1.2,       # Technical articles and papers
                'project': 1.4,       # Advanced case studies
                'video': 0.9,         # Less need for basic tutorials
                'interactive': 1.0    # Standard
            }
        }
        return weights.get(career_stage, {})


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
        
        # Career-based content weighting (NEW: uses career_stage for personalization)
        career_stage = basic_info.get('career_stage', 'student')
        career_weights = self._get_career_content_weights(career_stage)
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

            # 1. Platform preference (20 points) - REDUCED for freshness factor
            if course.platform in preferred_platforms:
                platform_score = 20.0
            elif not preferred_platforms:  # No preference
                platform_score = 10.0
            else:
                platform_score = 4.0
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

            # 5. Content type/learning style match (10 points) - ENHANCED with career weighting
            content_score = 5.0  # Base score
            career_multiplier = 1.0  # Default multiplier
            
            if 'videos' in learning_styles and course.platform == 'youtube':
                content_score = 10.0
                career_multiplier = career_weights.get('video', 1.0)
            elif 'hands_on' in learning_styles and course.platform in ['udemy', 'coursera']:
                content_score = 9.0
                career_multiplier = career_weights.get('project', 1.0)
            elif 'reading' in learning_styles and course.platform in ['medium', 'dev_to']:
                content_score = 10.0
                career_multiplier = career_weights.get('article', 1.0)
            elif 'visual' in learning_styles and course.platform == 'youtube':
                content_score = 10.0
                career_multiplier = career_weights.get('video', 1.0)
            
            # Apply career-based multiplier
            content_score *= career_multiplier
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

            # 8. Content freshness (5 points) - NEW!
            # Prioritize recent content to ensure up-to-date information
            freshness_score = 0.0
            if course.published_date:
                try:
                    from datetime import datetime
                    pub_date = datetime.fromisoformat(course.published_date.replace('Z', '+00:00'))
                    days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                    
                    if days_old < 180:  # < 6 months
                        freshness_score = 5.0
                    elif days_old < 365:  # < 1 year
                        freshness_score = 4.0
                    elif days_old < 730:  # < 2 years
                        freshness_score = 3.0
                    else:
                        freshness_score = 1.0
                except:
                    freshness_score = 2.5  # Default if date parsing fails
            else:
                freshness_score = 2.5  # Default if no date available
            
            score += freshness_score
            breakdown['freshness'] = freshness_score

            # 9. Playlist/structure bonus (5 points) - KEPT for structured learning
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

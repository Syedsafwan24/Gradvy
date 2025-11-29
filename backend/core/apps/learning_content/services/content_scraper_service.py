# File: backend/core/apps/learning_content/services/content_scraper_service.py
# Description: Service for scraping content from YouTube, articles, and GitHub
# Why: Extracts actual lesson content for generating relevant quiz questions
# Relevant Files: quiz_orchestrator_service.py, models.py

import logging
import re
import hashlib
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentScraperService:
    """
    Service for scraping educational content from various platforms.

    Supports:
    - YouTube: Video transcripts via youtube-transcript-api
    - Articles: Web articles via newspaper3k or BeautifulSoup
    - GitHub: README files via GitHub API

    Returns cleaned text suitable for quiz question generation.
    """

    # Maximum content length (characters) to avoid overwhelming the AI
    MAX_CONTENT_LENGTH = 15000

    # User agent for web requests
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    @classmethod
    def scrape_lesson_content(
        cls,
        url: str,
        platform: str,
        title: str = "",
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a lesson URL based on platform.

        Args:
            url: Lesson URL to scrape
            platform: Platform type (youtube, article, github, etc.)
            title: Lesson title (fallback content)
            description: Lesson description (fallback content)

        Returns:
            Dictionary with scraped content:
            {
                'content': str,  # Scraped text content
                'source': str,   # Source type (youtube_transcript, article, github, metadata)
                'success': bool, # Whether scraping succeeded
                'content_hash': str,  # MD5 hash of content
                'word_count': int,    # Number of words
                'error': str or None  # Error message if failed
            }
        """
        platform_lower = platform.lower()

        try:
            # Route to appropriate scraper
            if 'youtube' in platform_lower or 'youtu.be' in url.lower():
                return cls._scrape_youtube(url, title, description)
            elif 'github' in platform_lower or 'github.com' in url.lower():
                return cls._scrape_github(url, title, description)
            else:
                # Default to article scraping for all other URLs
                return cls._scrape_article(url, title, description)

        except Exception as e:
            logger.error(f"Error scraping content from {url}: {e}", exc_info=True)
            # Return metadata fallback
            return cls._fallback_to_metadata(title, description, error=str(e))

    @classmethod
    def _scrape_youtube(
        cls,
        url: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Scrape YouTube video transcript.

        Uses youtube-transcript-api to fetch captions/subtitles.
        Falls back to metadata if transcript unavailable.
        """
        try:
            # Import here to avoid import errors if package not installed
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

            # Extract video ID from URL
            video_id = cls._extract_youtube_video_id(url)
            if not video_id:
                logger.warning(f"Could not extract video ID from {url}")
                return cls._fallback_to_metadata(title, description, error="Invalid YouTube URL")

            # Fetch transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])

            # Combine transcript segments into full text
            full_text = ' '.join(segment['text'] for segment in transcript_list)

            # Clean up text
            cleaned_text = cls._clean_text(full_text)

            # Truncate if too long
            if len(cleaned_text) > cls.MAX_CONTENT_LENGTH:
                cleaned_text = cleaned_text[:cls.MAX_CONTENT_LENGTH] + "..."

            content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            word_count = len(cleaned_text.split())

            logger.info(f"✅ Successfully scraped YouTube transcript: {video_id} ({word_count} words)")

            return {
                'content': cleaned_text,
                'source': 'youtube_transcript',
                'success': True,
                'content_hash': content_hash,
                'word_count': word_count,
                'error': None
            }

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"YouTube transcript not available for {url}: {e}")
            return cls._fallback_to_metadata(title, description, error="Transcript not available")

        except ImportError:
            logger.error("youtube-transcript-api not installed")
            return cls._fallback_to_metadata(title, description, error="youtube-transcript-api not installed")

        except Exception as e:
            logger.error(f"Error scraping YouTube {url}: {e}", exc_info=True)
            return cls._fallback_to_metadata(title, description, error=str(e))

    @classmethod
    def _scrape_article(
        cls,
        url: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Scrape article content from web pages.

        Uses newspaper3k for intelligent article extraction.
        Falls back to BeautifulSoup if newspaper3k fails.
        """
        try:
            # Try newspaper3k first (best for news/blog articles)
            try:
                from newspaper import Article

                article = Article(url)
                article.download()
                article.parse()

                content = article.text
                if content and len(content.strip()) > 100:
                    cleaned_text = cls._clean_text(content)

                    # Truncate if too long
                    if len(cleaned_text) > cls.MAX_CONTENT_LENGTH:
                        cleaned_text = cleaned_text[:cls.MAX_CONTENT_LENGTH] + "..."

                    content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
                    word_count = len(cleaned_text.split())

                    logger.info(f"✅ Successfully scraped article with newspaper3k ({word_count} words)")

                    return {
                        'content': cleaned_text,
                        'source': 'article',
                        'success': True,
                        'content_hash': content_hash,
                        'word_count': word_count,
                        'error': None
                    }

            except ImportError:
                logger.warning("newspaper3k not installed, trying BeautifulSoup")
            except Exception as e:
                logger.warning(f"newspaper3k failed: {e}, trying BeautifulSoup")

            # Fallback to BeautifulSoup
            return cls._scrape_with_beautifulsoup(url, title, description)

        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}", exc_info=True)
            return cls._fallback_to_metadata(title, description, error=str(e))

    @classmethod
    def _scrape_with_beautifulsoup(
        cls,
        url: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Scrape web page using BeautifulSoup.

        Extracts text from main content areas.
        """
        try:
            headers = {'User-Agent': cls.USER_AGENT}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text from main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|article|post'))
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)

            cleaned_text = cls._clean_text(text)

            if len(cleaned_text) < 100:
                logger.warning(f"Extracted text too short from {url}")
                return cls._fallback_to_metadata(title, description, error="Insufficient content extracted")

            # Truncate if too long
            if len(cleaned_text) > cls.MAX_CONTENT_LENGTH:
                cleaned_text = cleaned_text[:cls.MAX_CONTENT_LENGTH] + "..."

            content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            word_count = len(cleaned_text.split())

            logger.info(f"✅ Successfully scraped with BeautifulSoup ({word_count} words)")

            return {
                'content': cleaned_text,
                'source': 'article',
                'success': True,
                'content_hash': content_hash,
                'word_count': word_count,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error with BeautifulSoup scraping {url}: {e}", exc_info=True)
            return cls._fallback_to_metadata(title, description, error=str(e))

    @classmethod
    def _scrape_github(
        cls,
        url: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Scrape GitHub README content.

        Fetches README.md from GitHub repositories.
        """
        try:
            # Extract owner and repo from URL
            # URL format: https://github.com/{owner}/{repo}
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')

            if len(path_parts) < 2:
                logger.warning(f"Invalid GitHub URL format: {url}")
                return cls._fallback_to_metadata(title, description, error="Invalid GitHub URL")

            owner, repo = path_parts[0], path_parts[1]

            # Fetch README via GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            headers = {
                'Accept': 'application/vnd.github.v3.raw',
                'User-Agent': cls.USER_AGENT
            }

            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            readme_text = response.text
            cleaned_text = cls._clean_text(readme_text)

            # Truncate if too long
            if len(cleaned_text) > cls.MAX_CONTENT_LENGTH:
                cleaned_text = cleaned_text[:cls.MAX_CONTENT_LENGTH] + "..."

            content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            word_count = len(cleaned_text.split())

            logger.info(f"✅ Successfully scraped GitHub README: {owner}/{repo} ({word_count} words)")

            return {
                'content': cleaned_text,
                'source': 'github',
                'success': True,
                'content_hash': content_hash,
                'word_count': word_count,
                'error': None
            }

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"GitHub README not found: {url}")
                return cls._fallback_to_metadata(title, description, error="README not found")
            else:
                logger.error(f"GitHub API error for {url}: {e}")
                return cls._fallback_to_metadata(title, description, error=str(e))

        except Exception as e:
            logger.error(f"Error scraping GitHub {url}: {e}", exc_info=True)
            return cls._fallback_to_metadata(title, description, error=str(e))

    @classmethod
    def _fallback_to_metadata(
        cls,
        title: str,
        description: str,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Fallback to using lesson metadata when scraping fails.

        Combines title and description to create basic content.
        """
        # Combine title and description
        metadata_content = f"{title}\n\n{description}" if description else title
        cleaned_text = cls._clean_text(metadata_content)

        content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
        word_count = len(cleaned_text.split())

        logger.info(f"⚠️  Using metadata fallback ({word_count} words)")

        return {
            'content': cleaned_text,
            'source': 'metadata',
            'success': False,
            'content_hash': content_hash,
            'word_count': word_count,
            'error': error
        }

    @staticmethod
    def _extract_youtube_video_id(url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
            r'(?:embed/)([0-9A-Za-z_-]{11})',   # Embed URLs
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.

        - Remove excessive whitespace
        - Remove special characters
        - Normalize line breaks
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text

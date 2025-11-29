"""
backend/ml_services/services/knowledge_assessor.py
User knowledge assessment service - replaces static experience levels with 0-100 scoring
Assesses actual user knowledge based on learning history and engagement
RELEVANT FILES: learning_path_service.py, ai_goal_analyzer.py, core/apps/preferences/models.py
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings


logger = logging.getLogger(__name__)


@dataclass
class KnowledgeScore:
    """
    User's knowledge score for a specific topic/skill.

    Score is 0-100 where:
    - 0-20: Absolute beginner
    - 20-40: Beginner with some basics
    - 40-60: Intermediate
    - 60-80: Advanced
    - 80-100: Expert
    """
    score: int  # 0-100
    confidence: float  # 0.0-1.0 - how confident we are in this score
    last_assessed: datetime
    contributing_factors: Dict[str, Any]  # What influenced this score


@dataclass
class DifficultyRecommendation:
    """
    Recommended difficulty range for a user based on knowledge.
    """
    min_difficulty: int  # 0-100
    max_difficulty: int  # 0-100
    optimal_starting_difficulty: int  # 0-100
    progression_rate: str  # 'slow', 'medium', 'fast'


class KnowledgeAssessor:
    """
    Service for assessing user knowledge dynamically.

    This replaces static experience levels (beginner/intermediate/advanced)
    with actual knowledge scoring based on user history.

    Key Features:
    - 0-100 scoring scale (not discrete levels)
    - Considers completed courses, quiz scores, time spent
    - Accounts for knowledge decay over time
    - Provides confidence scores
    - Recommends appropriate difficulty progression
    """

    # Scoring weights for different factors
    WEIGHT_COMPLETED_COURSES = 0.40  # 40% - completion shows commitment
    WEIGHT_QUIZ_SCORES = 0.30  # 30% - quiz results show actual understanding
    WEIGHT_RELATED_SKILLS = 0.20  # 20% - related skills indicate transferable knowledge
    WEIGHT_SELF_REPORTED = 0.10  # 10% - user's self-assessment (least reliable)

    # Time decay parameters
    KNOWLEDGE_HALF_LIFE_DAYS = 180  # Knowledge decays 50% after 6 months of inactivity
    MAX_DECAY_FACTOR = 0.5  # Knowledge never decays below 50% of original

    def __init__(self):
        """Initialize knowledge assessor."""
        pass

    def assess_user_knowledge(
        self,
        user_id: int,
        topic: str,
        user_data: Optional[Dict[str, Any]] = None
    ) -> KnowledgeScore:
        """
        Assess user's knowledge level for a specific topic.

        Args:
            user_id: User's ID
            topic: Topic/skill to assess (e.g., 'python', 'react', 'machine learning')
            user_data: Optional pre-fetched user data (for performance)

        Returns:
            KnowledgeScore with 0-100 score and metadata

        Example:
            >>> assessor = KnowledgeAssessor()
            >>> score = assessor.assess_user_knowledge(user_id=10, topic='react')
            >>> print(f"Knowledge: {score.score}/100, Confidence: {score.confidence}")
        """
        logger.info(f"📊 Assessing knowledge for user {user_id}, topic: {topic}")

        # Fetch user data if not provided
        if user_data is None:
            user_data = self._fetch_user_data(user_id)

        # Calculate base score from different factors
        completed_score = self._score_from_completed_courses(user_data, topic)
        quiz_score = self._score_from_quiz_results(user_data, topic)
        skills_score = self._score_from_related_skills(user_data, topic)
        self_reported_score = self._score_from_self_report(user_data, topic)

        # Weighted combination
        base_score = (
            completed_score * self.WEIGHT_COMPLETED_COURSES +
            quiz_score * self.WEIGHT_QUIZ_SCORES +
            skills_score * self.WEIGHT_RELATED_SKILLS +
            self_reported_score * self.WEIGHT_SELF_REPORTED
        )

        # Apply time decay (knowledge fades without practice)
        time_adjusted_score = self._apply_time_decay(base_score, user_data, topic)

        # Calculate confidence (how reliable is this score?)
        confidence = self._calculate_confidence(user_data, topic)

        # Round to integer 0-100
        final_score = max(0, min(100, int(round(time_adjusted_score))))

        knowledge_score = KnowledgeScore(
            score=final_score,
            confidence=confidence,
            last_assessed=datetime.now(),
            contributing_factors={
                'completed_courses': completed_score,
                'quiz_scores': quiz_score,
                'related_skills': skills_score,
                'self_reported': self_reported_score,
                'time_decay_applied': base_score != time_adjusted_score
            }
        )

        logger.info(
            f"✅ Knowledge score for {topic}: {final_score}/100 "
            f"(confidence: {confidence:.2f})"
        )

        return knowledge_score

    def recommend_module_difficulty(
        self,
        knowledge_score: KnowledgeScore,
        learning_preferences: Dict[str, Any]
    ) -> DifficultyRecommendation:
        """
        Recommend appropriate module difficulty based on knowledge score.

        Maps 0-100 knowledge score to 0-100 difficulty range.
        Considers user's learning pace preference.

        Args:
            knowledge_score: User's knowledge score
            learning_preferences: User's learning preferences

        Returns:
            DifficultyRecommendation with min/max difficulty range

        Example:
            Knowledge 45 → Difficulty 35-60 (slightly easier to slightly harder)
        """
        score = knowledge_score.score
        pace = learning_preferences.get('preferred_pace', 'medium')

        # Map knowledge score to difficulty range
        # Users should start slightly below their knowledge level
        # and progress to slightly above
        if score < 20:
            # Absolute beginners
            optimal_start = 10
            min_diff = 5
            max_diff = 30
        elif score < 40:
            # Beginners with basics
            optimal_start = score - 5
            min_diff = score - 10
            max_diff = score + 20
        elif score < 60:
            # Intermediate
            optimal_start = score
            min_diff = score - 15
            max_diff = score + 25
        elif score < 80:
            # Advanced
            optimal_start = score + 5
            min_diff = score - 10
            max_diff = score + 20
        else:
            # Expert
            optimal_start = score + 10
            min_diff = score - 15
            max_diff = 100

        # Adjust based on pace preference
        if pace == 'slow':
            # More conservative - start easier
            optimal_start = max(5, optimal_start - 10)
            min_diff = max(0, min_diff - 10)
            progression_rate = 'slow'
        elif pace == 'fast':
            # More aggressive - push harder
            optimal_start = min(95, optimal_start + 10)
            max_diff = min(100, max_diff + 10)
            progression_rate = 'fast'
        else:
            progression_rate = 'medium'

        # Ensure valid ranges
        min_diff = max(0, min_diff)
        max_diff = min(100, max_diff)
        optimal_start = max(min_diff, min(max_diff, optimal_start))

        recommendation = DifficultyRecommendation(
            min_difficulty=int(min_diff),
            max_difficulty=int(max_diff),
            optimal_starting_difficulty=int(optimal_start),
            progression_rate=progression_rate
        )

        logger.info(
            f"📈 Difficulty recommendation: {optimal_start} "
            f"(range {min_diff}-{max_diff})"
        )

        return recommendation

    def _fetch_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Fetch user's learning history and profile data.

        Args:
            user_id: User's ID

        Returns:
            Dictionary with user data
        """
        try:
            from core.apps.preferences.models import UserPreference
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Get user preferences from MongoDB
            try:
                user_pref = UserPreference.objects.get(user_id=user_id)

                user_data = {
                    'user_id': user_id,
                    'learning_goals': user_pref.basic_info.learning_goals if user_pref.basic_info else [],
                    'experience_level': user_pref.basic_info.experience_level if user_pref.basic_info else 'complete_beginner',
                    'completed_courses': [],  # TODO: Fetch from LearningPath model
                    'quiz_scores': {},  # TODO: Fetch from assessment results
                    'skills': user_pref.basic_info.current_skills if user_pref.basic_info else [],
                    'last_activity': user_pref.last_updated,
                }

            except UserPreference.DoesNotExist:
                logger.warning(f"No preferences found for user {user_id}")
                user_data = {
                    'user_id': user_id,
                    'learning_goals': [],
                    'experience_level': 'complete_beginner',
                    'completed_courses': [],
                    'quiz_scores': {},
                    'skills': [],
                    'last_activity': datetime.now(),
                }

            return user_data

        except Exception as e:
            logger.error(f"Failed to fetch user data: {e}")
            # Return minimal data
            return {
                'user_id': user_id,
                'learning_goals': [],
                'experience_level': 'complete_beginner',
                'completed_courses': [],
                'quiz_scores': {},
                'skills': [],
                'last_activity': datetime.now(),
            }

    def _score_from_completed_courses(
        self,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Score based on completed courses related to the topic.

        Args:
            user_data: User's data
            topic: Topic to assess

        Returns:
            Score 0-100
        """
        completed_courses = user_data.get('completed_courses', [])

        if not completed_courses:
            return 0.0

        # Count relevant courses
        # TODO: Use semantic matching to find related courses
        topic_lower = topic.lower()
        relevant_courses = [
            course for course in completed_courses
            if topic_lower in course.get('title', '').lower()
        ]

        if not relevant_courses:
            return 0.0

        # Score based on number of completed courses
        # 1 course = 40, 2 courses = 60, 3+ courses = 80
        count = len(relevant_courses)
        if count == 1:
            return 40.0
        elif count == 2:
            return 60.0
        else:
            return 80.0

    def _score_from_quiz_results(
        self,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Score based on quiz/assessment results for the topic.

        Args:
            user_data: User's data
            topic: Topic to assess

        Returns:
            Score 0-100
        """
        quiz_scores = user_data.get('quiz_scores', {})

        if not quiz_scores:
            return 50.0  # Neutral score if no data

        # Get average quiz score for this topic
        # TODO: Implement quiz system and fetch actual results
        topic_lower = topic.lower()
        relevant_scores = [
            score for key, score in quiz_scores.items()
            if topic_lower in key.lower()
        ]

        if not relevant_scores:
            return 50.0  # Neutral score

        # Return average of quiz scores
        return sum(relevant_scores) / len(relevant_scores)

    def _score_from_related_skills(
        self,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Score based on related skills in user's profile.

        Args:
            user_data: User's data
            topic: Topic to assess

        Returns:
            Score 0-100
        """
        skills = user_data.get('skills', [])

        if not skills:
            return 0.0

        # Check for exact or partial matches
        topic_lower = topic.lower()
        exact_match = topic_lower in [s.lower() for s in skills]

        # For related technologies, give partial credit
        # e.g., JavaScript skills help with React
        related_tech_map = {
            'react': ['javascript', 'html', 'css', 'jsx'],
            'vue': ['javascript', 'html', 'css'],
            'angular': ['javascript', 'typescript', 'html', 'css'],
            'node': ['javascript'],
            'express': ['javascript', 'node'],
            'django': ['python'],
            'flask': ['python'],
            'react native': ['react', 'javascript'],
            'flutter': ['dart'],
            'ios': ['swift', 'objective-c'],
            'android': ['kotlin', 'java']
        }

        related_skills = related_tech_map.get(topic_lower, [])
        related_count = sum(
            1 for skill in skills
            if skill.lower() in related_skills
        )

        if exact_match:
            return 70.0  # High score for exact match
        elif related_count > 0:
            # Give significant credit for related skills
            return min(60.0, 35.0 + (related_count * 10.0))
        else:
            return 0.0

    def _score_from_self_report(
        self,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Score based on user's self-reported experience level.

        This is the least reliable indicator, so it has low weight.

        Args:
            user_data: User's data
            topic: Topic to assess

        Returns:
            Score 0-100
        """
        experience_level = user_data.get('experience_level', 'complete_beginner')

        # Map experience levels to scores
        experience_map = {
            'complete_beginner': 10,
            'some_basics': 35,
            'intermediate': 55,
            'advanced': 75,
            'expert': 90
        }

        return float(experience_map.get(experience_level, 10))

    def _apply_time_decay(
        self,
        base_score: float,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Apply time decay to knowledge score.

        Knowledge fades without practice. This uses exponential decay.

        Args:
            base_score: Original score before decay
            user_data: User's data
            topic: Topic being assessed

        Returns:
            Time-adjusted score
        """
        last_activity = user_data.get('last_activity', datetime.now())

        # Calculate days since last activity
        days_inactive = (datetime.now() - last_activity).days

        if days_inactive <= 0:
            return base_score

        # Exponential decay formula: score * (0.5 ^ (days / half_life))
        decay_factor = 0.5 ** (days_inactive / self.KNOWLEDGE_HALF_LIFE_DAYS)

        # Don't decay below max_decay_factor
        decay_factor = max(self.MAX_DECAY_FACTOR, decay_factor)

        decayed_score = base_score * decay_factor

        if decayed_score < base_score:
            logger.debug(
                f"⏰ Knowledge decay: {base_score:.1f} → {decayed_score:.1f} "
                f"({days_inactive} days inactive)"
            )

        return decayed_score

    def _calculate_confidence(
        self,
        user_data: Dict[str, Any],
        topic: str
    ) -> float:
        """
        Calculate confidence in the knowledge score.

        Higher confidence when we have more data points.

        Args:
            user_data: User's data
            topic: Topic being assessed

        Returns:
            Confidence 0.0-1.0
        """
        data_points = 0

        # Count available data points
        if user_data.get('completed_courses'):
            data_points += 1
        if user_data.get('quiz_scores'):
            data_points += 1
        if user_data.get('skills'):
            data_points += 1
        if user_data.get('experience_level'):
            data_points += 1

        # More data points = higher confidence
        # 0 points = 0.2, 1 point = 0.4, 2 points = 0.6, 3 points = 0.8, 4 points = 1.0
        confidence = min(1.0, 0.2 + (data_points * 0.2))

        return confidence

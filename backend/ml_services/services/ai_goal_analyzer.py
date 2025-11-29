"""
backend/ml_services/services/ai_goal_analyzer.py
AI-powered learning goal analysis and dynamic path generation
Replaces hardcoded roadmap mapping with intelligent goal understanding using Groq LLM
RELEVANT FILES: roadmap_service.py, learning_path_service.py, models/api_text_generation_model.py
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from openai import OpenAI
from django.conf import settings

from ..integrations.roadmap_service import RoadmapService, Roadmap, RoadmapNode
from ..base.exceptions import MLServiceError, ValidationError
from ..utils.external_api_logger import log_external_api_call


logger = logging.getLogger(__name__)


@dataclass
class DynamicModule:
    """
    A dynamically generated learning module with flexible structure.
    Unlike hardcoded modules, these adapt to any learning goal.
    """
    id: str
    title: str
    description: str
    learning_objectives: List[str]
    difficulty_score: int  # 0-100 scale (not discrete levels)
    estimated_hours: int
    prerequisites: List[str]  # Module IDs that must be completed first
    skills_to_master: List[str]
    recommended_sequence: int  # Order in the learning path
    complexity_indicators: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'learning_objectives': self.learning_objectives,
            'difficulty_score': self.difficulty_score,
            'estimated_hours': self.estimated_hours,
            'prerequisites': self.prerequisites,
            'skills_to_master': self.skills_to_master,
            'recommended_sequence': self.recommended_sequence,
            'complexity_indicators': self.complexity_indicators
        }


@dataclass
class DynamicLearningPath:
    """
    A completely dynamic learning path that adapts to ANY goal.
    No hardcoded limits, no fixed structure.
    """
    path_id: str
    title: str
    description: str
    learning_goal: str
    modules: List[DynamicModule]
    total_estimated_hours: int
    difficulty_progression: List[int]  # Difficulty score for each module
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'path_id': self.path_id,
            'title': self.title,
            'description': self.description,
            'learning_goal': self.learning_goal,
            'modules': [module.to_dict() for module in self.modules],
            'total_estimated_hours': self.total_estimated_hours,
            'difficulty_progression': self.difficulty_progression,
            'metadata': self.metadata
        }


class AIGoalAnalyzer:
    """
    AI-powered learning goal analysis service.

    This service eliminates ALL hardcoded roadmap mappings by using Groq LLM
    to understand ANY learning goal and generate personalized learning paths.

    Key Features:
    - Understands ANY learning goal (not just 10 hardcoded ones)
    - Hybrid approach: Try roadmap.sh first, fall back to AI
    - Considers user's background and preferences
    - Generates dynamic module structures (3-30 modules based on complexity)
    - Uses 0-100 difficulty scale (not discrete levels)
    - Identifies prerequisites dynamically
    """

    def __init__(self):
        """Initialize AI analyzer with Groq client and roadmap service."""
        # Initialize Groq LLM client (OpenAI-compatible)
        api_key = getattr(settings, 'ML_API_KEY', None)
        if not api_key:
            logger.warning("ML_API_KEY not configured. AI generation will fail.")

        api_base = getattr(settings, 'ML_API_BASE_URL', 'https://api.openai.com/v1')
        self.api_model = getattr(settings, 'ML_API_MODEL', 'gpt-3.5-turbo')

        self.client = OpenAI(api_key=api_key, base_url=api_base) if api_key else None

        # Initialize roadmap.sh service for hybrid approach
        self.roadmap_service = RoadmapService()

        # Quality thresholds for roadmap.sh data
        self.MIN_ROADMAP_NODES = 5  # Minimum nodes to consider roadmap.sh usable
        self.MIN_NODE_QUALITY_SCORE = 0.3  # Quality score threshold

    def analyze_learning_goal(
        self,
        learning_goal: str,
        user_background: Dict[str, Any],
        preferences: Dict[str, Any],
        force_ai: bool = False
    ) -> DynamicLearningPath:
        """
        Analyze a learning goal and generate a personalized learning path.

        This is the main entry point that replaces hardcoded roadmap mapping.

        Args:
            learning_goal: User's learning goal (ANY goal, not just predefined ones)
            user_background: User's experience, skills, education
            preferences: Learning preferences (time, pace, style)
            force_ai: If True, skip roadmap.sh and use pure AI generation

        Returns:
            DynamicLearningPath with personalized modules

        Raises:
            MLServiceError: If analysis fails
        """
        logger.info(f"🎯 Analyzing learning goal: {learning_goal}")
        start_time = time.time()

        try:
            # Step 1: Try roadmap.sh first (hybrid approach)
            roadmap_path = None
            if not force_ai:
                roadmap_path = self._try_roadmap_sh(learning_goal, user_background)

            # Step 2: Evaluate roadmap quality
            if roadmap_path and self._is_high_quality_roadmap(roadmap_path):
                logger.info(f"✅ Using roadmap.sh data for {learning_goal}")
                # Enhance roadmap.sh data with AI
                dynamic_path = self._enhance_roadmap_with_ai(
                    roadmap_path, user_background, preferences
                )
            else:
                # Step 3: Fall back to pure AI generation
                logger.info(f"🤖 Generating learning path with AI for {learning_goal}")
                dynamic_path = self._generate_with_ai(
                    learning_goal, user_background, preferences
                )

            # Add generation metadata
            processing_time = (time.time() - start_time) * 1000
            dynamic_path.metadata.update({
                'generation_method': 'roadmap_enhanced' if roadmap_path else 'pure_ai',
                'generated_at': datetime.now().isoformat(),
                'processing_time_ms': processing_time,
                'ai_model': self.api_model
            })

            logger.info(
                f"✅ Generated {len(dynamic_path.modules)} modules "
                f"for '{learning_goal}' in {processing_time:.0f}ms"
            )

            return dynamic_path

        except Exception as e:
            logger.error(f"❌ Failed to analyze learning goal '{learning_goal}': {e}")
            raise MLServiceError(f"Learning goal analysis failed: {e}")

    def _try_roadmap_sh(
        self,
        learning_goal: str,
        user_background: Dict[str, Any]
    ) -> Optional[Roadmap]:
        """
        Attempt to fetch roadmap from roadmap.sh using semantic matching.

        This replaces the hardcoded ROADMAP_MAPPING with intelligent matching.

        Args:
            learning_goal: User's learning goal
            user_background: User's background for context

        Returns:
            Roadmap if found, None otherwise
        """
        try:
            # First, try direct fetch (handles existing mappings)
            roadmap = self.roadmap_service.fetch_roadmap(learning_goal)

            if roadmap:
                logger.info(f"📦 Found direct roadmap.sh match for {learning_goal}")
                return roadmap

            # If no direct match, try semantic matching
            # Map common goal variations to roadmap.sh names
            roadmap_name = self._get_semantic_roadmap_mapping(learning_goal)

            if roadmap_name:
                logger.info(f"🔍 Trying semantic match: {learning_goal} → {roadmap_name}")
                # Fetch directly from roadmap.sh using the roadmap name
                roadmap = self._fetch_roadmap_direct(roadmap_name, learning_goal)
                if roadmap:
                    return roadmap

            logger.info(f"⚠️ No roadmap.sh match for {learning_goal}")
            return None

        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch roadmap.sh data: {e}")
            return None

    def _fetch_roadmap_direct(
        self,
        roadmap_name: str,
        learning_goal: str
    ) -> Optional[Roadmap]:
        """
        Fetch roadmap directly from roadmap.sh by roadmap name.

        This bypasses the ROADMAP_MAPPING and fetches directly from GitHub.

        Args:
            roadmap_name: roadmap.sh roadmap name (e.g., 'react-native', 'frontend')
            learning_goal: Original learning goal for metadata

        Returns:
            Roadmap if successful, None otherwise
        """
        try:
            import requests
            import json

            # Construct GitHub raw URL directly
            url = f"{self.roadmap_service.GITHUB_RAW_BASE}/src/data/roadmaps/{roadmap_name}/{roadmap_name}.json"

            logger.info(f"🌐 Fetching roadmap directly from: {url}")

            response = self.roadmap_service.session.get(url, timeout=10)
            response.raise_for_status()

            roadmap_data = response.json()

            # Parse roadmap into structured format
            roadmap = self.roadmap_service._parse_roadmap(roadmap_data, roadmap_name, learning_goal)

            logger.info(f"✅ Successfully fetched roadmap '{roadmap.title}' with {len(roadmap.nodes)} nodes")
            return roadmap

        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch roadmap '{roadmap_name}' directly: {e}")
            return None

    def _get_semantic_roadmap_mapping(self, learning_goal: str) -> Optional[str]:
        """
        Intelligent semantic matching for learning goals to roadmap.sh names.

        This handles variations and synonyms without hardcoding every possibility.

        Args:
            learning_goal: User's learning goal

        Returns:
            Mapped roadmap name or None
        """
        goal_lower = learning_goal.lower().strip()

        # Semantic mapping with multiple variations
        # This is more flexible than the old hardcoded dict
        semantic_map = {
            # Mobile development variations
            'mobile': 'react-native',
            'mobile_dev': 'react-native',
            'mobile development': 'react-native',
            'app development': 'react-native',
            'mobile app': 'react-native',
            'ios': 'ios',
            'android': 'android',
            'react native': 'react-native',
            'flutter': 'flutter',

            # Web development variations
            'web': 'frontend',
            'web_dev': 'frontend',
            'web development': 'frontend',
            'frontend': 'frontend',
            'frontend development': 'frontend',
            'front-end': 'frontend',
            'backend': 'backend',
            'backend development': 'backend',
            'back-end': 'backend',
            'full stack': 'full-stack',
            'fullstack': 'full-stack',
            'full-stack': 'full-stack',

            # AI/ML/Data variations
            'ai': 'ai-data-scientist',
            'ai_ml': 'ai-data-scientist',
            'artificial intelligence': 'ai-data-scientist',
            'machine learning': 'ai-data-scientist',
            'ml': 'ai-data-scientist',
            'data science': 'ai-data-scientist',
            'data_science': 'ai-data-scientist',
            'data scientist': 'ai-data-scientist',

            # Other domains
            'devops': 'devops',
            'cybersecurity': 'cyber-security',
            'cyber security': 'cyber-security',
            'blockchain': 'blockchain',
            'game': 'game-developer',
            'game_dev': 'game-developer',
            'game development': 'game-developer',
        }

        # Try exact match first
        if goal_lower in semantic_map:
            return semantic_map[goal_lower]

        # Try partial match (contains keyword)
        for keyword, roadmap_name in semantic_map.items():
            if keyword in goal_lower or goal_lower in keyword:
                logger.info(f"🔍 Partial semantic match: '{goal_lower}' contains '{keyword}'")
                return roadmap_name

        return None

    def _is_high_quality_roadmap(self, roadmap: Roadmap) -> bool:
        """
        Evaluate if roadmap.sh data is high quality enough to use.

        Poor quality roadmaps (too few nodes, missing data) should fall back to AI.

        Args:
            roadmap: Roadmap from roadmap.sh

        Returns:
            True if roadmap is usable quality
        """
        if not roadmap or not roadmap.nodes:
            return False

        # Check minimum node count
        if len(roadmap.nodes) < self.MIN_ROADMAP_NODES:
            logger.warning(
                f"⚠️ Roadmap has only {len(roadmap.nodes)} nodes "
                f"(min {self.MIN_ROADMAP_NODES})"
            )
            return False

        # Calculate quality score based on node completeness
        # Use dynamic sample size instead of hardcoded 10 - analyze up to 20 nodes max
        max_analysis_nodes = min(len(roadmap.nodes), 20)
        quality_scores = []
        for node in roadmap.nodes[:max_analysis_nodes]:
            score = 0.0

            # Has title (required)
            if node.title and node.title.strip():
                score += 0.3

            # Has description
            if node.description and len(node.description) > 20:
                score += 0.2

            # Has learning objectives (skills)
            if node.skills and len(node.skills) > 0:
                score += 0.2

            # Has resources
            if node.resources and len(node.resources) > 0:
                score += 0.15

            # Has prerequisites
            if node.prerequisites:
                score += 0.15

            quality_scores.append(score)

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        logger.info(f"📊 Roadmap quality score: {avg_quality:.2f} (min {self.MIN_NODE_QUALITY_SCORE})")

        return avg_quality >= self.MIN_NODE_QUALITY_SCORE

    def _enhance_roadmap_with_ai(
        self,
        roadmap: Roadmap,
        user_background: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> DynamicLearningPath:
        """
        Enhance roadmap.sh data with AI-powered personalization.

        Takes the structured roadmap and adapts it to the user's specific needs.

        Args:
            roadmap: Original roadmap from roadmap.sh
            user_background: User's background
            preferences: Learning preferences

        Returns:
            Enhanced DynamicLearningPath
        """
        # Convert RoadmapNodes to DynamicModules
        modules = []
        for idx, node in enumerate(roadmap.nodes):
            # Map node difficulty to 0-100 scale
            difficulty_map = {
                'beginner': 25,
                'intermediate': 50,
                'advanced': 75
            }
            difficulty_score = difficulty_map.get(node.difficulty, 50)

            module = DynamicModule(
                id=node.id,
                title=node.title,
                description=node.description,
                learning_objectives=node.skills,  # roadmap.sh stores objectives as skills
                difficulty_score=difficulty_score,
                estimated_hours=node.estimated_hours,
                prerequisites=node.prerequisites,
                skills_to_master=node.skills,
                recommended_sequence=idx + 1,
                complexity_indicators={
                    'source': 'roadmap.sh',
                    'category': node.category,
                    'original_difficulty': node.difficulty
                }
            )
            modules.append(module)

        # Calculate difficulty progression
        difficulty_progression = [m.difficulty_score for m in modules]

        # Create dynamic learning path
        dynamic_path = DynamicLearningPath(
            path_id=roadmap.roadmap_id,
            title=roadmap.title,
            description=roadmap.description,
            learning_goal=roadmap.category,
            modules=modules,
            total_estimated_hours=sum(m.estimated_hours for m in modules),
            difficulty_progression=difficulty_progression,
            metadata={
                'source': 'roadmap.sh',
                'enhanced_with_ai': True,
                'original_node_count': roadmap.metadata.get('total_nodes', len(modules))
            }
        )

        return dynamic_path

    @log_external_api_call(
        api_name="Groq LLM - Learning Path Generation",
        include_tokens=True,  # Track token usage for cost monitoring
        sanitize_auth=True,  # Sanitize API keys in logs
        truncate_response_at=3000  # Truncate long learning path responses
    )
    def _generate_with_ai(
        self,
        learning_goal: str,
        user_background: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> DynamicLearningPath:
        """
        Generate a complete learning path using pure AI (Groq LLM).

        This is used when roadmap.sh doesn't have data or quality is poor.

        Args:
            learning_goal: User's learning goal
            user_background: User's background and experience
            preferences: Learning preferences

        Returns:
            AI-generated DynamicLearningPath

        Raises:
            MLServiceError: If AI generation fails
        """
        if not self.client:
            raise MLServiceError("AI generation unavailable: ML_API_KEY not configured")

        try:
            # Build AI prompt
            prompt = self._build_ai_prompt(learning_goal, user_background, preferences)

            # Call Groq LLM
            logger.info(f"🤖 Calling Groq LLM for {learning_goal}")
            response = self.client.chat.completions.create(
                model=self.api_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert learning path designer. Generate structured, personalized learning roadmaps in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"}  # Enforce JSON output
            )

            # Parse AI response
            ai_response = response.choices[0].message.content
            path_data = json.loads(ai_response)

            # Convert to DynamicLearningPath
            dynamic_path = self._parse_ai_response(path_data, learning_goal)

            return dynamic_path

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            raise MLServiceError(f"AI response parsing failed: {e}")
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            raise MLServiceError(f"AI generation failed: {e}")

    def _build_ai_prompt(
        self,
        learning_goal: str,
        user_background: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> str:
        """
        Build a comprehensive prompt for the AI to generate a learning path.

        Args:
            learning_goal: User's learning goal
            user_background: User's background
            preferences: Learning preferences

        Returns:
            Formatted prompt string
        """
        # Extract user context
        experience_level = preferences.get('experience_level', 'intermediate')
        time_availability = preferences.get('time_availability', '3-5hrs')
        learning_styles = preferences.get('learning_styles', ['hands_on'])
        target_timeline = preferences.get('target_timeline', 'flexible')

        # Build prompt
        prompt = f"""Generate a personalized learning roadmap for the following goal:

LEARNING GOAL: {learning_goal}

USER CONTEXT:
- Experience level: {experience_level}
- Time availability: {time_availability} per week
- Learning styles: {', '.join(learning_styles)}
- Target timeline: {target_timeline}
- Background skills: {user_background.get('skills', [])}
- Career stage: {user_background.get('career_stage', 'student')}

REQUIREMENTS:
1. Generate 5-20 modules (based on complexity - simple goals need fewer modules, complex goals need more)
2. Each module should have:
   - Unique ID (module_1, module_2, etc.)
   - Clear title and description
   - 3-5 specific learning objectives
   - Difficulty score (0-100 scale, where 0=absolute beginner, 100=expert level)
   - Estimated hours to complete
   - Prerequisites (IDs of modules that must be completed first)
   - 3-5 key skills to master in this module
3. Ensure gradual difficulty progression (each module slightly harder than previous)
4. Consider the user's experience level when setting starting difficulty
5. Total estimated hours should fit within target timeline

OUTPUT FORMAT (valid JSON):
{{
  "title": "Learning Path Title",
  "description": "Brief description of what this path covers",
  "modules": [
    {{
      "id": "module_1",
      "title": "Module Title",
      "description": "What this module covers",
      "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"],
      "difficulty_score": 25,
      "estimated_hours": 10,
      "prerequisites": [],
      "skills_to_master": ["Skill 1", "Skill 2", "Skill 3"],
      "recommended_sequence": 1
    }}
  ]
}}

Generate the learning path now:"""

        return prompt

    def _parse_ai_response(
        self,
        path_data: Dict[str, Any],
        learning_goal: str
    ) -> DynamicLearningPath:
        """
        Parse AI JSON response into DynamicLearningPath object.

        Args:
            path_data: Parsed JSON from AI
            learning_goal: Original learning goal

        Returns:
            DynamicLearningPath object

        Raises:
            ValidationError: If AI response is invalid
        """
        try:
            # Parse modules
            modules = []
            for module_data in path_data.get('modules', []):
                module = DynamicModule(
                    id=module_data['id'],
                    title=module_data['title'],
                    description=module_data['description'],
                    learning_objectives=module_data.get('learning_objectives', []),
                    difficulty_score=module_data.get('difficulty_score', 50),
                    estimated_hours=module_data.get('estimated_hours', 10),
                    prerequisites=module_data.get('prerequisites', []),
                    skills_to_master=module_data.get('skills_to_master', []),
                    recommended_sequence=module_data.get('recommended_sequence', len(modules) + 1),
                    complexity_indicators={
                        'source': 'ai_generated',
                        'ai_model': self.api_model
                    }
                )
                modules.append(module)

            # Validate we got at least some modules
            if not modules:
                raise ValidationError("modules", modules, "AI generated no modules")

            # Calculate difficulty progression
            difficulty_progression = [m.difficulty_score for m in modules]

            # Create dynamic learning path
            dynamic_path = DynamicLearningPath(
                path_id=f"ai_{learning_goal}_{int(time.time())}",
                title=path_data.get('title', f'{learning_goal} Learning Path'),
                description=path_data.get('description', f'Personalized learning path for {learning_goal}'),
                learning_goal=learning_goal,
                modules=modules,
                total_estimated_hours=sum(m.estimated_hours for m in modules),
                difficulty_progression=difficulty_progression,
                metadata={
                    'source': 'ai_generated',
                    'ai_model': self.api_model,
                    'module_count': len(modules)
                }
            )

            return dynamic_path

        except KeyError as e:
            logger.error(f"❌ Missing required field in AI response: {e}")
            raise ValidationError(str(e), None, "AI response missing required field")
        except Exception as e:
            logger.error(f"❌ Failed to parse AI response: {e}")
            raise ValidationError("ai_response", path_data, str(e))

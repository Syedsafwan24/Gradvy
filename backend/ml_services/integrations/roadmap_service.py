"""
backend/ml_services/integrations/roadmap_service.py
Roadmap.sh integration service - fetches and parses structured learning roadmaps
Why: Provides curated learning paths from roadmap.sh instead of AI-generated content
RELEVANT FILES: learning_path_service.py, course_search_service.py, views.py
"""

import json
import logging
import requests
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, deque

# Import external API logger for tracking roadmap.sh GitHub API calls
from ..utils.external_api_logger import log_external_api_call


logger = logging.getLogger(__name__)


@dataclass
class RoadmapNode:
    """
    Represents a single node/topic in a learning roadmap.
    Each node can have prerequisites and dependencies.
    """
    id: str
    title: str
    description: str = ""
    category: str = ""
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    estimated_hours: int = 10
    prerequisites: List[str] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)


@dataclass
class Roadmap:
    """
    Complete roadmap structure with metadata and ordered nodes.
    """
    roadmap_id: str
    title: str
    description: str
    category: str
    nodes: List[RoadmapNode]
    metadata: Dict = field(default_factory=dict)


class RoadmapService:
    """
    Service for fetching and parsing roadmaps from roadmap.sh GitHub repository.

    Roadmap.sh stores roadmaps as JSON files in their GitHub repo:
    https://github.com/kamranahmedse/developer-roadmap

    This service:
    1. Fetches roadmap JSON from GitHub raw URL
    2. Parses the structure into RoadmapNode objects
    3. Performs topological sort for prerequisite ordering
    4. Returns structured learning path data
    """

    # GitHub raw content base URL for roadmap.sh
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/master"

    # Mapping of our learning goals to roadmap.sh roadmap files
    ROADMAP_MAPPING = {
        'web_dev': 'frontend',
        'mobile_dev': 'react-native',  # Cross-platform mobile development (React Native)
        'ai_ml': 'ai-data-scientist',
        'data_science': 'ai-data-scientist',
        'devops': 'devops',
        'cybersecurity': 'cyber-security',
        'blockchain': 'blockchain',
        'backend_dev': 'backend',
        'full_stack': 'full-stack',
        'game_dev': 'game-developer',
    }

    def __init__(self):
        """Initialize the roadmap service with HTTP session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Gradvy-Learning-Platform/1.0'
        })
        self._cache = {}  # Simple in-memory cache

    @log_external_api_call(
        api_name="roadmap.sh GitHub Raw Content",
        include_headers=False,
        truncate_response_at=5000  # Roadmap JSON can be large
    )
    def fetch_roadmap(self, learning_goal: str) -> Optional[Roadmap]:
        """
        Fetch a roadmap for the given learning goal.

        Args:
            learning_goal: User's learning goal (e.g., 'web_dev', 'ai_ml')

        Returns:
            Roadmap object with structured learning path, or None if not found
        """
        # Check cache first
        if learning_goal in self._cache:
            logger.info(f"📦 Using cached roadmap for {learning_goal}")
            return self._cache[learning_goal]

        # Map learning goal to roadmap.sh roadmap
        roadmap_name = self.ROADMAP_MAPPING.get(learning_goal)
        if not roadmap_name:
            logger.warning(f"⚠️ No roadmap mapping found for learning goal: {learning_goal}")
            return None

        try:
            # Fetch roadmap JSON from GitHub
            url = f"{self.GITHUB_RAW_BASE}/src/data/roadmaps/{roadmap_name}/{roadmap_name}.json"
            logger.info(f"🌐 Fetching roadmap from: {url}")
            logger.info(f"📂 Expected filename: {roadmap_name}.json")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            roadmap_data = response.json()

            # Parse roadmap into structured format
            roadmap = self._parse_roadmap(roadmap_data, roadmap_name, learning_goal)

            # Cache the result
            self._cache[learning_goal] = roadmap

            logger.info(f"✅ Successfully fetched roadmap '{roadmap.title}' with {len(roadmap.nodes)} nodes")
            return roadmap

        except requests.RequestException as e:
            logger.error(f"❌ Failed to fetch roadmap from GitHub: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Failed to parse roadmap JSON: {e}")
            return None

    def _parse_roadmap(self, roadmap_data: Dict, roadmap_name: str, learning_goal: str) -> Roadmap:
        """
        Parse roadmap JSON from roadmap.sh into our Roadmap structure.

        Roadmap.sh uses a graph structure with nodes and edges.
        We convert this to a linear learning path using topological sort.

        Args:
            roadmap_data: Raw JSON data from roadmap.sh
            roadmap_name: Name of the roadmap (e.g., 'frontend')
            learning_goal: User's learning goal

        Returns:
            Parsed Roadmap object
        """
        # DEBUG: Log the actual JSON structure from roadmap.sh to understand field names
        logger.debug(f"🔍 Debugging roadmap.sh JSON structure for {roadmap_name}")
        logger.debug(f"Top-level keys: {list(roadmap_data.keys())}")

        # Sample first node to see actual field structure
        sample_nodes = roadmap_data.get('nodes', roadmap_data.get('topics', []))
        if sample_nodes and len(sample_nodes) > 0:
            logger.debug(f"Sample node structure (first node): {json.dumps(sample_nodes[0], indent=2)}")
            logger.debug(f"Sample node keys: {list(sample_nodes[0].keys())}")
        else:
            logger.warning(f"⚠️ No nodes/topics found in roadmap_data. Full data: {json.dumps(roadmap_data, indent=2)[:500]}")

        nodes = []
        node_map = {}

        # Extract nodes from roadmap data
        # Roadmap.sh structure varies, so we handle multiple formats
        roadmap_nodes = roadmap_data.get('nodes', [])
        if not roadmap_nodes:
            # Try alternative structure
            roadmap_nodes = roadmap_data.get('topics', [])

        # Parse each node - FILTER out UI nodes, keep only learning topics
        # roadmap.sh JSON contains UI elements (vertical lines, paragraphs, legends)
        # We only want actual topic/subtopic nodes with learning content
        SKIP_NODE_TYPES = {'vertical', 'horizontal', 'paragraph', 'legend', 'title', 'button'}
        TOPIC_NODE_TYPES = {'topic', 'subtopic', 'resource'}

        for idx, node_data in enumerate(roadmap_nodes):
            node_id = node_data.get('id', str(len(nodes)))
            node_type = node_data.get('type', '')

            # DEBUG: Log first 3 nodes to see actual field structure
            if idx < 3:
                logger.debug(f"Node {idx} raw data: {json.dumps(node_data, indent=2)}")
                logger.debug(f"Node {idx} - id: {node_id}, type: {node_type}, keys: {list(node_data.keys())}")

            # FILTER: Skip UI elements - only process actual learning topics
            if node_type in SKIP_NODE_TYPES:
                logger.debug(f"Skipping UI node {idx} - type: {node_type}")
                continue

            # Extract title and description
            # roadmap.sh stores title in data.label (nested structure)
            data_obj = node_data.get('data', {})
            title = (
                node_data.get('title') or
                data_obj.get('label') or
                node_data.get('label') or
                ''  # Empty string instead of fallback - we'll filter below
            )
            description = (
                node_data.get('description') or
                data_obj.get('description') or
                node_data.get('desc') or
                ''
            )

            # FILTER: Skip nodes with no meaningful title
            if not title or title.strip() == '':
                logger.debug(f"Skipping node {idx} with empty title - type: {node_type}")
                continue

            # DEBUG: Log when unexpected node type is kept
            if node_type not in TOPIC_NODE_TYPES:
                logger.info(f"ℹ️ Keeping node with unusual type '{node_type}': {title}")

            # Extract category and difficulty
            category = node_data.get('category', roadmap_name)
            difficulty = node_data.get('difficulty', 'intermediate')

            # Extract prerequisites (dependencies/edges pointing to this node)
            prerequisites = node_data.get('dependencies', [])
            if not prerequisites:
                prerequisites = node_data.get('prerequisites', [])

            # Extract resources if available
            resources = node_data.get('resources', [])

            # Extract skills/topics
            skills = node_data.get('skills', [])
            if not skills and isinstance(title, str):
                # Extract keywords from title as skills
                skills = [word.strip() for word in title.split(',')]

            # Create roadmap node
            node = RoadmapNode(
                id=node_id,
                title=title,
                description=description,
                category=category,
                difficulty=difficulty,
                estimated_hours=node_data.get('hours', 10),
                prerequisites=prerequisites,
                resources=resources,
                skills=skills
            )

            nodes.append(node)
            node_map[node_id] = node

        # Perform topological sort to order nodes by prerequisites
        sorted_nodes = self._topological_sort(nodes, node_map)

        # Create roadmap object
        roadmap = Roadmap(
            roadmap_id=roadmap_name,
            title=roadmap_data.get('title', roadmap_name.replace('-', ' ').title()),
            description=roadmap_data.get('description', f'Learning roadmap for {learning_goal}'),
            category=learning_goal,
            nodes=sorted_nodes,
            metadata={
                'source': 'roadmap.sh',
                'total_nodes': len(sorted_nodes),
                'estimated_total_hours': sum(node.estimated_hours for node in sorted_nodes)
            }
        )

        return roadmap

    def _topological_sort(self, nodes: List[RoadmapNode], node_map: Dict[str, RoadmapNode]) -> List[RoadmapNode]:
        """
        Perform topological sort on roadmap nodes based on prerequisites.

        This ensures that prerequisite topics come before dependent topics
        in the learning path.

        Uses Kahn's algorithm for topological sorting.

        Args:
            nodes: List of RoadmapNode objects
            node_map: Mapping of node IDs to RoadmapNode objects

        Returns:
            Sorted list of nodes in learning order
        """
        # Build adjacency list and in-degree count
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize all nodes
        for node in nodes:
            if node.id not in in_degree:
                in_degree[node.id] = 0

        # Build graph
        for node in nodes:
            for prereq_id in node.prerequisites:
                if prereq_id in node_map:
                    adj_list[prereq_id].append(node.id)
                    in_degree[node.id] += 1

        # Kahn's algorithm - use queue for BFS
        queue = deque()

        # Add nodes with no prerequisites to queue
        for node in nodes:
            if in_degree[node.id] == 0:
                queue.append(node.id)

        sorted_nodes = []

        while queue:
            # Process node with no remaining prerequisites
            node_id = queue.popleft()
            sorted_nodes.append(node_map[node_id])

            # Reduce in-degree for dependent nodes
            for dependent_id in adj_list[node_id]:
                in_degree[dependent_id] -= 1

                # If all prerequisites are met, add to queue
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        # Check for cycles (if not all nodes were processed)
        if len(sorted_nodes) != len(nodes):
            logger.warning(f"⚠️ Detected cycle in roadmap prerequisites. Using partial sort.")
            # Add remaining nodes at the end
            processed_ids = {node.id for node in sorted_nodes}
            for node in nodes:
                if node.id not in processed_ids:
                    sorted_nodes.append(node)

        return sorted_nodes

    def get_roadmap_for_preferences(self, user_preferences: Dict) -> Optional[Roadmap]:
        """
        Get the most appropriate roadmap based on user preferences.

        Args:
            user_preferences: User's learning preferences with learning_goals

        Returns:
            Roadmap object for the first matching learning goal
        """
        learning_goals = user_preferences.get('basic_info', {}).get('learning_goals', [])

        if not learning_goals:
            logger.warning("⚠️ No learning goals found in user preferences")
            return None

        # Get roadmap for the first learning goal
        primary_goal = learning_goals[0]
        logger.info(f"🎯 Fetching roadmap for primary learning goal: {primary_goal}")

        return self.fetch_roadmap(primary_goal)

    def get_merged_roadmap_for_goals(
        self,
        learning_goals: List[str],
        user_preferences: Dict
    ) -> Optional[Roadmap]:
        """
        PHASE 3: Fetch and merge roadmaps for users with multiple learning goals.

        Example: User wants ["web_dev", "ai_ml"]
        → Merges frontend + ai-data-scientist roadmaps
        → De-duplicates overlapping topics (Python, Git, etc.)
        → Balances modules from both paths

        Args:
            learning_goals: List of learning goals (e.g., ['web_dev', 'ai_ml', 'mobile_dev'])
            user_preferences: User's learning preferences

        Returns:
            Merged Roadmap object, or single roadmap if only one goal
        """
        if not learning_goals:
            logger.warning("⚠️ No learning goals provided for multi-goal merging")
            return None

        # Single goal - still run de-duplication to remove roadmap duplicates
        # BUG FIX: Apply de-duplication to ALL paths, not just multi-goal
        if len(learning_goals) == 1:
            roadmap = self.get_roadmap_for_preferences(user_preferences)
            if roadmap:
                # Apply de-duplication to single roadmap (removes "Learn the basics" duplicates)
                deduplicated_roadmap = self._deduplicate_roadmap_nodes(roadmap)
                return deduplicated_roadmap
            return roadmap

        logger.info(f"🔀 Multi-goal path generation for {len(learning_goals)} goals: {learning_goals}")

        # Fetch all roadmaps (max 3 goals to avoid excessive complexity)
        goal_roadmaps = []
        for goal in learning_goals[:3]:
            roadmap = self.fetch_roadmap(goal)
            if roadmap:
                goal_roadmaps.append((goal, roadmap))
                logger.info(f"   ✓ Fetched {roadmap.title}: {len(roadmap.nodes)} nodes")
            else:
                logger.warning(f"   ✗ No roadmap found for goal: {goal}")

        if not goal_roadmaps:
            logger.error("❌ No roadmaps found for any of the specified goals")
            return None

        # Single roadmap fetched - return it directly
        if len(goal_roadmaps) == 1:
            return goal_roadmaps[0][1]

        # Multiple roadmaps - merge them
        return self._merge_roadmaps(goal_roadmaps, user_preferences)

    def _merge_roadmaps(
        self,
        goal_roadmaps: List[Tuple[str, Roadmap]],
        user_preferences: Dict
    ) -> Roadmap:
        """
        PHASE 3: Merge multiple roadmaps with intelligent de-duplication.

        Merging strategy:
        1. De-duplication: 70% title similarity = duplicate → merge skills
        2. Goal weighting: Primary goal 1.0x, secondary 0.7x, tertiary 0.5x
        3. Shared prerequisites prioritized
        4. Topological sort maintains learning order

        Args:
            goal_roadmaps: List of (goal_name, roadmap) tuples
            user_preferences: User preferences for context

        Returns:
            Merged Roadmap with de-duplicated nodes
        """
        from difflib import SequenceMatcher

        merged_nodes = []
        seen_titles = {}  # title_lower → node
        goal_weights = {0: 1.0, 1: 0.7, 2: 0.5}  # Primary, secondary, tertiary

        logger.info(f"🔀 Merging {len(goal_roadmaps)} roadmaps...")

        for goal_idx, (goal, roadmap) in enumerate(goal_roadmaps):
            weight = goal_weights.get(goal_idx, 0.3)

            for node in roadmap.nodes:
                title_lower = node.title.lower().strip()

                # Check for duplicates using similarity matching
                is_duplicate = False
                for seen_title, existing_node in seen_titles.items():
                    similarity = SequenceMatcher(None, title_lower, seen_title).ratio()

                    if similarity >= 0.7:  # 70% similarity threshold
                        # Duplicate found - merge information
                        logger.debug(f"   🔗 Merging duplicate: '{node.title}' with '{existing_node.title}' ({similarity:.2f} similarity)")

                        # Combine skills from both nodes
                        existing_node.skills = list(set(existing_node.skills + node.skills))

                        # Keep higher goal weight (primary goal takes priority)
                        if weight > existing_node.goal_weight:
                            existing_node.goal_weight = weight

                        # Track which goals this node serves
                        if hasattr(existing_node, 'goal_sources'):
                            existing_node.goal_sources.append(goal)
                        else:
                            existing_node.goal_sources = [existing_node.goal_source if hasattr(existing_node, 'goal_source') else '', goal]

                        is_duplicate = True
                        break

                if not is_duplicate:
                    # New unique node - add it
                    node.goal_weight = weight
                    node.goal_source = goal
                    node.goal_sources = [goal]
                    merged_nodes.append(node)
                    seen_titles[title_lower] = node

        # Sort nodes using topological sort with priority weighting
        sorted_nodes = self._topological_sort_with_priority(merged_nodes)

        # Calculate statistics
        original_total = sum(len(r.nodes) for _, r in goal_roadmaps)
        merged_total = len(sorted_nodes)
        dedup_savings = original_total - merged_total

        # Create merged roadmap
        merged_roadmap = Roadmap(
            roadmap_id=f"merged_{'_'.join([g for g, _ in goal_roadmaps])}",
            title=" + ".join([r.title for _, r in goal_roadmaps]),
            description=f"Combined learning path for {', '.join([g for g, _ in goal_roadmaps])}",
            category="multi_goal",
            nodes=sorted_nodes,
            metadata={
                'merged_goals': [g for g, _ in goal_roadmaps],
                'original_node_counts': {g: len(r.nodes) for g, r in goal_roadmaps},
                'merged_node_count': merged_total,
                'deduplication_savings': dedup_savings,
                'goal_weights': goal_weights
            }
        )

        logger.info(f"✅ Merged roadmap complete:")
        logger.info(f"   Original: {original_total} nodes → Merged: {merged_total} nodes")
        logger.info(f"   Deduplication savings: {dedup_savings} nodes ({dedup_savings/original_total*100:.1f}%)")

        return merged_roadmap

    def _deduplicate_roadmap_nodes(self, roadmap: Roadmap) -> Roadmap:
        """
        BUG FIX: Remove duplicate titles from a single roadmap.

        Uses same 70% similarity logic as multi-goal merging.
        Keeps first instance of each duplicate title (better foundational order).
        Merges skills from duplicates.

        This fixes the bug where "Learn the Basics" appears 3+ times in single-goal paths.

        Args:
            roadmap: Single roadmap that may have duplicate titles

        Returns:
            Roadmap with deduplicated nodes
        """
        from difflib import SequenceMatcher

        deduplicated_nodes = []
        seen_titles = {}  # title_lower → node

        for idx, node in enumerate(roadmap.nodes):
            title_lower = node.title.lower().strip()

            # Check for duplicates using similarity matching
            is_duplicate = False
            for seen_title, existing_node in seen_titles.items():
                similarity = SequenceMatcher(None, title_lower, seen_title).ratio()

                if similarity >= 0.7:  # 70% similarity = duplicate
                    # Merge skills into the first occurrence
                    if len(node.skills) > len(existing_node.skills):
                        # This duplicate has more skills - merge both ways
                        existing_node.skills = list(set(existing_node.skills + node.skills))
                        existing_node.description = node.description or existing_node.description
                    else:
                        # Just merge skills into existing
                        existing_node.skills = list(set(existing_node.skills + node.skills))

                    is_duplicate = True
                    logger.debug(f"🔀 Merged duplicate: '{node.title}' → '{existing_node.title}' ({similarity:.2f} similarity)")
                    break

            if not is_duplicate:
                deduplicated_nodes.append(node)
                seen_titles[title_lower] = node

        duplicates_removed = len(roadmap.nodes) - len(deduplicated_nodes)
        if duplicates_removed > 0:
            logger.info(f"🧹 De-duplication: {len(roadmap.nodes)} → {len(deduplicated_nodes)} nodes (removed {duplicates_removed} duplicates)")

        # Create new roadmap with deduplicated nodes
        deduplicated_roadmap = Roadmap(
            roadmap_id=roadmap.roadmap_id,
            title=roadmap.title,
            description=roadmap.description,
            category=roadmap.category,
            nodes=deduplicated_nodes,
            metadata={
                **roadmap.metadata,
                'deduplicated': True,
                'duplicates_removed': duplicates_removed
            }
        )

        return deduplicated_roadmap

    def _topological_sort_with_priority(
        self,
        nodes: List[RoadmapNode]
    ) -> List[RoadmapNode]:
        """
        PHASE 3: Topological sort with priority weighting for multi-goal paths.

        Sorts nodes by:
        1. Prerequisites (must come before dependents)
        2. Goal weight (primary goal nodes prioritized)
        3. Original position (preserve learning flow)

        Args:
            nodes: List of RoadmapNode objects (possibly from multiple roadmaps)

        Returns:
            Sorted list maintaining prerequisites and goal priorities
        """
        # Build node map
        node_map = {node.id: node for node in nodes}

        # Use existing topological sort as base
        sorted_nodes = self._topological_sort(nodes, node_map)

        # Within each topological level, sort by goal weight
        # Nodes without prerequisites go first, then nodes by goal priority
        def sort_key(node):
            # Primary sort: prerequisite depth (fewer prerequisites first)
            prereq_depth = len(node.prerequisites) if node.prerequisites else 0

            # Secondary sort: goal weight (higher weight = primary goal = first)
            goal_weight = getattr(node, 'goal_weight', 0.5)

            # Tertiary sort: original position (preserve flow)
            original_idx = nodes.index(node) if node in nodes else 999

            return (prereq_depth, -goal_weight, original_idx)

        # Stable sort within topological constraints
        # This preserves prerequisite order while prioritizing primary goal nodes
        final_sorted = sorted(sorted_nodes, key=sort_key)

        logger.debug(f"📊 Topological sort with priority: {len(final_sorted)} nodes ordered")

        return final_sorted

    def select_optimal_modules(
        self,
        roadmap: Roadmap,
        user_preferences: Dict,
        user_profile: Optional,  # UserContentProfile
        target_count: int
    ) -> List[RoadmapNode]:
        """
        PHASE 3: Select best N modules based on multi-factor priority scoring.

        Priority Scoring (100 points total):
        - Skill Gap Relevance (30 points): Teaches user's target_skills
        - Goal Alignment (25 points): Serves primary vs secondary goals
        - Career Stage Fit (20 points): Matches career needs (student/professional/career_change)
        - Difficulty Progression (15 points): Appropriate for user level + path position
        - Prerequisite Coverage (10 points): Fewer dependencies = easier to sequence

        Plus optional modifiers:
        - Struggle/Strength Areas (±10 points): Avoid difficult topics, boost strengths

        Args:
            roadmap: Roadmap with all available modules
            user_preferences: User's learning preferences
            user_profile: UserContentProfile with target_skills, struggle_areas, etc.
            target_count: Number of modules to select

        Returns:
            List of N highest-priority modules, topologically sorted
        """
        if len(roadmap.nodes) <= target_count:
            # Roadmap smaller than target - return all nodes
            logger.info(f"📊 Roadmap has {len(roadmap.nodes)} nodes ≤ target {target_count}, returning all")
            return roadmap.nodes

        logger.info(f"📊 Module prioritization: Selecting top {target_count} from {len(roadmap.nodes)} modules")

        scored_modules = []
        basic_info = user_preferences.get('basic_info', {})

        for idx, node in enumerate(roadmap.nodes):
            score = 0.0
            score_breakdown = {}

            # Factor 1: Skill Gap Relevance (30 points)
            # Does this module teach skills the user wants to learn?
            if user_profile and hasattr(user_profile, 'target_skills') and user_profile.target_skills:
                target_skills = set(s.lower().strip() for s in user_profile.target_skills if s)
                node_skills = set(s.lower().strip() for s in node.skills if s)

                # How many target skills does this module teach?
                target_overlap = len(node_skills & target_skills)
                skill_gap_score = min(target_overlap * 10.0, 30.0)  # Max 30 points
                score += skill_gap_score
                score_breakdown['skill_gap'] = skill_gap_score
            else:
                # No target skills specified - neutral score
                score += 15.0
                score_breakdown['skill_gap'] = 15.0

            # Factor 2: Goal Alignment (25 points)
            # Modules serving primary goal get full points, secondary get less
            if hasattr(node, 'goal_weight'):
                goal_score = node.goal_weight * 25.0  # 1.0 * 25 = 25, 0.7 * 25 = 17.5, etc.
                score += goal_score
                score_breakdown['goal_alignment'] = goal_score
            else:
                # Single goal - full points
                score += 25.0
                score_breakdown['goal_alignment'] = 25.0

            # Factor 3: Career Stage Fit (20 points)
            # Match module content to user's career needs
            career_stage = basic_info.get('career_stage', 'student')
            title_lower = node.title.lower()

            career_keywords = {
                'student': ['fundamentals', 'basics', 'introduction', 'getting started', 'beginner'],
                'career_change': ['project', 'portfolio', 'practical', 'build', 'create', 'hands-on'],
                'skill_upgrade': ['advanced', 'best practices', 'optimization', 'patterns', 'professional'],
                'professional': ['architecture', 'enterprise', 'scalability', 'production', 'advanced']
            }

            if any(kw in title_lower for kw in career_keywords.get(career_stage, [])):
                career_score = 20.0  # Perfect fit
            else:
                career_score = 8.0  # Neutral

            score += career_score
            score_breakdown['career_fit'] = career_score

            # Factor 4: Difficulty Progression Fit (15 points)
            # Early modules should match user level, later can be harder
            position_ratio = idx / max(len(roadmap.nodes), 1)
            experience_level = basic_info.get('experience_level', 'some_basics')

            difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            exp_map = {
                'complete_beginner': 1.0,
                'some_basics': 1.5,
                'intermediate': 2.0,
                'advanced': 3.0
            }

            node_difficulty = difficulty_map.get(node.difficulty, 2)
            # Target difficulty increases through path: start at user level, end slightly higher
            target_difficulty = exp_map.get(experience_level, 2.0) + (position_ratio * 0.5)

            difficulty_diff = abs(node_difficulty - target_difficulty)
            difficulty_score = max(0, 15.0 - (difficulty_diff * 5.0))  # Penalty for mismatch
            score += difficulty_score
            score_breakdown['difficulty_fit'] = difficulty_score

            # Factor 5: Prerequisite Coverage (10 points)
            # Modules with fewer prerequisites are easier to sequence
            prereq_count = len(node.prerequisites) if node.prerequisites else 0
            prereq_score = max(0, 10.0 - (prereq_count * 2.0))  # -2 points per prerequisite
            score += prereq_score
            score_breakdown['prereq_coverage'] = prereq_score

            # Factor 6: Struggle/Strength Areas (±10 points) - OPTIONAL
            struggle_penalty = 0.0
            strength_bonus = 0.0

            if user_profile and hasattr(user_profile, 'struggle_areas') and hasattr(user_profile, 'strength_areas'):
                struggle_areas = set(s.lower().strip() for s in (user_profile.struggle_areas or []) if s)
                strength_areas = set(s.lower().strip() for s in (user_profile.strength_areas or []) if s)

                # Penalty for struggle areas (deprioritize difficult topics)
                if any(area in title_lower for area in struggle_areas):
                    struggle_penalty = -10.0
                    logger.debug(f"⚠️ Struggle area detected in '{node.title}'")

                # Bonus for strength areas (build on what user knows)
                if any(area in title_lower for area in strength_areas):
                    strength_bonus = +5.0

            score += struggle_penalty + strength_bonus
            score_breakdown['struggle_strength'] = struggle_penalty + strength_bonus

            # Store scored module
            scored_modules.append((score, idx, node, score_breakdown))

        # Sort by score (descending), then by original position (preserve flow)
        scored_modules.sort(key=lambda x: (-x[0], x[1]))

        # BUG FIX: Filter duplicate titles (defense in depth - keep highest-scored instance)
        seen_titles = set()
        unique_scored = []

        for score, idx, node, breakdown in scored_modules:
            title_normalized = node.title.lower().strip()

            if title_normalized not in seen_titles:
                unique_scored.append((score, idx, node, breakdown))
                seen_titles.add(title_normalized)
            else:
                logger.debug(f"🚫 Skipping duplicate title '{node.title}' (lower score)")

        if len(scored_modules) > len(unique_scored):
            logger.info(f"🧹 Removed {len(scored_modules) - len(unique_scored)} duplicate titles from selection")

        # Select top N modules from deduplicated list
        selected_scored = unique_scored[:target_count]
        selected_nodes = [node for score, idx, node, breakdown in selected_scored]

        # Log top selections
        logger.info(f"📊 Module prioritization complete:")
        logger.info(f"   Selected {len(selected_nodes)}/{len(roadmap.nodes)} modules")
        if selected_scored:
            logger.info(f"   Top 3 scores: {[f'{score:.1f}' for score, _, _, _ in selected_scored[:3]]}")
            logger.info(f"   Top modules: {[node.title for _, _, node, _ in selected_scored[:3]]}")

        # Re-sort selected modules by topological order to maintain prerequisites
        node_map = {n.id: n for n in selected_nodes}
        ordered_selected = self._topological_sort(selected_nodes, node_map)

        return ordered_selected

    def filter_roadmap_by_experience(
        self,
        roadmap: Roadmap,
        experience_level: str
    ) -> Roadmap:
        """
        Filter roadmap nodes based on user's experience level.

        - Beginners: Include beginner and some intermediate topics
        - Intermediate: Include intermediate and some advanced topics
        - Advanced: Include all topics

        Args:
            roadmap: Original roadmap
            experience_level: User's experience level

        Returns:
            Filtered roadmap with appropriate difficulty nodes
        """
        if experience_level == 'complete_beginner':
            allowed_difficulties = {'beginner', 'intermediate'}
        elif experience_level in ['some_basics', 'intermediate']:
            allowed_difficulties = {'beginner', 'intermediate', 'advanced'}
        else:  # advanced
            # Include all nodes for advanced users
            return roadmap

        # Filter nodes by difficulty
        filtered_nodes = [
            node for node in roadmap.nodes
            if node.difficulty in allowed_difficulties
        ]

        # Update metadata
        filtered_roadmap = Roadmap(
            roadmap_id=roadmap.roadmap_id,
            title=roadmap.title,
            description=roadmap.description,
            category=roadmap.category,
            nodes=filtered_nodes,
            metadata={
                **roadmap.metadata,
                'filtered_by_experience': experience_level,
                'original_nodes': roadmap.metadata.get('total_nodes', len(roadmap.nodes)),
                'total_nodes': len(filtered_nodes)
            }
        )

        logger.info(f"🔍 Filtered roadmap from {len(roadmap.nodes)} to {len(filtered_nodes)} nodes for {experience_level} level")

        return filtered_roadmap

    def filter_roadmap_by_skills(
        self,
        roadmap: Roadmap,
        current_skills: List[str],
        similarity_threshold: float = 0.7
    ) -> Roadmap:
        """
        Filter roadmap to skip nodes the user already knows (skill gap analysis).

        Uses fuzzy title matching to compare user's current skills against roadmap node titles.
        Nodes with 70%+ similarity to user's skills are filtered out (already known).

        Args:
            roadmap: Original roadmap with all nodes
            current_skills: List of skills the user already has (e.g., ["Python", "HTML/CSS"])
            similarity_threshold: Minimum similarity ratio to consider a skill "known" (default 0.7)

        Returns:
            Filtered roadmap with nodes the user needs to learn (unknown skills only)
        """
        # If no current skills, return full roadmap (user is complete beginner)
        if not current_skills:
            logger.info("🔍 No current skills provided - returning full roadmap")
            return roadmap

        # Normalize user skills for comparison (lowercase, strip whitespace)
        normalized_user_skills = [skill.lower().strip() for skill in current_skills if skill]

        if not normalized_user_skills:
            return roadmap

        # Filter out nodes that user already knows
        filtered_nodes = []
        skipped_nodes = []

        for node in roadmap.nodes:
            # Normalize node title for comparison
            normalized_title = node.title.lower().strip()

            # Check if this node matches any of the user's current skills
            is_known = False
            for skill in normalized_user_skills:
                # Calculate simple similarity ratio (percentage of matching characters)
                # This is a lightweight alternative to fuzzywuzzy/difflib for exact word matching
                if skill in normalized_title or normalized_title in skill:
                    # Check character-level similarity
                    similarity = self._calculate_similarity(normalized_title, skill)

                    if similarity >= similarity_threshold:
                        is_known = True
                        skipped_nodes.append(node.title)
                        logger.debug(f"⏭️  Skipping known node: '{node.title}' (matches skill: '{skill}', similarity: {similarity:.2f})")
                        break

            # Keep node if it's NOT already known
            if not is_known:
                filtered_nodes.append(node)

        # Update metadata
        filtered_roadmap = Roadmap(
            roadmap_id=roadmap.roadmap_id,
            title=roadmap.title,
            description=roadmap.description,
            category=roadmap.category,
            nodes=filtered_nodes,
            metadata={
                **roadmap.metadata,
                'filtered_by_skills': True,
                'user_skills': current_skills,
                'original_nodes': len(roadmap.nodes),
                'skipped_nodes': len(skipped_nodes),
                'total_nodes': len(filtered_nodes)
            }
        )

        logger.info(f"🔍 Skill gap analysis: {len(roadmap.nodes)} nodes → {len(filtered_nodes)} nodes (skipped {len(skipped_nodes)} known topics)")
        if skipped_nodes:
            logger.info(f"   Skipped topics: {', '.join(skipped_nodes[:5])}{'...' if len(skipped_nodes) > 5 else ''}")

        return filtered_roadmap

    def add_prerequisite_nodes(
        self,
        roadmap: Roadmap,
        current_skills: List[str],
        filtered_roadmap: Roadmap
    ) -> Roadmap:
        """
        Add back prerequisite nodes for topics the user doesn't know.

        After filtering out known skills, we need to ensure all prerequisites
        for remaining nodes are included in the learning path.

        Example:
        - User knows: Python basics
        - Filtered roadmap includes: Advanced Python, Web Frameworks
        - This method adds back: Intermediate Python (prerequisite for Advanced Python)

        Args:
            roadmap: Original full roadmap
            current_skills: User's current skills
            filtered_roadmap: Roadmap after filtering by skills

        Returns:
            Roadmap with prerequisite nodes added back to fill skill gaps
        """
        # Build a set of node IDs in the filtered roadmap
        filtered_node_ids = {node.id for node in filtered_roadmap.nodes}

        # Build a map of all nodes from original roadmap
        all_nodes_map = {node.id: node for node in roadmap.nodes}

        # Find missing prerequisite nodes
        nodes_to_add = []
        checked_nodes = set()

        for node in filtered_roadmap.nodes:
            # Check each prerequisite
            for prereq_id in node.prerequisites:
                # If prerequisite is not in filtered roadmap and not already checked
                if prereq_id not in filtered_node_ids and prereq_id not in checked_nodes:
                    # Add the prerequisite node
                    if prereq_id in all_nodes_map:
                        prereq_node = all_nodes_map[prereq_id]
                        nodes_to_add.append(prereq_node)
                        filtered_node_ids.add(prereq_id)
                        checked_nodes.add(prereq_id)

                        logger.debug(f"➕ Adding prerequisite node: '{prereq_node.title}' (required for '{node.title}')")

        # Combine filtered nodes with prerequisite nodes
        all_nodes = list(filtered_roadmap.nodes) + nodes_to_add

        # Re-sort nodes using topological sort to maintain prerequisite ordering
        node_map = {node.id: node for node in all_nodes}
        sorted_nodes = self._topological_sort(all_nodes, node_map)

        # Update metadata
        enhanced_roadmap = Roadmap(
            roadmap_id=filtered_roadmap.roadmap_id,
            title=filtered_roadmap.title,
            description=filtered_roadmap.description,
            category=filtered_roadmap.category,
            nodes=sorted_nodes,
            metadata={
                **filtered_roadmap.metadata,
                'prerequisites_added': len(nodes_to_add),
                'total_nodes': len(sorted_nodes)
            }
        )

        if nodes_to_add:
            logger.info(f"➕ Added {len(nodes_to_add)} prerequisite nodes to fill skill gaps")
            logger.info(f"   Prerequisites: {', '.join([n.title for n in nodes_to_add[:3]])}{'...' if len(nodes_to_add) > 3 else ''}")

        return enhanced_roadmap

    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate simple string similarity ratio.

        Uses a lightweight character-based approach:
        - Exact substring match → 1.0
        - Partial word overlap → 0.5-0.9
        - No overlap → 0.0

        Args:
            str1: First string (normalized)
            str2: Second string (normalized)

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        # Exact match
        if str1 == str2:
            return 1.0

        # Full substring match
        if str1 in str2 or str2 in str1:
            return 0.85

        # Word-level matching (split by spaces and compare words)
        words1 = set(str1.split())
        words2 = set(str2.split())

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity (intersection over union)
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def generate_module_learning_outcomes(
        self,
        module_title: str,
        module_description: str = "",
        difficulty: str = "intermediate",
        lessons: List[Dict] = None
    ) -> List[str]:
        """
        Generate learning outcomes for a module using template-based approach.

        Phase 3 Enhancement: Adds "what you will learn" outcomes to each module.
        Uses pattern matching on module titles and difficulty levels.

        Future enhancement: Replace with LLM-based generation for better quality.

        Args:
            module_title: Title of the module
            module_description: Optional module description
            difficulty: Difficulty level (beginner, intermediate, advanced)
            lessons: Optional list of lessons in the module

        Returns:
            List of learning outcome strings (3-5 outcomes per module)

        Example:
            >>> service = RoadmapService()
            >>> outcomes = service.generate_module_learning_outcomes(
            ...     "Introduction to React Hooks",
            ...     difficulty="intermediate"
            ... )
            >>> print(outcomes)
            ['Understand React Hooks fundamentals', 'Use useState for state management', ...]
        """
        outcomes = []
        title_lower = module_title.lower()

        # Pattern-based outcome templates
        # Format: (keyword_pattern, [outcome_templates])
        outcome_patterns = {
            # Frontend patterns
            r'\breact\b': [
                f"Understand React {difficulty}-level concepts",
                "Build interactive user interfaces with React",
                "Manage component state and props effectively"
            ],
            r'\bhooks?\b': [
                "Master React Hooks (useState, useEffect, useContext)",
                "Create custom hooks for reusable logic",
                "Understand hook rules and best practices"
            ],
            r'\bjavascript\b|\bjs\b': [
                "Write clean and efficient JavaScript code",
                "Understand JavaScript core concepts and ES6+ features",
                "Apply JavaScript best practices in real projects"
            ],
            r'\btypescript\b': [
                "Add type safety to JavaScript applications",
                "Define interfaces and types for better code quality",
                "Understand TypeScript advanced features"
            ],
            r'\bcss\b|\ styling\b': [
                "Create responsive and modern UI designs",
                "Apply CSS best practices and methodologies",
                "Build mobile-first layouts"
            ],

            # Backend patterns
            r'\bnode\.?js\b': [
                "Build server-side applications with Node.js",
                "Understand asynchronous programming patterns",
                "Create RESTful APIs with Express or Fastify"
            ],
            r'\bapi\b|\ rest\b': [
                "Design and implement RESTful APIs",
                "Handle HTTP requests and responses",
                "Implement API authentication and authorization"
            ],
            r'\bdatabase\b|\ sql\b|\ nosql\b': [
                "Design efficient database schemas",
                "Write optimized queries",
                "Understand database normalization and indexing"
            ],
            r'\bdjango\b': [
                "Build web applications using Django framework",
                "Implement models, views, and templates",
                "Handle user authentication and permissions"
            ],

            # AI/ML patterns
            r'\bmachine learning\b|\ ml\b': [
                "Understand machine learning fundamentals",
                "Train and evaluate ML models",
                "Apply appropriate algorithms to real problems"
            ],
            r'\bdeep learning\b': [
                "Build neural networks from scratch",
                "Understand backpropagation and optimization",
                "Train deep learning models effectively"
            ],
            r'\bdata science\b': [
                "Perform exploratory data analysis",
                "Clean and preprocess datasets",
                "Visualize data insights effectively"
            ],

            # DevOps/Cloud patterns
            r'\bdocker\b': [
                "Containerize applications with Docker",
                "Write efficient Dockerfiles",
                "Manage multi-container applications with Docker Compose"
            ],
            r'\bkubernetes\b|\ k8s\b': [
                "Deploy applications to Kubernetes clusters",
                "Understand pods, services, and deployments",
                "Manage application scaling and updates"
            ],
            r'\bci/cd\b|\ pipeline\b': [
                "Set up automated CI/CD pipelines",
                "Implement continuous testing and deployment",
                "Optimize build and deployment processes"
            ],

            # Mobile patterns
            r'\bmobile\b|\ app\b': [
                "Build mobile applications from scratch",
                "Understand mobile UI/UX best practices",
                "Handle mobile-specific challenges (performance, offline, etc.)"
            ],

            # Security patterns
            r'\bsecurity\b|\ authentication\b': [
                "Implement secure authentication mechanisms",
                "Understand common security vulnerabilities",
                "Apply security best practices"
            ],

            # Testing patterns
            r'\btesting\b|\ test\b': [
                "Write effective unit and integration tests",
                "Apply test-driven development (TDD)",
                "Achieve high test coverage"
            ],
        }

        # Match patterns and add outcomes
        for pattern, pattern_outcomes in outcome_patterns.items():
            if re.search(pattern, title_lower):
                outcomes.extend(pattern_outcomes[:2])  # Take first 2 outcomes per pattern

        # Generic outcomes based on difficulty if no patterns matched
        if not outcomes:
            if difficulty == "beginner":
                outcomes = [
                    f"Understand {module_title} fundamentals",
                    "Apply basic concepts in practice",
                    "Build foundation for advanced topics"
                ]
            elif difficulty == "intermediate":
                outcomes = [
                    f"Master {module_title} core concepts",
                    "Build practical applications",
                    "Implement best practices and patterns"
                ]
            else:  # advanced
                outcomes = [
                    f"Achieve expert-level {module_title} proficiency",
                    "Solve complex real-world problems",
                    "Optimize performance and architecture"
                ]

        # Add lesson-specific outcomes if lessons provided
        if lessons:
            lesson_count = len(lessons)
            if lesson_count > 0:
                outcomes.append(f"Complete {lesson_count} hands-on lesson{'s' if lesson_count > 1 else ''}")

        # Limit to 3-5 outcomes (remove duplicates)
        outcomes = list(dict.fromkeys(outcomes))  # Remove duplicates while preserving order
        outcomes = outcomes[:5]  # Max 5 outcomes

        logger.debug(f"Generated {len(outcomes)} learning outcomes for '{module_title}'")
        return outcomes

    def clear_cache(self):
        """Clear the roadmap cache."""
        self._cache.clear()
        logger.info("🗑️ Roadmap cache cleared")

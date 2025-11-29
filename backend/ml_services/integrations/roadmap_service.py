"""
backend/ml_services/integrations/roadmap_service.py
Roadmap.sh integration service - fetches and parses structured learning roadmaps
Why: Provides curated learning paths from roadmap.sh instead of AI-generated content
RELEVANT FILES: learning_path_service.py, course_search_service.py, views.py
"""

import json
import logging
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
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

    def clear_cache(self):
        """Clear the roadmap cache."""
        self._cache.clear()
        logger.info("🗑️ Roadmap cache cleared")

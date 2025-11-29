# File: backend/ml_services/services/career_insights_service.py
# Description: Service for generating career insights for learning paths based on learning goals and skills
# Why: Enriches learning paths with career opportunities, salaries, job market data, and career progression
# Relevant Files: job_api_service.py, career_data.py, models.py, roadmap_service.py

"""
Career Insights Service

This service generates comprehensive career insights for learning paths by:
1. Mapping learning goals to career domains
2. Extracting skills from learning path modules
3. Fetching relevant career roles from static taxonomy
4. Enriching roles with real-time job market data (via Adzuna API)
5. Generating career progression paths
6. Calculating market demand scores

Used by GenerateLearningPathView to add career context to paths.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from apps.learning_content.career_data import (
    CAREER_DATA_TAXONOMY,
    get_domain_roles,
    get_career_progression,
    get_all_domains
)
from apps.learning_content.models import (
    CareerRole,
    CareerInsights,
    SkillOutcome,
    ProjectMilestone
)
from ml_services.integrations.job_api_service import get_job_api_service

logger = logging.getLogger(__name__)


class CareerInsightsService:
    """
    Service for generating career insights for learning paths.

    Features:
    - Maps learning goals to career domains using keyword matching
    - Extracts skills from module content
    - Generates career role recommendations
    - Enriches with real-time job market data
    - Creates career progression paths
    """

    def __init__(self):
        """Initialize CareerInsightsService with JobAPIService."""
        self.job_api = get_job_api_service()

    def map_learning_goals_to_career_domain(self, learning_goals: str) -> str:
        """
        Map user's learning goals to a career domain.

        Uses keyword matching to identify the best matching domain.
        Falls back to 'web_development' if no match found.

        Args:
            learning_goals: User's learning goals text

        Returns:
            Career domain key (e.g., 'web_development', 'ai_ml')

        Example:
            >>> service = CareerInsightsService()
            >>> domain = service.map_learning_goals_to_career_domain(
            ...     "I want to learn React and build web applications"
            ... )
            >>> print(domain)  # 'web_development'
        """
        goals_lower = learning_goals.lower()

        # Domain keyword mapping (most specific first)
        domain_keywords = {
            "ai_ml": [
                "machine learning", "deep learning", "artificial intelligence",
                "neural network", "tensorflow", "pytorch", "data science",
                "nlp", "computer vision", "llm", "transformers", "ai", "ml"
            ],
            "cybersecurity": [
                "cybersecurity", "security", "penetration testing", "ethical hacking",
                "pentesting", "vulnerability", "siem", "firewall", "infosec"
            ],
            "mobile_development": [
                "mobile", "ios", "android", "swift", "kotlin", "react native",
                "flutter", "mobile app", "app development"
            ],
            "devops": [
                "devops", "ci/cd", "jenkins", "kubernetes", "docker", "containerization",
                "pipeline", "deployment", "automation", "sre", "site reliability"
            ],
            "cloud_engineering": [
                "cloud", "aws", "azure", "gcp", "cloud computing", "terraform",
                "infrastructure", "cloudformation", "cloud architect"
            ],
            "data_engineering": [
                "data engineering", "etl", "data pipeline", "spark", "airflow",
                "data warehouse", "kafka", "big data", "analytics engineering"
            ],
            "web_development": [
                "web development", "frontend", "backend", "full stack", "react",
                "vue", "angular", "node.js", "django", "flask", "javascript",
                "typescript", "html", "css", "web app", "website"
            ],
        }

        # Score each domain based on keyword matches
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in goals_lower)
            domain_scores[domain] = score

        # Get domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        best_score = domain_scores[best_domain]

        if best_score > 0:
            logger.info(f"Mapped learning goals to domain '{best_domain}' (score: {best_score})")
            return best_domain
        else:
            logger.warning(f"No domain match found for goals. Defaulting to 'web_development'")
            return "web_development"

    def extract_skills_from_modules(self, modules: List[Dict[str, Any]]) -> List[SkillOutcome]:
        """
        Extract skills from learning path modules.

        Analyzes module titles and descriptions to identify skills.
        Currently uses pattern matching. Can be enhanced with NLP/LLM.

        Args:
            modules: List of module dictionaries from learning path

        Returns:
            List of SkillOutcome instances

        Example:
            >>> modules = [
            ...     {"title": "Introduction to React Hooks", "difficulty": "intermediate"},
            ...     {"title": "Building REST APIs with Node.js", "difficulty": "beginner"}
            ... ]
            >>> skills = service.extract_skills_from_modules(modules)
            >>> print(skills[0].skill_name)  # 'React'
        """
        skills = []
        skill_patterns = {
            # Frontend
            "React": r"\breact\b",
            "Vue": r"\bvue\b",
            "Angular": r"\bangular\b",
            "JavaScript": r"\bjavascript\b|\bjs\b",
            "TypeScript": r"\btypescript\b|\bts\b",
            "HTML/CSS": r"\bhtml\b|\bcss\b",
            "Tailwind CSS": r"\btailwind\b",
            "Responsive Design": r"\bresponsive\b",

            # Backend
            "Node.js": r"\bnode\.?js\b",
            "Express": r"\bexpress\b",
            "Django": r"\bdjango\b",
            "Flask": r"\bflask\b",
            "FastAPI": r"\bfastapi\b",
            "REST APIs": r"\brest\b|\bapi\b",
            "GraphQL": r"\bgraphql\b",

            # Databases
            "PostgreSQL": r"\bpostgresql\b|\bpostgres\b",
            "MongoDB": r"\bmongodb\b|\bmongo\b",
            "MySQL": r"\bmysql\b",
            "Redis": r"\bredis\b",

            # AI/ML
            "Python": r"\bpython\b",
            "Machine Learning": r"\bmachine learning\b|\bml\b",
            "TensorFlow": r"\btensorflow\b",
            "PyTorch": r"\bpytorch\b",
            "scikit-learn": r"\bscikit-learn\b|\bsklearn\b",
            "Deep Learning": r"\bdeep learning\b",
            "NLP": r"\bnlp\b|\bnatural language processing\b",

            # DevOps/Cloud
            "Docker": r"\bdocker\b",
            "Kubernetes": r"\bkubernetes\b|\bk8s\b",
            "AWS": r"\baws\b|\bamazon web services\b",
            "CI/CD": r"\bci/cd\b|\bjenkins\b|\bgithub actions\b",
            "Terraform": r"\bterraform\b",

            # Mobile
            "React Native": r"\breact native\b",
            "Swift": r"\bswift\b",
            "Kotlin": r"\bkotlin\b",
            "Flutter": r"\bflutter\b",

            # Other
            "Git": r"\bgit\b",
            "Testing": r"\btesting\b|\btest\b|\bjest\b|\bpytest\b",
            "Agile": r"\bagile\b|\bscrum\b",
        }

        skill_categories = {
            "React": "frontend",
            "Vue": "frontend",
            "Angular": "frontend",
            "JavaScript": "frontend",
            "TypeScript": "frontend",
            "HTML/CSS": "frontend",
            "Tailwind CSS": "frontend",
            "Responsive Design": "frontend",
            "Node.js": "backend",
            "Express": "backend",
            "Django": "backend",
            "Flask": "backend",
            "FastAPI": "backend",
            "REST APIs": "backend",
            "GraphQL": "backend",
            "PostgreSQL": "database",
            "MongoDB": "database",
            "MySQL": "database",
            "Redis": "database",
            "Python": "programming",
            "Machine Learning": "ai_ml",
            "TensorFlow": "ai_ml",
            "PyTorch": "ai_ml",
            "scikit-learn": "ai_ml",
            "Deep Learning": "ai_ml",
            "NLP": "ai_ml",
            "Docker": "devops",
            "Kubernetes": "devops",
            "AWS": "cloud",
            "CI/CD": "devops",
            "Terraform": "devops",
            "React Native": "mobile",
            "Swift": "mobile",
            "Kotlin": "mobile",
            "Flutter": "mobile",
            "Git": "tools",
            "Testing": "testing",
            "Agile": "methodology",
        }

        found_skills = set()

        for module in modules:
            module_text = f"{module.get('title', '')} {module.get('description', '')}".lower()
            difficulty = module.get('difficulty', 'beginner')

            # Match skill patterns
            for skill_name, pattern in skill_patterns.items():
                if re.search(pattern, module_text, re.IGNORECASE):
                    if skill_name not in found_skills:
                        found_skills.add(skill_name)

                        # Determine proficiency based on difficulty
                        if difficulty == 'beginner':
                            proficiency = 'beginner'
                            importance = 60
                        elif difficulty == 'intermediate':
                            proficiency = 'intermediate'
                            importance = 75
                        else:  # advanced
                            proficiency = 'advanced'
                            importance = 90

                        skills.append(SkillOutcome(
                            skill_name=skill_name,
                            skill_category=skill_categories.get(skill_name, "general"),
                            proficiency_level=proficiency,
                            importance_score=importance
                        ))

        logger.info(f"Extracted {len(skills)} skills from {len(modules)} modules")
        return skills

    def generate_project_milestones(
        self,
        modules: List[Dict[str, Any]],
        domain: str
    ) -> List[ProjectMilestone]:
        """
        Generate hands-on project milestones for learning path.

        Places projects at strategic points (25%, 50%, 75%, 100%) in the path.
        Projects are domain-specific and difficulty-appropriate.

        Args:
            modules: List of module dictionaries
            domain: Career domain key

        Returns:
            List of ProjectMilestone instances

        Example:
            >>> modules = [{"title": "Module 1"}, {"title": "Module 2"}, ...]  # 8 modules
            >>> milestones = service.generate_project_milestones(modules, "web_development")
            >>> print(len(milestones))  # 3-4 projects
        """
        if not modules:
            return []

        total_modules = len(modules)
        milestones = []

        # Project templates by domain
        project_templates = {
            "web_development": [
                {
                    "percentage": 0.25,
                    "title": "Build a Portfolio Website",
                    "description": "Create a responsive personal portfolio using HTML, CSS, and JavaScript",
                    "hours": 8,
                    "skills": ["HTML/CSS", "JavaScript", "Responsive Design"]
                },
                {
                    "percentage": 0.50,
                    "title": "Full Stack Todo App",
                    "description": "Build a complete todo application with frontend, backend, and database",
                    "hours": 12,
                    "skills": ["React", "Node.js", "MongoDB", "REST APIs"]
                },
                {
                    "percentage": 0.75,
                    "title": "E-commerce Platform",
                    "description": "Develop an e-commerce site with authentication, cart, and payments",
                    "hours": 20,
                    "skills": ["Full Stack", "Authentication", "Payment Integration"]
                },
            ],
            "ai_ml": [
                {
                    "percentage": 0.33,
                    "title": "Data Analysis Project",
                    "description": "Analyze a real-world dataset using pandas and visualize insights",
                    "hours": 10,
                    "skills": ["Python", "Pandas", "Data Visualization"]
                },
                {
                    "percentage": 0.66,
                    "title": "Machine Learning Classification",
                    "description": "Build a classification model for a real dataset (e.g., iris, titanic)",
                    "hours": 15,
                    "skills": ["scikit-learn", "Machine Learning", "Model Evaluation"]
                },
                {
                    "percentage": 1.0,
                    "title": "Deep Learning Image Classifier",
                    "description": "Train a CNN to classify images using TensorFlow or PyTorch",
                    "hours": 20,
                    "skills": ["Deep Learning", "TensorFlow/PyTorch", "CNNs"]
                },
            ],
            "mobile_development": [
                {
                    "percentage": 0.33,
                    "title": "Simple Mobile App UI",
                    "description": "Build a multi-screen mobile app with navigation",
                    "hours": 10,
                    "skills": ["React Native/Flutter", "Mobile UI", "Navigation"]
                },
                {
                    "percentage": 0.66,
                    "title": "Weather App with API",
                    "description": "Create a weather app that fetches data from an external API",
                    "hours": 12,
                    "skills": ["API Integration", "State Management"]
                },
                {
                    "percentage": 1.0,
                    "title": "Social Media Clone",
                    "description": "Build a social media app with posts, likes, and user profiles",
                    "hours": 25,
                    "skills": ["Full Stack Mobile", "Backend Integration", "Authentication"]
                },
            ],
            "devops": [
                {
                    "percentage": 0.4,
                    "title": "CI/CD Pipeline Setup",
                    "description": "Configure a complete CI/CD pipeline for a web application",
                    "hours": 10,
                    "skills": ["CI/CD", "Jenkins/GitHub Actions", "Testing"]
                },
                {
                    "percentage": 0.8,
                    "title": "Kubernetes Deployment",
                    "description": "Deploy a microservices app to Kubernetes cluster",
                    "hours": 15,
                    "skills": ["Kubernetes", "Docker", "Microservices"]
                },
            ],
        }

        # Get templates for domain (default to web_development)
        templates = project_templates.get(domain, project_templates["web_development"])

        # Generate milestones based on module count
        for template in templates:
            module_index = int(total_modules * template["percentage"]) - 1
            if module_index < 0:
                module_index = 0
            if module_index >= total_modules:
                module_index = total_modules - 1

            milestone_id = f"milestone_{template['title'].lower().replace(' ', '_')}"

            milestones.append(ProjectMilestone(
                milestone_id=milestone_id,
                title=template["title"],
                description=template["description"],
                estimated_hours=template["hours"],
                skills_practiced=template["skills"],
                appears_after_module=module_index
            ))

        logger.info(f"Generated {len(milestones)} project milestones for {domain}")
        return milestones

    def generate_career_insights(
        self,
        learning_goals: str,
        modules: List[Dict[str, Any]],
        user_location: str = ""
    ) -> CareerInsights:
        """
        Generate comprehensive career insights for a learning path.

        This is the main method that orchestrates:
        1. Domain mapping
        2. Role selection from taxonomy
        3. Job count enrichment via API
        4. Career progression generation
        5. Market demand calculation

        Args:
            learning_goals: User's learning goals text
            modules: List of module dictionaries
            user_location: Optional user location for job market data

        Returns:
            CareerInsights instance with all career data

        Example:
            >>> service = CareerInsightsService()
            >>> insights = service.generate_career_insights(
            ...     learning_goals="I want to become a React developer",
            ...     modules=[...],
            ...     user_location="San Francisco"
            ... )
            >>> print(len(insights.career_roles))  # e.g., 4 roles
            >>> print(insights.market_demand_score)  # e.g., 85
        """
        logger.info(f"Generating career insights for goals: '{learning_goals[:50]}...'")

        # Step 1: Map learning goals to career domain
        domain = self.map_learning_goals_to_career_domain(learning_goals)

        # Step 2: Get career roles from static taxonomy
        domain_data = CAREER_DATA_TAXONOMY.get(domain, {})
        static_roles = domain_data.get("roles", [])

        if not static_roles:
            logger.warning(f"No roles found for domain '{domain}'. Using default.")
            static_roles = CAREER_DATA_TAXONOMY["web_development"]["roles"]

        # Step 3: Enrich roles with real-time job counts
        enriched_roles_data = self.job_api.enrich_career_roles_with_job_counts(
            static_roles,
            location=user_location
        )

        # Step 4: Convert to CareerRole instances
        career_roles = []
        total_job_openings = 0

        for role_data in enriched_roles_data:
            career_role = CareerRole(
                role_title=role_data.get("role_title", ""),
                role_description=role_data.get("role_description", ""),
                salary_entry_min=role_data.get("salary_entry_min", 0),
                salary_entry_max=role_data.get("salary_entry_max", 0),
                salary_mid_min=role_data.get("salary_mid_min", 0),
                salary_mid_max=role_data.get("salary_mid_max", 0),
                salary_senior_min=role_data.get("salary_senior_min", 0),
                salary_senior_max=role_data.get("salary_senior_max", 0),
                required_skills=role_data.get("required_skills", []),
                experience_level=role_data.get("experience_level", "entry"),
                job_openings_count=role_data.get("job_openings_count", 0),
                market_demand=role_data.get("market_demand", "medium"),
                next_roles=role_data.get("next_roles", [])
            )
            career_roles.append(career_role)
            total_job_openings += career_role.job_openings_count

        # Step 5: Get career progression path
        career_progression = get_career_progression(domain)

        # Step 6: Calculate market demand score
        market_demand_score = self.job_api.calculate_market_demand_score(total_job_openings)

        # Step 7: Create CareerInsights instance
        insights = CareerInsights(
            career_roles=career_roles,
            market_demand_score=market_demand_score,
            total_job_openings=total_job_openings,
            career_progression=career_progression,
            last_updated=datetime.utcnow()
        )

        logger.info(
            f"Generated career insights: {len(career_roles)} roles, "
            f"{total_job_openings} total jobs, "
            f"demand score: {market_demand_score}"
        )

        return insights


# Singleton instance
_career_insights_service = None


def get_career_insights_service() -> CareerInsightsService:
    """
    Get singleton CareerInsightsService instance.

    Returns:
        CareerInsightsService instance
    """
    global _career_insights_service
    if _career_insights_service is None:
        _career_insights_service = CareerInsightsService()
    return _career_insights_service

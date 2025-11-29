# File: backend/core/apps/learning_content/career_data.py
# Description: Static career data taxonomy mapping learning domains to job roles, salaries, and skills
# Why: Provides baseline career insights without API calls, enriched with real-time job counts later
# Relevant Files: models.py, career_insights_service.py, job_api_service.py

"""
Static Career Data Taxonomy

This module contains comprehensive career data for different learning domains.
Data includes:
- Job roles and titles
- Salary ranges (entry/mid/senior levels in USD)
- Required skills with importance scores (0-100)
- Market demand indicators
- Career progression paths

Sources:
- Glassdoor salary data (2024)
- LinkedIn job postings analysis
- Bureau of Labor Statistics (BLS)
- Industry surveys from Stack Overflow, DICE

Updates:
- Salary data should be updated annually
- Skills taxonomy updated quarterly based on job market trends
- Market demand indicators updated monthly via Adzuna API
"""

# Career Data Taxonomy by Learning Domain
CAREER_DATA_TAXONOMY = {
    "web_development": {
        "domain_name": "Web Development",
        "roles": [
            {
                "role_title": "Frontend Developer",
                "role_description": "Build responsive user interfaces and web applications using modern frameworks",
                "salary_entry_min": 60000,
                "salary_entry_max": 85000,
                "salary_mid_min": 85000,
                "salary_mid_max": 120000,
                "salary_senior_min": 120000,
                "salary_senior_max": 175000,
                "required_skills": [
                    {"skill": "HTML/CSS", "importance": 95},
                    {"skill": "JavaScript", "importance": 100},
                    {"skill": "React", "importance": 90},
                    {"skill": "TypeScript", "importance": 80},
                    {"skill": "Responsive Design", "importance": 85},
                    {"skill": "Git", "importance": 75},
                    {"skill": "REST APIs", "importance": 70},
                    {"skill": "Testing (Jest/Vitest)", "importance": 65},
                ],
                "experience_level": "entry",
                "market_demand": "very_high",
                "next_roles": ["Senior Frontend Developer", "Full Stack Developer", "Frontend Architect"]
            },
            {
                "role_title": "Full Stack Developer",
                "role_description": "Develop complete web applications handling both frontend and backend systems",
                "salary_entry_min": 75000,
                "salary_entry_max": 100000,
                "salary_mid_min": 100000,
                "salary_mid_max": 140000,
                "salary_senior_min": 140000,
                "salary_senior_max": 200000,
                "required_skills": [
                    {"skill": "JavaScript", "importance": 100},
                    {"skill": "React/Vue/Angular", "importance": 90},
                    {"skill": "Node.js", "importance": 90},
                    {"skill": "Express/Fastify", "importance": 80},
                    {"skill": "PostgreSQL/MongoDB", "importance": 85},
                    {"skill": "REST APIs", "importance": 90},
                    {"skill": "Git", "importance": 80},
                    {"skill": "Docker", "importance": 70},
                    {"skill": "CI/CD", "importance": 65},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior Full Stack Developer", "Tech Lead", "Solutions Architect"]
            },
            {
                "role_title": "Backend Developer",
                "role_description": "Design and implement server-side logic, databases, and APIs",
                "salary_entry_min": 70000,
                "salary_entry_max": 95000,
                "salary_mid_min": 95000,
                "salary_mid_max": 135000,
                "salary_senior_min": 135000,
                "salary_senior_max": 190000,
                "required_skills": [
                    {"skill": "Python/Java/Node.js", "importance": 100},
                    {"skill": "REST APIs", "importance": 95},
                    {"skill": "SQL Databases", "importance": 90},
                    {"skill": "NoSQL Databases", "importance": 80},
                    {"skill": "Git", "importance": 80},
                    {"skill": "API Design", "importance": 85},
                    {"skill": "Microservices", "importance": 75},
                    {"skill": "Docker", "importance": 70},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior Backend Developer", "Backend Architect", "DevOps Engineer"]
            },
            {
                "role_title": "React Developer",
                "role_description": "Specialize in building modern web applications using React ecosystem",
                "salary_entry_min": 65000,
                "salary_entry_max": 90000,
                "salary_mid_min": 90000,
                "salary_mid_max": 130000,
                "salary_senior_min": 130000,
                "salary_senior_max": 180000,
                "required_skills": [
                    {"skill": "React", "importance": 100},
                    {"skill": "JavaScript/TypeScript", "importance": 100},
                    {"skill": "Redux/Context API", "importance": 85},
                    {"skill": "React Hooks", "importance": 95},
                    {"skill": "Next.js", "importance": 80},
                    {"skill": "CSS-in-JS", "importance": 70},
                    {"skill": "Testing (Jest/RTL)", "importance": 75},
                    {"skill": "Git", "importance": 75},
                ],
                "experience_level": "entry",
                "market_demand": "very_high",
                "next_roles": ["Senior React Developer", "Frontend Architect", "Full Stack Developer"]
            },
        ],
        "career_progression": [
            "Frontend Developer",
            "Senior Frontend Developer",
            "Full Stack Developer",
            "Tech Lead",
            "Engineering Manager"
        ]
    },

    "ai_ml": {
        "domain_name": "Artificial Intelligence & Machine Learning",
        "roles": [
            {
                "role_title": "Machine Learning Engineer",
                "role_description": "Design, build, and deploy machine learning models and ML systems",
                "salary_entry_min": 90000,
                "salary_entry_max": 120000,
                "salary_mid_min": 120000,
                "salary_mid_max": 160000,
                "salary_senior_min": 160000,
                "salary_senior_max": 220000,
                "required_skills": [
                    {"skill": "Python", "importance": 100},
                    {"skill": "Machine Learning", "importance": 100},
                    {"skill": "TensorFlow/PyTorch", "importance": 95},
                    {"skill": "SQL", "importance": 80},
                    {"skill": "Data Preprocessing", "importance": 85},
                    {"skill": "Git", "importance": 75},
                    {"skill": "MLOps", "importance": 70},
                    {"skill": "Cloud Platforms", "importance": 75},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior ML Engineer", "ML Architect", "AI Research Scientist"]
            },
            {
                "role_title": "Data Scientist",
                "role_description": "Analyze complex data, build predictive models, and extract actionable insights",
                "salary_entry_min": 85000,
                "salary_entry_max": 110000,
                "salary_mid_min": 110000,
                "salary_mid_max": 150000,
                "salary_senior_min": 150000,
                "salary_senior_max": 210000,
                "required_skills": [
                    {"skill": "Python/R", "importance": 100},
                    {"skill": "Statistics", "importance": 95},
                    {"skill": "SQL", "importance": 90},
                    {"skill": "Machine Learning", "importance": 90},
                    {"skill": "Data Visualization", "importance": 85},
                    {"skill": "Pandas/NumPy", "importance": 90},
                    {"skill": "scikit-learn", "importance": 85},
                    {"skill": "Jupyter Notebooks", "importance": 80},
                ],
                "experience_level": "entry",
                "market_demand": "very_high",
                "next_roles": ["Senior Data Scientist", "ML Engineer", "Data Science Manager"]
            },
            {
                "role_title": "AI Engineer",
                "role_description": "Develop AI-powered applications and integrate AI models into production systems",
                "salary_entry_min": 95000,
                "salary_entry_max": 125000,
                "salary_mid_min": 125000,
                "salary_mid_max": 170000,
                "salary_senior_min": 170000,
                "salary_senior_max": 240000,
                "required_skills": [
                    {"skill": "Python", "importance": 100},
                    {"skill": "Deep Learning", "importance": 95},
                    {"skill": "TensorFlow/PyTorch", "importance": 95},
                    {"skill": "NLP/Computer Vision", "importance": 85},
                    {"skill": "LLMs/Transformers", "importance": 90},
                    {"skill": "MLOps", "importance": 80},
                    {"skill": "Cloud AI Services", "importance": 80},
                    {"skill": "Docker/Kubernetes", "importance": 75},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior AI Engineer", "AI Architect", "AI Research Lead"]
            },
            {
                "role_title": "Deep Learning Engineer",
                "role_description": "Build neural network architectures and train deep learning models",
                "salary_entry_min": 100000,
                "salary_entry_max": 130000,
                "salary_mid_min": 130000,
                "salary_mid_max": 180000,
                "salary_senior_min": 180000,
                "salary_senior_max": 250000,
                "required_skills": [
                    {"skill": "Python", "importance": 100},
                    {"skill": "PyTorch/TensorFlow", "importance": 100},
                    {"skill": "Neural Networks", "importance": 100},
                    {"skill": "CNNs/RNNs/Transformers", "importance": 95},
                    {"skill": "GPU Computing (CUDA)", "importance": 80},
                    {"skill": "Model Optimization", "importance": 85},
                    {"skill": "Research Papers", "importance": 75},
                    {"skill": "Linear Algebra", "importance": 80},
                ],
                "experience_level": "mid",
                "market_demand": "high",
                "next_roles": ["Senior DL Engineer", "AI Research Scientist", "ML Architect"]
            },
        ],
        "career_progression": [
            "Data Scientist",
            "Machine Learning Engineer",
            "Senior ML Engineer",
            "AI Architect",
            "Head of AI/ML"
        ]
    },

    "mobile_development": {
        "domain_name": "Mobile Development",
        "roles": [
            {
                "role_title": "iOS Developer",
                "role_description": "Build native iOS applications using Swift and iOS frameworks",
                "salary_entry_min": 70000,
                "salary_entry_max": 95000,
                "salary_mid_min": 95000,
                "salary_mid_max": 135000,
                "salary_senior_min": 135000,
                "salary_senior_max": 185000,
                "required_skills": [
                    {"skill": "Swift", "importance": 100},
                    {"skill": "UIKit/SwiftUI", "importance": 95},
                    {"skill": "Xcode", "importance": 95},
                    {"skill": "iOS SDK", "importance": 90},
                    {"skill": "REST APIs", "importance": 85},
                    {"skill": "Core Data", "importance": 75},
                    {"skill": "Git", "importance": 75},
                    {"skill": "App Store Guidelines", "importance": 70},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior iOS Developer", "Mobile Architect", "Lead iOS Engineer"]
            },
            {
                "role_title": "Android Developer",
                "role_description": "Develop native Android applications using Kotlin and Android SDK",
                "salary_entry_min": 68000,
                "salary_entry_max": 92000,
                "salary_mid_min": 92000,
                "salary_mid_max": 130000,
                "salary_senior_min": 130000,
                "salary_senior_max": 180000,
                "required_skills": [
                    {"skill": "Kotlin/Java", "importance": 100},
                    {"skill": "Android SDK", "importance": 95},
                    {"skill": "Android Studio", "importance": 90},
                    {"skill": "Jetpack Compose", "importance": 85},
                    {"skill": "REST APIs", "importance": 85},
                    {"skill": "Room Database", "importance": 75},
                    {"skill": "Git", "importance": 75},
                    {"skill": "Material Design", "importance": 70},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior Android Developer", "Mobile Architect", "Lead Android Engineer"]
            },
            {
                "role_title": "React Native Developer",
                "role_description": "Build cross-platform mobile apps using React Native framework",
                "salary_entry_min": 65000,
                "salary_entry_max": 90000,
                "salary_mid_min": 90000,
                "salary_mid_max": 125000,
                "salary_senior_min": 125000,
                "salary_senior_max": 170000,
                "required_skills": [
                    {"skill": "React Native", "importance": 100},
                    {"skill": "JavaScript/TypeScript", "importance": 100},
                    {"skill": "React", "importance": 90},
                    {"skill": "Mobile UI/UX", "importance": 85},
                    {"skill": "REST APIs", "importance": 85},
                    {"skill": "Native Modules", "importance": 75},
                    {"skill": "Git", "importance": 75},
                    {"skill": "App Deployment", "importance": 70},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior React Native Dev", "Mobile Architect", "Full Stack Mobile Dev"]
            },
        ],
        "career_progression": [
            "Mobile Developer",
            "Senior Mobile Developer",
            "Mobile Architect",
            "Lead Mobile Engineer",
            "VP of Mobile Engineering"
        ]
    },

    "cloud_engineering": {
        "domain_name": "Cloud Engineering & Architecture",
        "roles": [
            {
                "role_title": "Cloud Engineer",
                "role_description": "Design, deploy, and manage cloud infrastructure on AWS/Azure/GCP",
                "salary_entry_min": 75000,
                "salary_entry_max": 100000,
                "salary_mid_min": 100000,
                "salary_mid_max": 140000,
                "salary_senior_min": 140000,
                "salary_senior_max": 195000,
                "required_skills": [
                    {"skill": "AWS/Azure/GCP", "importance": 100},
                    {"skill": "Infrastructure as Code", "importance": 90},
                    {"skill": "Terraform/CloudFormation", "importance": 85},
                    {"skill": "Docker", "importance": 85},
                    {"skill": "Kubernetes", "importance": 80},
                    {"skill": "Linux", "importance": 85},
                    {"skill": "CI/CD", "importance": 80},
                    {"skill": "Networking", "importance": 75},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior Cloud Engineer", "Cloud Architect", "DevOps Lead"]
            },
            {
                "role_title": "Solutions Architect",
                "role_description": "Design enterprise cloud solutions and technical architecture",
                "salary_entry_min": 95000,
                "salary_entry_max": 125000,
                "salary_mid_min": 125000,
                "salary_mid_max": 170000,
                "salary_senior_min": 170000,
                "salary_senior_max": 230000,
                "required_skills": [
                    {"skill": "Cloud Platforms", "importance": 100},
                    {"skill": "System Design", "importance": 95},
                    {"skill": "Architecture Patterns", "importance": 90},
                    {"skill": "Microservices", "importance": 85},
                    {"skill": "Security", "importance": 85},
                    {"skill": "Cost Optimization", "importance": 80},
                    {"skill": "Networking", "importance": 85},
                    {"skill": "Client Communication", "importance": 75},
                ],
                "experience_level": "senior",
                "market_demand": "high",
                "next_roles": ["Principal Architect", "Enterprise Architect", "CTO"]
            },
        ],
        "career_progression": [
            "Cloud Engineer",
            "Senior Cloud Engineer",
            "Cloud Architect",
            "Solutions Architect",
            "Principal Architect"
        ]
    },

    "devops": {
        "domain_name": "DevOps & Site Reliability Engineering",
        "roles": [
            {
                "role_title": "DevOps Engineer",
                "role_description": "Automate deployment pipelines and manage infrastructure",
                "salary_entry_min": 70000,
                "salary_entry_max": 95000,
                "salary_mid_min": 95000,
                "salary_mid_max": 135000,
                "salary_senior_min": 135000,
                "salary_senior_max": 190000,
                "required_skills": [
                    {"skill": "CI/CD", "importance": 100},
                    {"skill": "Docker", "importance": 95},
                    {"skill": "Kubernetes", "importance": 90},
                    {"skill": "Jenkins/GitLab CI", "importance": 85},
                    {"skill": "Linux", "importance": 90},
                    {"skill": "Scripting (Bash/Python)", "importance": 85},
                    {"skill": "Infrastructure as Code", "importance": 85},
                    {"skill": "Monitoring", "importance": 80},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior DevOps Engineer", "SRE", "DevOps Architect"]
            },
            {
                "role_title": "Site Reliability Engineer (SRE)",
                "role_description": "Ensure system reliability, performance, and scalability",
                "salary_entry_min": 90000,
                "salary_entry_max": 115000,
                "salary_mid_min": 115000,
                "salary_mid_max": 155000,
                "salary_senior_min": 155000,
                "salary_senior_max": 210000,
                "required_skills": [
                    {"skill": "System Reliability", "importance": 100},
                    {"skill": "Monitoring & Alerting", "importance": 95},
                    {"skill": "Kubernetes", "importance": 90},
                    {"skill": "Python/Go", "importance": 85},
                    {"skill": "Incident Response", "importance": 90},
                    {"skill": "Performance Tuning", "importance": 85},
                    {"skill": "Cloud Platforms", "importance": 85},
                    {"skill": "SLO/SLI/SLA", "importance": 80},
                ],
                "experience_level": "mid",
                "market_demand": "high",
                "next_roles": ["Senior SRE", "SRE Lead", "Infrastructure Architect"]
            },
        ],
        "career_progression": [
            "DevOps Engineer",
            "Senior DevOps Engineer",
            "Site Reliability Engineer",
            "SRE Lead",
            "VP of Infrastructure"
        ]
    },

    "cybersecurity": {
        "domain_name": "Cybersecurity & Information Security",
        "roles": [
            {
                "role_title": "Security Engineer",
                "role_description": "Protect systems and networks from security threats and vulnerabilities",
                "salary_entry_min": 75000,
                "salary_entry_max": 100000,
                "salary_mid_min": 100000,
                "salary_mid_max": 140000,
                "salary_senior_min": 140000,
                "salary_senior_max": 195000,
                "required_skills": [
                    {"skill": "Network Security", "importance": 95},
                    {"skill": "Penetration Testing", "importance": 90},
                    {"skill": "SIEM Tools", "importance": 85},
                    {"skill": "Firewalls/IDS/IPS", "importance": 85},
                    {"skill": "Security Frameworks", "importance": 80},
                    {"skill": "Scripting (Python)", "importance": 80},
                    {"skill": "Incident Response", "importance": 85},
                    {"skill": "Vulnerability Assessment", "importance": 85},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior Security Engineer", "Security Architect", "CISO"]
            },
            {
                "role_title": "Penetration Tester",
                "role_description": "Test systems for vulnerabilities through ethical hacking",
                "salary_entry_min": 70000,
                "salary_entry_max": 95000,
                "salary_mid_min": 95000,
                "salary_mid_max": 130000,
                "salary_senior_min": 130000,
                "salary_senior_max": 180000,
                "required_skills": [
                    {"skill": "Penetration Testing", "importance": 100},
                    {"skill": "Kali Linux", "importance": 90},
                    {"skill": "Metasploit", "importance": 85},
                    {"skill": "Web Application Security", "importance": 90},
                    {"skill": "Network Protocols", "importance": 85},
                    {"skill": "Scripting", "importance": 80},
                    {"skill": "Report Writing", "importance": 75},
                    {"skill": "OWASP Top 10", "importance": 90},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior Pentester", "Security Consultant", "Red Team Lead"]
            },
        ],
        "career_progression": [
            "Security Analyst",
            "Security Engineer",
            "Senior Security Engineer",
            "Security Architect",
            "CISO"
        ]
    },

    "data_engineering": {
        "domain_name": "Data Engineering & Analytics",
        "roles": [
            {
                "role_title": "Data Engineer",
                "role_description": "Build and maintain data pipelines and infrastructure",
                "salary_entry_min": 80000,
                "salary_entry_max": 105000,
                "salary_mid_min": 105000,
                "salary_mid_max": 145000,
                "salary_senior_min": 145000,
                "salary_senior_max": 200000,
                "required_skills": [
                    {"skill": "Python/SQL", "importance": 100},
                    {"skill": "ETL Pipelines", "importance": 95},
                    {"skill": "Apache Spark", "importance": 85},
                    {"skill": "Data Warehousing", "importance": 85},
                    {"skill": "Airflow/Kafka", "importance": 80},
                    {"skill": "Cloud Data Services", "importance": 85},
                    {"skill": "Data Modeling", "importance": 80},
                    {"skill": "Docker", "importance": 70},
                ],
                "experience_level": "mid",
                "market_demand": "very_high",
                "next_roles": ["Senior Data Engineer", "Data Architect", "ML Engineer"]
            },
            {
                "role_title": "Analytics Engineer",
                "role_description": "Transform raw data into actionable insights and dashboards",
                "salary_entry_min": 75000,
                "salary_entry_max": 100000,
                "salary_mid_min": 100000,
                "salary_mid_max": 135000,
                "salary_senior_min": 135000,
                "salary_senior_max": 185000,
                "required_skills": [
                    {"skill": "SQL", "importance": 100},
                    {"skill": "dbt", "importance": 90},
                    {"skill": "Python/R", "importance": 85},
                    {"skill": "Data Visualization", "importance": 90},
                    {"skill": "Tableau/PowerBI", "importance": 85},
                    {"skill": "Data Modeling", "importance": 85},
                    {"skill": "Cloud Data Warehouses", "importance": 80},
                    {"skill": "Git", "importance": 70},
                ],
                "experience_level": "entry",
                "market_demand": "high",
                "next_roles": ["Senior Analytics Engineer", "Data Scientist", "Data Lead"]
            },
        ],
        "career_progression": [
            "Data Analyst",
            "Analytics Engineer",
            "Data Engineer",
            "Senior Data Engineer",
            "Head of Data"
        ]
    },
}


# Helper function to get all roles for a domain
def get_domain_roles(domain_key: str) -> list:
    """
    Get all career roles for a specific domain.

    Args:
        domain_key: Domain key (e.g., 'web_development', 'ai_ml')

    Returns:
        List of role dictionaries
    """
    return CAREER_DATA_TAXONOMY.get(domain_key, {}).get("roles", [])


# Helper function to get career progression for a domain
def get_career_progression(domain_key: str) -> list:
    """
    Get career progression path for a domain.

    Args:
        domain_key: Domain key (e.g., 'web_development', 'ai_ml')

    Returns:
        List of role titles in progression order
    """
    return CAREER_DATA_TAXONOMY.get(domain_key, {}).get("career_progression", [])


# Helper function to get all domains
def get_all_domains() -> list:
    """
    Get list of all available career domains.

    Returns:
        List of domain keys
    """
    return list(CAREER_DATA_TAXONOMY.keys())

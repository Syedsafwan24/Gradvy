# Gradvy - Technology Stack Overview & Project Modules

> **Comprehensive Documentation for Presentation and Reporting**
> Last Updated: 2025-11-29

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Frontend Technology Stack](#frontend-technology-stack)
4. [Backend Technology Stack](#backend-technology-stack)
5. [AI/ML Models & Algorithms](#aiml-models--algorithms)
6. [External Integrations & APIs](#external-integrations--apis)
7. [Storage & Media Solutions](#storage--media-solutions)
8. [Project Modules](#project-modules)
9. [Development Tools & Infrastructure](#development-tools--infrastructure)

---

## Project Overview

**Gradvy** is an AI-powered personalized learning platform that provides adaptive learning experiences through intelligent content recommendations, personalized learning paths, and comprehensive user data analytics.

### Core Mission
Transform education through AI-driven personalization, adaptive learning paths, and intelligent content curation.

### Key Differentiators
- **Hybrid AI Approach**: Combines curated roadmap.sh content with GPT-powered dynamic generation
- **0-100 Knowledge Scoring**: Replaces static difficulty levels with continuous scoring
- **Real-time Course Search**: YouTube + Udemy API integration with intelligent ranking
- **Privacy-First**: GDPR-compliant data collection with granular consent management
- **Multi-factor Authentication**: Enterprise-grade security with TOTP + backup codes

---

## Architecture

### System Architecture Pattern
**Hybrid Development Setup** - Data services in Docker, application runs locally

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (Browser)                    │
│            Next.js 15 + React 18 + TailwindCSS              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                   Backend Layer (Django)                     │
│        Django 5.1.3 + DRF + JWT + Celery Worker             │
└─┬─────────┬──────────┬──────────┬────────────┬─────────────┘
  │         │          │          │            │
  │         │          │          │            │
┌─▼───────┐ │  ┌───────▼────┐  ┌─▼──────┐  ┌──▼──────────┐
│PostgreSQL│ │  │  MongoDB   │  │ Redis  │  │  ML APIs    │
│   15     │ │  │    7.0     │  │   7    │  │ (Groq/GPT)  │
└──────────┘ │  └────────────┘  └────────┘  └─────────────┘
             │
      ┌──────▼─────────┐
      │ External APIs   │
      │ (YouTube/Udemy) │
      └────────────────┘
```

### Technology Choices Rationale

| Component | Technology | Why? |
|-----------|-----------|------|
| Frontend | Next.js 15 | Server-side rendering, App Router, React Server Components |
| Backend | Django 5.1 | Robust ORM, admin panel, security features, mature ecosystem |
| Auth | JWT + TOTP | Stateless authentication with enterprise-grade MFA |
| Task Queue | Celery + Redis | Async processing for analytics, email, data pipelines |
| AI | Groq API | Fast inference (10x faster than OpenAI), cost-effective |
| Caching | Redis 7 | Session management, Celery broker, query caching |

---

## Frontend Technology Stack

### Core Framework
```json
{
  "framework": "Next.js 15.0.0",
  "runtime": "React 18.3.1",
  "typescript": "5.6.2",
  "build": "Turbopack (--turbo flag)"
}
```

### UI/UX Libraries

#### Component Libraries
- **Radix UI** - Unstyled, accessible component primitives
  - `@radix-ui/react-dialog` - Modal dialogs
  - `@radix-ui/react-dropdown-menu` - Dropdown menus
  - `@radix-ui/react-tabs` - Tab components
  - `@radix-ui/react-slider` - Range sliders
  - `@radix-ui/react-switch` - Toggle switches
  - `@radix-ui/react-tooltip` - Accessible tooltips
  - `@radix-ui/react-progress` - Progress bars
  - `@radix-ui/react-accordion` - Accordion components

#### Styling & Animations
- **TailwindCSS 3.4.10** - Utility-first CSS framework
- **Framer Motion 11.5.4** - Production-ready animations
- **tailwindcss-animate** - Pre-built animation utilities
- **class-variance-authority** - Type-safe component variants
- **clsx + tailwind-merge** - Conditional className utilities
- **Lucide React 0.446.0** - 1000+ beautiful icons

#### Code Editor
- **Monaco Editor 0.53.0** - VSCode-powered editor
- **@monaco-editor/react 4.7.0** - React integration
- Features: Syntax highlighting, IntelliSense, multi-language support

### State Management
- **Redux Toolkit 2.9.0** - Predictable state container
- **React Redux 9.2.0** - Official React bindings
- **Redux Persist 6.0.0** - Persist state across sessions
- **RTK Query** - Powerful data fetching and caching

### Forms & Validation
- **React Hook Form 7.53.0** - Performant form library
- **Yup 1.7.0** - Schema validation
- **Zod 4.1.13** - TypeScript-first validation
- **@hookform/resolvers 5.2.1** - Validation resolver

### Data Visualization
- **Recharts 3.2.0** - Composable charting library
- Features: Line charts, bar charts, pie charts, area charts

### HTTP Client
- **Axios 1.7.7** - Promise-based HTTP client
- **js-cookie 3.0.5** - Cookie handling
- **react-hot-toast 2.6.0** - Toast notifications

### Development Tools
- **ESLint 8.57.1** - Code linting
- **PostCSS 8.4.45** - CSS transformations
- **Autoprefixer 10.4.20** - Vendor prefix automation

---

## Backend Technology Stack

### Core Framework
```python
{
  "framework": "Django 5.1.3",
  "rest_api": "Django REST Framework 3.15.2",
  "python_version": "3.10+"
}
```

### API & Authentication

#### REST API
- **Django REST Framework 3.15.2** - Powerful REST API toolkit
- **djangorestframework-simplejwt 5.3.0** - JWT authentication
- **PyJWT 2.10.1** - JSON Web Token implementation

#### Security & Authentication
- **django-axes 6.4.0** - Brute-force attack protection
- **django-two-factor-auth 1.16.0** - Two-factor authentication
- **django-otp 1.5.4** - One-time password framework
- **argon2-cffi 25.1.0** - Password hashing (Argon2)
- **qrcode 7.4.2** - QR code generation for TOTP

#### CORS & Security
- **django-cors-headers 4.4.0** - Cross-Origin Resource Sharing
- **requests-oauthlib 1.3.1** - OAuth authentication

### Database & ORM

#### SQL Database
- **PostgreSQL 15 (Alpine)** - Primary relational database
- **psycopg 3.2.9** - PostgreSQL adapter
- **dj-database-url 2.1.0** - Database URL parsing

#### NoSQL Database
- **MongoDB 7.0** - User preferences & analytics
- **mongoengine 0.27.0** - MongoDB ODM
- **pymongo 4.6.0** - MongoDB driver

### Task Queue & Background Processing
- **Celery 5.3.6** - Distributed task queue
- **Redis 5.0.3** - Message broker & cache
- **Flower 2.0.1** - Celery monitoring UI
- **billiard 4.2.1** - Multiprocessing pool
- **kombu 5.5.4** - Messaging library
- **eventlet 0.36.1** - Concurrent networking

### Machine Learning & Data Processing

#### ML Libraries
- **numpy 1.24+** - Numerical computing
- **scipy 1.10+** - Scientific computing
- **scikit-learn 1.3+** - Machine learning algorithms
- **pandas 2.0+** - Data manipulation

#### Deep Learning (Optional)
- **torch 2.0+** - PyTorch deep learning framework
- **torchvision 0.15+** - Computer vision models
- **torchaudio 2.0+** - Audio processing

#### HuggingFace Ecosystem (Local Models)
- **transformers 4.30+** - Pre-trained models (CodeLlama, Mistral)
- **sentence-transformers 2.2.2** - Semantic embeddings
- **huggingface_hub 0.15.1** - Model hub integration
- **tokenizers 0.13.3** - Fast tokenization
- **accelerate 0.20+** - Model optimization

#### Model Optimization
- **bitsandbytes 0.39+** - 4-bit/8-bit quantization
- **optimum 1.8+** - Model optimization tools

#### External ML APIs
- **openai 1.0+** - OpenAI/Groq/Together AI compatible client

### Utilities

#### Phone & User Agent
- **django-phonenumber-field 7.3.0** - Phone validation
- **phonenumbers 8.13.47** - Phone number parsing
- **user-agents 2.2+** - User agent parsing

#### Date & Time
- **python-dateutil 2.9+** - Date utilities
- **pytz 2025.2** - Timezone support
- **tzdata 2025.2** - Timezone database

#### System & Monitoring
- **psutil 5.9+** - System monitoring
- **prometheus_client 0.22.1** - Metrics collection

#### Configuration
- **python-decouple 3.8** - Settings management
- **python-dotenv 1.0.1** - .env file support

---

## AI/ML Models & Algorithms

### Model Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   ML Services Layer                         │
├─────────────────────┬───────────────────────────────────────┤
│  API-Based Models   │         Local Models (Optional)       │
├─────────────────────┼───────────────────────────────────────┤
│ Groq/OpenAI/Together│  Mistral-7B-Instruct                 │
│ LLaMA 3 70B (Groq) │  CodeLlama (13B)                      │
│ GPT-4/3.5 (OpenAI)  │  all-MiniLM-L6-v2 (Embeddings)       │
└─────────────────────┴───────────────────────────────────────┘
```

### 1. AI-Powered Learning Path Generation

#### Primary Service: `AIGoalAnalyzer`
**Location**: `backend/ml_services/services/ai_goal_analyzer.py`

**Algorithm**: Hybrid AI + Curated Content
```python
def analyze_learning_goal(goal, user_background, preferences):
    # Step 1: Try roadmap.sh (curated expert content)
    roadmap = fetch_roadmap_sh(goal)

    # Step 2: Evaluate quality (5+ nodes, 0.3+ quality score)
    if is_high_quality(roadmap):
        return enhance_with_ai(roadmap)

    # Step 3: Fallback to pure AI generation
    return generate_with_ai(goal, user_background, preferences)
```

**Key Features**:
- **Semantic Matching**: Maps 30+ goal variations to roadmap.sh roadmaps
- **Dynamic Module Count**: 5-20 modules based on complexity
- **0-100 Difficulty Scale**: Continuous difficulty (not discrete levels)
- **Prerequisite Analysis**: Identifies module dependencies
- **Quality Scoring**: Evaluates roadmap completeness (30% title, 20% description, etc.)

**AI Model Used**: Groq LLaMA 3 70B (8192 context window)
- **Why Groq?**: 10x faster inference than OpenAI, cost-effective
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 3000 for comprehensive learning paths

#### Example AI Prompt Structure:
```
Generate a personalized learning roadmap for: [GOAL]

USER CONTEXT:
- Experience level: [intermediate]
- Time availability: [3-5hrs/week]
- Learning styles: [hands_on, visual]
- Background skills: [JavaScript, HTML]

REQUIREMENTS:
1. Generate 5-20 modules (complexity-based)
2. Each module: ID, title, objectives, difficulty (0-100), hours, prerequisites
3. Gradual difficulty progression
4. JSON format output
```

### 2. Knowledge Assessment System

#### Service: `KnowledgeAssessor`
**Location**: `backend/ml_services/services/knowledge_assessor.py`

**Algorithm**: Multi-Factor Scoring with Time Decay
```python
def assess_knowledge(user, topic):
    # Weighted scoring
    score = (
        completed_courses * 0.40 +  # 40% - Completion
        quiz_results * 0.30 +        # 30% - Assessment
        related_skills * 0.20 +      # 20% - Transferable knowledge
        self_reported * 0.10         # 10% - User input
    )

    # Apply exponential time decay
    decay = 0.5 ^ (days_inactive / 180)  # Half-life: 6 months
    final_score = score * max(decay, 0.5)  # Never below 50%

    return (final_score, confidence_score)
```

**Scoring Breakdown**:
| Factor | Weight | Rationale |
|--------|--------|-----------|
| Completed Courses | 40% | Shows commitment and effort |
| Quiz/Assessment Scores | 30% | Proves actual understanding |
| Related Skills | 20% | Transferable knowledge (JS → React) |
| Self-Reported Level | 10% | Least reliable indicator |

**Time Decay Model**:
- **Half-life**: 180 days (knowledge decays 50% after 6 months)
- **Minimum Retention**: 50% (knowledge never fully forgotten)
- **Formula**: `score * (0.5 ^ (days_inactive / 180))`

### 3. Course Search & Ranking

#### Service: `CourseSearchService`
**Location**: `backend/ml_services/integrations/course_search_service.py`

**Algorithm**: Intelligent Multi-Platform Ranking
```python
def rank_courses(courses, user_preferences):
    for course in courses:
        score = (
            platform_match * 0.25 +        # 25% - Platform preference
            rating_quality * 0.20 +        # 20% - Course rating
            difficulty_match * 0.20 +      # 20% - Difficulty alignment
            duration_preference * 0.15 +   # 15% - Duration fit
            content_type_match * 0.10 +    # 10% - Learning style
            language_preference * 0.05 +   # 5% - Language
            instructor_rating * 0.05       # 5% - Instructor quality
        )

    return sorted(courses, key=lambda c: c.score, reverse=True)
```

**Query Enrichment** (4 Layers):
1. **Learning Goal Context**: "Introduction" → "Introduction to Mobile Development"
2. **Difficulty Keywords**: "beginner tutorial", "advanced"
3. **Learning Style Keywords**: "project", "course", "tutorial"
4. **Duration Hints**: "quick", "complete"

**Example**:
```
Input: "Introduction" (mobile_dev, beginner, hands_on)
Output: "Introduction to Mobile Development beginner tutorial project"
```

### 4. Semantic Roadmap Matching

**Algorithm**: Keyword-Based Semantic Search
```python
def get_semantic_mapping(goal):
    # Map 30+ variations to roadmap.sh names
    semantic_map = {
        'mobile': 'react-native',
        'mobile_dev': 'react-native',
        'app development': 'react-native',
        'web': 'frontend',
        'ai': 'ai-data-scientist',
        # ... 30+ mappings
    }

    # Try exact match
    if goal in semantic_map:
        return semantic_map[goal]

    # Try partial match (contains keyword)
    for keyword, roadmap_name in semantic_map.items():
        if keyword in goal or goal in keyword:
            return roadmap_name

    return None  # Fall back to AI
```

### 5. Text Generation Models

#### API-Based Model: `APITextGenerationModel`
**Location**: `backend/ml_services/models/api_text_generation_model.py`

**Supported Providers**:
- **Groq** (Primary): LLaMA 3 70B, Mixtral 8x7B
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Together AI**: Various open-source models

**Features**:
- OpenAI-compatible API interface
- Token usage tracking (cost monitoring)
- Request/response logging with truncation
- Configurable temperature, max_length, top_p

#### Local Models (Optional - Heavy)
```python
# Requires 16GB+ RAM, 100GB+ disk, GPU recommended
models = {
    'mistral-7b-instruct': {
        'size': '7B parameters',
        'use_case': 'General text generation',
        'quantization': '4-bit (bitsandbytes)'
    },
    'all-minilm-l6-v2': {
        'size': '22M parameters',
        'use_case': 'Semantic embeddings',
        'speed': 'Fast (sentence-transformers)'
    }
}
```

### 6. Embedding Models

**Model**: `all-MiniLM-L6-v2` (sentence-transformers)
**Use Cases**:
- Semantic course matching
- Content similarity analysis
- User skill clustering

**Specs**:
- **Parameters**: 22 million
- **Embedding Dimension**: 384
- **Performance**: 14,200 sentences/sec on CPU

---

## External Integrations & APIs

### 1. AI/ML APIs

#### Groq API (Primary)
**Location**: `backend/ml_services/models/api_text_generation_model.py`

```python
{
  "provider": "Groq",
  "base_url": "https://api.groq.com/openai/v1",
  "models": ["llama3-70b-8192", "mixtral-8x7b-32768"],
  "use_case": "Learning path generation, goal analysis",
  "advantages": "10x faster than OpenAI, cost-effective"
}
```

**Configuration** (settings.py:23-27):
```python
ML_API_PROVIDER = 'groq'  # 'openai', 'groq', 'together', 'mock'
ML_API_KEY = env('ML_API_KEY')
ML_API_BASE_URL = 'https://api.groq.com/openai/v1'
ML_API_MODEL = 'llama3-70b-8192'
```

**Logging**: All API calls logged with:
- Request/response data (truncated)
- Token usage (cost monitoring)
- Sanitized auth (API keys hidden)
- API-specific quota tracking

### 2. Course Content APIs

#### YouTube Data API v3
**Location**: `backend/ml_services/integrations/course_search_service.py:279-485`

**Endpoints Used**:
1. **Video Search** (`/search?type=video`)
   - Quota Cost: 100 units per search
   - Features: High-definition filter, relevance ranking

2. **Playlist Search** (`/search?type=playlist`)
   - Quota Cost: 100 units per search
   - Use Case: Structured course sequences

3. **Video Details** (`/videos`)
   - Quota Cost: 1 unit per video
   - Data: Duration (ISO 8601), views, likes, comments

4. **Playlist Details** (`/playlists`)
   - Quota Cost: 1 unit per playlist
   - Data: Video count, estimated duration

**Daily Quota**: 10,000 units/day (free tier)

**Smart Features**:
- **Engagement-Based Rating**: Calculates 0-5 rating from likes, comments, views
  ```python
  rating = 2.5 + ((like_ratio * 0.5) + (comment_engagement * 0.3) +
                  (view_popularity * 0.2)) * 2.5
  ```
- **Content Structure Preference**: Respects user's videos/playlists preference
- **Playlist Detection**: Marks playlists with 📚 emoji

**Configuration** (settings.py:29):
```python
YOUTUBE_API_KEY = env('YOUTUBE_API_KEY', default='')
```

#### Udemy Affiliate API
**Location**: `backend/ml_services/integrations/course_search_service.py:702-783`

**Endpoints**:
1. **Course Search** (`/api-2.0/courses/`)
   - Auth: Basic Auth (client_id + secret)
   - Parameters: search, page_size, ordering, price
   - Returns: Title, price, rating, reviews, instructor

**Affiliate Tracking**:
```python
def generate_affiliate_link(course_url):
    return f"{base_url}?referralCode={UDEMY_AFFILIATE_ID}"
```

**Configuration** (settings.py:30-33):
```python
UDEMY_CLIENT_ID = env('UDEMY_CLIENT_ID', default='')
UDEMY_CLIENT_SECRET = env('UDEMY_CLIENT_SECRET', default='')
UDEMY_AFFILIATE_ID = env('UDEMY_AFFILIATE_ID', default='')
```

**Smart Fallback**:
- **Mock Courses**: If APIs unavailable, generates preview data
- **Quality Indicators**: Clear labeling ("🎓 PREVIEW: ...")
- **Configuration Flags**:
  ```python
  USE_MOCK_COURSES = True  # Development mode
  REQUIRE_REAL_COURSES = False  # Fail if no APIs
  ```

### 3. Roadmap.sh Integration

#### Roadmap.sh GitHub API
**Location**: `backend/ml_services/integrations/roadmap_service.py:91-142`

**Data Source**: GitHub Raw Content
```
https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/
master/src/data/roadmaps/{roadmap_name}/{roadmap_name}.json
```

**Supported Roadmaps**:
| Learning Goal | Roadmap File | Nodes |
|--------------|--------------|-------|
| web_dev | frontend | 50+ |
| mobile_dev | react-native | 40+ |
| ai_ml | ai-data-scientist | 60+ |
| devops | devops | 55+ |
| blockchain | blockchain | 35+ |
| game_dev | game-developer | 45+ |

**Features**:
- **Topological Sort**: Orders nodes by prerequisites (Kahn's algorithm)
- **Quality Filtering**: Removes UI nodes (vertical, paragraph, legend)
- **Node Validation**: Requires title, description, skills
- **Caching**: In-memory cache for performance

**Algorithm** (Topological Sort):
```python
def topological_sort(nodes):
    # Build adjacency list and in-degree count
    for node in nodes:
        for prereq in node.prerequisites:
            adj_list[prereq].append(node)
            in_degree[node] += 1

    # BFS with queue
    queue = [n for n in nodes if in_degree[n] == 0]
    sorted_nodes = []

    while queue:
        node = queue.pop(0)
        sorted_nodes.append(node)

        for dependent in adj_list[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    return sorted_nodes
```

### 4. Social OAuth Providers

#### Google OAuth
**Location**: `backend/core/apps/auth/social_services.py:103-198`

**APIs Used**:
1. **Google People API** (`/v1/people/me`)
   - Fields: names, emails, photos, biographies, organizations, skills
   - Consent: OAuth 2.0 (user approval required)

**Data Collected** (with consent):
- Profile: Name, email, avatar, bio
- Location: City, country, address
- Work: Company, job title, work history
- Skills: Interests, declared skills

#### GitHub OAuth
**Location**: `backend/core/apps/auth/social_services.py:200-293`

**APIs Used**:
1. **User Info** (`/user`)
2. **Repositories** (`/user/repos`)
3. **Organizations** (`/user/orgs`)

**Enrichment**:
- **Programming Languages**: Extracted from repo languages
- **Project Complexity**: Stars, forks, repo size
- **Technical Interests**: Repo topics

#### LinkedIn OAuth
**Location**: `backend/core/apps/auth/social_services.py:296-422`

**APIs Used**:
1. **Profile** (`/v2/people/~`)
   - Fields: firstName, lastName, headline, positions, educations
2. **Email** (`/v2/emailAddress`)

**Data Points**:
- Professional: Current job, work history, industry
- Education: Schools, degrees, fields of study
- Network: Connections, endorsements

**Privacy**:
- All OAuth calls logged with sanitized auth tokens
- User consent required for each data type
- Granular permission settings
- GDPR-compliant data export

---

## Storage & Media Solutions

### 1. PostgreSQL 15 (Primary Database)

**Container**: `gradvy-postgres` (Alpine)

**Purpose**:
- User authentication (User model, sessions)
- Authorization (permissions, groups)
- Relational data (Foreign keys, joins)

**Schema Examples**:
```sql
-- User Model (core/apps/auth/)
CREATE TABLE gradvy_auth_user (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Social Auth Provider
CREATE TABLE social_provider (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    client_id VARCHAR(255),
    client_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Social Account
CREATE TABLE social_account (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES gradvy_auth_user(id),
    provider_id BIGINT REFERENCES social_provider(id),
    access_token TEXT,
    refresh_token TEXT,
    profile_data JSONB
);
```

**Configuration** (docker-compose.yml:2-28):
```yaml
gradvy-postgres:
  image: postgres:15-alpine
  ports: ['5434:5432']
  volumes: [gradvy_postgres:/var/lib/postgresql/data]
  environment:
    POSTGRES_DB: gradvy_db
    POSTGRES_USER: gradvy_user
    POSTGRES_PASSWORD: gradvy_secure_2024
```

**Health Check**:
```bash
pg_isready -U gradvy_user -d gradvy_db
```

### 2. MongoDB 7.0 (User Preferences & Analytics)

**Container**: `gradvy-mongodb`

**Purpose**:
- User preferences (flexible schema)
- Behavioral analytics (time-series data)
- Privacy settings (granular consent)
- Social data (nested documents)

**Collections** (mongoengine models):

#### UserPreference
```python
{
  "user_id": 123,
  "basic_info": {
    "learning_goals": ["web_dev", "ai_ml"],
    "experience_level": "intermediate",
    "learning_style": ["hands_on", "visual"],
    "current_skills": ["JavaScript", "Python"],
    "time_availability": "3-5hrs",
    "preferred_pace": "medium"
  },
  "content_preferences": {
    "preferred_platforms": ["youtube", "udemy"],
    "duration_preference": "mixed",
    "content_structure": "playlists_preferred",
    "language_preference": ["english"],
    "instructor_ratings_min": 4.0
  },
  "behavioral_patterns": {
    "active_days": ["Monday", "Wednesday", "Friday"],
    "peak_learning_hours": [18, 19, 20],
    "avg_session_duration": 45,
    "preferred_content_types": ["video", "interactive"]
  },
  "privacy_settings": {
    "analytics_consent": true,
    "personalization_consent": true,
    "data_export_request": null
  }
}
```

#### SocialData
```python
{
  "user_id": 123,
  "google_profile": {
    "email": "user@gmail.com",
    "name": "John Doe",
    "skills": ["Python", "Machine Learning"],
    "organizations": ["Tech Corp"]
  },
  "github_profile": {
    "username": "johndoe",
    "programming_languages": ["Python", "JavaScript", "Go"],
    "total_stars": 523,
    "public_repos": 42
  },
  "linkedin_profile": {
    "current_company": "Tech Corp",
    "current_title": "Senior Developer",
    "work_history": [...]
  }
}
```

**Configuration** (docker-compose.yml:53-79):
```yaml
gradvy-mongodb:
  image: mongo:7.0
  ports: ['27017:27017']
  volumes:
    - gradvy_mongodb:/data/db
    - gradvy_mongodb_config:/data/configdb
  environment:
    MONGO_INITDB_ROOT_USERNAME: gradvy_admin
    MONGO_INITDB_ROOT_PASSWORD: gradvy_mongo_secure_2024
```

**Connection** (settings.py:284-302):
```python
MONGODB_URI = 'mongodb://gradvy_app:gradvy_app_secure_2024@localhost:27017/gradvy_preferences'
mongoengine.connect(**MONGODB_SETTINGS)
```

### 3. Redis 7 (Cache & Message Broker)

**Container**: `gradvy-redis`

**Use Cases**:

#### 1. Celery Message Broker
```python
# Task queue for background processing
CELERY_BROKER_URL = 'redis://localhost:6380/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6380/0'
```

#### 2. Session Cache
```python
# Django session storage (optional)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

#### 3. API Response Cache
```python
# Course search cache (in-memory)
cache_key = f"courses:{topic}:{max_results}"
if cache_key in self._cache:
    return cached_courses
```

#### 4. Rate Limiting
```python
# DRF throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/min',
        'user': '120/min'
    }
}
```

**Configuration** (docker-compose.yml:30-51):
```yaml
gradvy-redis:
  image: redis:7-alpine
  ports: ['6380:6379']
  command: redis-server --appendonly yes --maxmemory 256mb
  volumes: [gradvy_redis:/data]
```

**Memory Policy**: `allkeys-lru` (Least Recently Used eviction)

### 4. Static Files & Media

**Static Files** (CSS, JS, Images):
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**Media Files** (User uploads):
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Production Storage** (Future):
- **AWS S3**: User avatars, course thumbnails
- **CloudFront CDN**: Static assets delivery
- **ImageKit**: Image optimization & transformation

### 5. Logging & Monitoring

**File-Based Logging** (settings.py:370-439):
```python
LOGGING = {
    'handlers': {
        'api_file': {
            'filename': 'logs/api_requests.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'external_api_file': {
            'filename': 'logs/external_apis.log',
            'maxBytes': 10485760,
            'backupCount': 10
        }
    },
    'loggers': {
        'external_api': {
            'handlers': ['console', 'external_api_file'],
            'level': 'DEBUG'
        }
    }
}
```

**External API Logging** (all third-party calls):
```
[2025-11-29 14:23:45] DEBUG [EXTERNAL API] Groq LLM API
Request: POST https://api.groq.com/openai/v1/chat/completions
Tokens: 1523 prompt, 847 completion
Response: 200 OK (truncated)
```

---

## Project Modules

### 1. Authentication & User Management

**Location**: `backend/core/apps/auth/` + `frontend/src/app/(auth)/`

**Features**:
- Email/password registration with email verification
- JWT-based authentication (24h access, 30d refresh)
- Multi-factor authentication (TOTP + backup codes)
- Social OAuth (Google, GitHub, LinkedIn)
- Password reset flow
- Session fingerprinting (device tracking)
- Brute-force protection (django-axes)

**Frontend Pages**:
- `/login` - Login with email/password
- `/register` - User registration
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset confirmation
- `/settings/security` - MFA setup, session management

**Backend APIs**:
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
POST /api/auth/logout/
POST /api/auth/mfa/setup/
POST /api/auth/mfa/verify/
POST /api/auth/social/connect/
```

**Security Measures**:
- Argon2 password hashing
- CSRF token validation
- CORS configuration
- Rate limiting (20 req/min anonymous, 120 req/min authenticated)
- Session expiration (7 days)
- Secure cookie flags (HttpOnly, Secure, SameSite)

### 2. Onboarding & Preferences

**Location**: `backend/core/apps/preferences/` + `frontend/src/app/app/onboarding/`

**Purpose**: Comprehensive user data collection for personalization

**Onboarding Flow** (4 Steps):

#### Step 1: Basic Info
```json
{
  "learning_goals": ["web_dev", "ai_ml"],
  "experience_level": "intermediate",
  "learning_style": ["hands_on", "visual"],
  "time_availability": "3-5hrs",
  "preferred_pace": "medium"
}
```

#### Step 2: Content Preferences
```json
{
  "preferred_platforms": ["youtube", "udemy", "coursera"],
  "duration_preference": "mixed",
  "content_structure": "playlists_preferred",
  "language_preference": ["english"],
  "instructor_ratings_min": 4.0
}
```

#### Step 3: Skills & Goals
```json
{
  "current_skills": ["JavaScript", "Python", "React"],
  "target_skills": ["Machine Learning", "Django"],
  "career_stage": "professional",
  "learning_timeline": "6months"
}
```

#### Step 4: Social Integration (Optional)
- Connect Google (work/education data)
- Connect GitHub (programming languages, projects)
- Connect LinkedIn (professional background)

**APIs**:
```
POST /api/preferences/onboarding/
GET /api/preferences/
PATCH /api/preferences/
POST /api/preferences/social/connect/{provider}/
```

**Privacy Controls**:
- Granular consent per data type
- Data export (GDPR)
- Data deletion request
- Opt-out analytics

### 3. Learning Paths (AI-Powered)

**Location**: `backend/core/apps/learning_content/` + `frontend/src/app/app/learning-paths/`

**Features**:
- AI-generated personalized roadmaps
- Hybrid approach (roadmap.sh + Groq AI)
- Dynamic module count (5-20 based on complexity)
- 0-100 difficulty progression
- Real-time course search (YouTube + Udemy)

**User Journey**:

#### 3.1 Generate Learning Path
```
Frontend: /app/learning-paths/generate
Backend: POST /api/learning-paths/generate/
```

**Request**:
```json
{
  "learning_goal": "mobile app development",
  "user_preferences": {
    "experience_level": "some_basics",
    "time_availability": "3-5hrs",
    "learning_styles": ["hands_on", "videos"]
  }
}
```

**Response** (AI-Generated):
```json
{
  "path_id": "ai_mobile_1732890234",
  "title": "Mobile App Development Learning Path",
  "description": "Comprehensive path from basics to deployment",
  "modules": [
    {
      "id": "module_1",
      "title": "Introduction to Mobile Development",
      "description": "Fundamentals of mobile platforms",
      "learning_objectives": [
        "Understand iOS vs Android",
        "Learn mobile development approaches",
        "Set up development environment"
      ],
      "difficulty_score": 20,
      "estimated_hours": 8,
      "prerequisites": [],
      "skills_to_master": ["Mobile basics", "Environment setup"],
      "courses": [
        {
          "title": "📚 Mobile Development for Beginners",
          "platform": "youtube",
          "url": "https://youtube.com/playlist?list=...",
          "rating": 4.6,
          "duration_hours": 3.5,
          "relevance_score": 87.5
        }
      ]
    },
    {
      "id": "module_2",
      "title": "React Native Fundamentals",
      "difficulty_score": 35,
      "estimated_hours": 15,
      "prerequisites": ["module_1"]
      // ... more modules
    }
  ],
  "total_estimated_hours": 120,
  "difficulty_progression": [20, 35, 45, 58, 67, 75, 82, 88],
  "metadata": {
    "generation_method": "pure_ai",
    "ai_model": "llama3-70b-8192",
    "processing_time_ms": 3421
  }
}
```

#### 3.2 View Learning Path
```
Frontend: /app/learning-paths/[pathId]
Backend: GET /api/learning-paths/{id}/
```

**UI Features**:
- Module cards with progress tracking
- Course recommendations per module
- Difficulty progression visualization
- Estimated completion timeline

#### 3.3 Track Progress
```
Backend: POST /api/learning-paths/{id}/progress/
```

**Progress Tracking**:
```json
{
  "module_id": "module_2",
  "status": "in_progress",
  "courses_completed": 2,
  "time_spent_hours": 12,
  "quiz_scores": {
    "quiz_1": 85,
    "quiz_2": 92
  }
}
```

**APIs**:
```
POST /api/learning-paths/generate/
GET /api/learning-paths/
GET /api/learning-paths/{id}/
POST /api/learning-paths/{id}/progress/
DELETE /api/learning-paths/{id}/
```

### 4. Code Playground (Interactive)

**Location**: `frontend/src/app/app/playground/`

**Features**:
- Multi-language code editor (Monaco Editor)
- Syntax highlighting & IntelliSense
- Code execution (browser-based)
- Template library (50+ starter templates)
- Code sharing & saving

**Supported Languages**:
- JavaScript / TypeScript
- Python
- HTML/CSS
- React (JSX)
- C / C++
- Java
- Go

**Components**:
```
PlaygroundPage (page.jsx)
├── PlaygroundToolbar (components/PlaygroundToolbar.jsx)
│   ├── Language selector
│   ├── Theme switcher
│   ├── Run/Stop buttons
│   └── Save/Share buttons
├── PlaygroundLayout (components/PlaygroundLayout.jsx)
│   ├── Monaco Editor (code editor)
│   ├── Output Console (execution results)
│   └── View mode (editor/preview/split)
└── TemplatesLibrary (components/TemplatesLibrary.jsx)
    └── 50+ code templates
```

**Template Categories**:
- **Basics**: Hello World, Variables, Loops
- **Data Structures**: Arrays, Objects, Maps
- **Algorithms**: Sorting, Searching, Recursion
- **Web**: DOM Manipulation, Fetch API, Forms
- **React**: Components, Hooks, State Management

**State Management** (usePlaygroundStore):
```javascript
{
  code: string,
  language: string,
  theme: 'vs-dark' | 'light',
  isRunning: boolean,
  output: string,
  selectedTemplate: Template | null
}
```

**Features**:
- Auto-save to localStorage
- Keyboard shortcuts (Ctrl+S, Ctrl+Enter)
- Error highlighting
- Multi-file support (future)

### 5. Courses Discovery

**Location**: `frontend/src/app/app/courses/`

**Features**:
- Browse curated course collections
- Filter by platform, difficulty, duration
- Course recommendations based on learning path
- Personalized course ranking

**Course Card Data**:
```json
{
  "title": "Complete React Developer in 2024",
  "platform": "udemy",
  "instructor": "Andrei Neagoie",
  "rating": 4.7,
  "num_ratings": 87234,
  "duration_hours": 40,
  "price": "$84.99",
  "difficulty": "intermediate",
  "thumbnail_url": "https://...",
  "url": "https://udemy.com/course/...?referralCode=GRADVY"
}
```

**Filters**:
- **Platform**: YouTube, Udemy, Coursera, All
- **Difficulty**: Beginner, Intermediate, Advanced
- **Duration**: < 3hrs, 3-10hrs, 10+hrs
- **Price**: Free, Paid, All
- **Rating**: 4.0+, 4.5+, 4.7+

**APIs**:
```
GET /api/courses/search/?q={query}&platform={platform}
GET /api/courses/recommendations/
GET /api/courses/{id}/
```

### 6. Dashboard & Analytics

**Location**: `frontend/src/app/app/dashboard/`

**Widgets**:
1. **Learning Progress**
   - Current learning paths
   - Modules completed
   - Hours invested
   - Streak counter

2. **Skill Development**
   - Skills acquired
   - Knowledge scores (0-100)
   - Recommended next skills

3. **Activity Timeline**
   - Recent courses completed
   - Quiz scores
   - Code playground sessions

4. **Recommendations**
   - Personalized course suggestions
   - Trending topics in your domain
   - Skill gaps to fill

**Charts** (Recharts):
- Learning hours per week (Line chart)
- Skills distribution (Radar chart)
- Module progress (Progress bars)
- Difficulty progression (Area chart)

**APIs**:
```
GET /api/analytics/dashboard/
GET /api/analytics/progress/
GET /api/analytics/skills/
GET /api/analytics/activity/
```

### 7. Profile & Settings

**Location**: `frontend/src/app/app/profile/` + `frontend/src/app/app/settings/`

#### 7.1 Profile Management
```
/app/profile/info - Basic profile info
/app/profile/actions - Data export, account deletion
```

**Profile Data**:
- Avatar, name, email
- Learning goals & skills
- Social connections (Google, GitHub, LinkedIn)
- Public profile URL

#### 7.2 Account Settings
```
/app/settings/account - Email, password
/app/settings/security - MFA, sessions
/app/settings/privacy - Data consent, analytics
```

**Security Features**:
- Enable/disable 2FA
- View active sessions
- Revoke sessions
- Download backup codes

**Privacy Controls**:
- Analytics consent toggle
- Personalization consent
- Social data permissions
- Data export (JSON)
- Account deletion

**APIs**:
```
GET /api/profile/
PATCH /api/profile/
POST /api/profile/avatar/
GET /api/settings/security/sessions/
POST /api/settings/security/mfa/enable/
POST /api/settings/privacy/export/
DELETE /api/account/delete/
```

### 8. Projects & Portfolio

**Location**: `frontend/src/app/app/projects/`

**Features** (Future):
- Showcase completed projects
- Link to GitHub repositories
- Project descriptions & tech stack
- Difficulty & time invested
- Share project portfolio

**Project Structure**:
```json
{
  "id": 123,
  "title": "Todo App with React",
  "description": "Full-stack todo application",
  "tech_stack": ["React", "Node.js", "MongoDB"],
  "github_url": "https://github.com/user/todo-app",
  "demo_url": "https://todo-app.vercel.app",
  "difficulty": "intermediate",
  "time_invested_hours": 24,
  "completion_date": "2025-11-15",
  "screenshots": ["url1", "url2"]
}
```

### 9. Community (Future)

**Location**: `frontend/src/app/app/community/`

**Planned Features**:
- Discussion forums
- Study groups
- Peer code reviews
- Knowledge sharing
- Q&A platform

### 10. Career & Job Board (Future)

**Location**: `frontend/src/app/app/career/`

**Planned Features**:
- Job recommendations based on skills
- Resume builder
- Interview preparation
- Skill gap analysis for job requirements
- Salary insights

### 11. Achievements & Gamification

**Location**: `frontend/src/app/app/achievements/`

**Achievement Types**:
- **Learning Streaks**: 7 days, 30 days, 100 days
- **Courses Completed**: 5, 10, 25, 50 courses
- **Skills Mastered**: Earn badges per skill
- **Code Playground**: 10, 50, 100 code snippets
- **Difficulty Levels**: Complete advanced modules

**Gamification Elements**:
- XP (Experience Points) system
- Level progression
- Leaderboards (weekly, monthly)
- Badges & trophies

---

## Development Tools & Infrastructure

### 1. Version Control
- **Git** - Source control
- **GitHub** - Code hosting, CI/CD
- **Branch Strategy**: `main` (production), `develop` (staging), `feature/*`

### 2. Development Environment

#### Backend Setup
```bash
# Virtual environment (cross-platform)
python -m venv venv
source venv/bin/activate  # Linux/Mac
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt

# Start data services (Docker)
./scripts/data-start.sh

# Run migrations
./scripts/local-migrate.sh

# Create superuser
./scripts/local-superuser.sh

# Start Django dev server
./scripts/local-dev.sh
```

#### Frontend Setup
```bash
# Install dependencies
npm install

# Start dev server (Turbopack)
npm run dev  # http://localhost:3000

# Type checking
npm run type-check

# Linting
npm run lint

# Production build
npm run build
```

### 3. Code Quality Tools

#### Backend
- **Black** - Code formatting (Python)
- **Flake8** - Linting
- **isort** - Import sorting
- **mypy** - Type checking (optional)

#### Frontend
- **ESLint 8.57.1** - JavaScript/TypeScript linting
- **Prettier** - Code formatting (via ESLint)
- **TypeScript 5.6.2** - Type safety

### 4. Testing (Future)

#### Backend Testing
```python
# Django test framework
python core/manage.py test

# Coverage
pytest --cov=core --cov-report=html
```

#### Frontend Testing
```bash
# Jest + React Testing Library
npm run test

# E2E testing (Playwright)
npm run test:e2e
```

### 5. CI/CD Pipeline (Future)

```yaml
# GitHub Actions workflow
name: CI/CD

on: [push, pull_request]

jobs:
  backend-tests:
    - Install dependencies
    - Run migrations
    - Run tests
    - Check code coverage

  frontend-tests:
    - Install dependencies
    - Run type checking
    - Run linting
    - Run unit tests

  deploy:
    - Build Docker images
    - Push to container registry
    - Deploy to staging/production
```

### 6. Monitoring & Observability (Future)

- **Sentry** - Error tracking & performance
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **ELK Stack** - Log aggregation (Elasticsearch, Logstash, Kibana)

### 7. Documentation

#### Code Documentation
- **Docstrings** (Python) - Function/class documentation
- **JSDoc** (JavaScript/TypeScript) - Function annotations
- **OpenAPI/Swagger** - API documentation (DRF Spectacular)

#### User Documentation
- **README.md** - Project overview & setup
- **DEVELOPER_GUIDE.md** - Development workflow
- **QUICK_REFERENCE.md** - Common commands
- **TROUBLESHOOTING.md** - Common issues & solutions
- **ML_SETUP.md** - ML model configuration

### 8. Environment Variables

#### Backend (.env)
```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://gradvy_user:password@localhost:5434/gradvy_db
MONGODB_URI=mongodb://gradvy_app:password@localhost:27017/gradvy_preferences

# Redis
CELERY_BROKER_URL=redis://localhost:6380/0

# ML APIs
ML_API_PROVIDER=groq
ML_API_KEY=your-groq-api-key
ML_API_MODEL=llama3-70b-8192

# Course APIs
YOUTUBE_API_KEY=your-youtube-api-key
UDEMY_CLIENT_ID=your-udemy-client-id
UDEMY_CLIENT_SECRET=your-udemy-client-secret
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8030
NEXT_PUBLIC_APP_NAME=Gradvy
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

---

## Summary

### Technology Highlights

| Category | Technologies |
|----------|-------------|
| **Frontend** | Next.js 15, React 18, TailwindCSS, Radix UI, Monaco Editor |
| **Backend** | Django 5.1, DRF, Celery, PostgreSQL, MongoDB, Redis |
| **AI/ML** | Groq LLaMA 3 70B, HuggingFace Transformers, scikit-learn |
| **APIs** | YouTube Data API, Udemy API, roadmap.sh, OAuth (Google/GitHub/LinkedIn) |
| **Storage** | PostgreSQL (relational), MongoDB (documents), Redis (cache) |
| **DevOps** | Docker, Git, GitHub Actions (future) |

### Key Innovations

1. **Hybrid AI Learning Paths**: Combines curated roadmap.sh content with AI generation
2. **0-100 Knowledge Scoring**: Replaces discrete levels with continuous assessment
3. **Intelligent Course Ranking**: Multi-factor scoring with user preferences
4. **Real-time API Integration**: Live YouTube + Udemy course search
5. **Privacy-First Design**: GDPR-compliant with granular consent management
6. **Enterprise Security**: JWT + TOTP MFA + session fingerprinting

### Project Scale

- **Backend**: 30,000+ lines of Python code
- **Frontend**: 15,000+ lines of TypeScript/JavaScript
- **ML Services**: 5,000+ lines of AI/ML code
- **Database Models**: 15+ Django models, 5+ MongoDB collections
- **API Endpoints**: 50+ REST endpoints
- **Components**: 100+ React components

---

**Document Version**: 1.0
**Generated**: 2025-11-29
**For**: Gradvy Presentation & Report

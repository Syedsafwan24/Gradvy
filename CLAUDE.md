# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT

1. Always Prioritize writing clean, simple, and modular code.
2. Use simple & easy-to-understand language. Write in short sentences.
3. DO NOT BE LAZY! Always read files IN FULL!!
4. Don't Update the services or endpoints which are already confirmed and working! But your written if just optimizing then it's fine
5. When Working with features please create a feature/** branch and then implement it in that branch and ask for MERGE!, if Okay then merge it in 'develop' branch

## COMMENTS

1. Write Comments in your code. Explain Exactly what you are doing in you comments.

## PLAN MODE RULES

<restrictions>
## RESTRICTIONS
Do What has be asked; nothing more, nothing less

## PLAN MODE RULES

1. Never propose a plan of action, UNLESS the user tells you to explicitly
2. IF you are in 'plan mode', it means the User wants to TALK and PLAN with you, not do any code
3. DO NOT propose code changes while you are in 'plan mode'
4. When in 'plan mode', just respond to the user. That's it
   </restrictions>

## Header Comments

- EVERY file has to start with 4 lines of comments!
  1. Exact file Location in codebase
  2. clear description of what this file does
  3. clear description of why this file exists
  4. RELVANT FILES:  comma-seperated list of 2-4 most relevant files
- NEVER delete these "header comments" from the files you're editing.

## Standard Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.
8. DO NOT BE LAZY. NEVER BE LAZY. IF THERE IS A BUG FIND THE ROOT CAUSE AND FIX IT. NO TEMPORARY FIXES. YOU ARE A SENIOR DEVELOPER. NEVER BE LAZY
9. MAKE ALL FIXES AND CODE CHANGES AS SIMPLE AS HUMANLY POSSIBLE. THEY SHOULD ONLY IMPACT NECESSARY CODE RELEVANT TO THE TASK AND NOTHING ELSE. IT SHOULD IMPACT AS LITTLE CODE AS POSSIBLE. YOUR GOAL IS TO NOT INTRODUCE ANY BUGS. IT'S ALL ABOUT SIMPLICITY

## Project Overview

**Gradvy** is an AI-powered personalized learning platform with a hybrid Django/Next.js architecture. The backend is a comprehensive user data collection and management system designed for adaptive learning experiences.

### Core Architecture

- **Backend**: Django 5.1.3 with hybrid development setup (Django local, data services in Docker)
- **Frontend**: Next.js 15.0.0 with TypeScript
- **Database**:
  - PostgreSQL 15 (user authentication, sessions)
  - MongoDB (user preferences, behavioral data, analytics)
  - Redis 7 (caching, Celery message broker)
- **Background Processing**: Celery 5.3.6 with Redis broker
- **Authentication**: JWT + TOTP MFA with backup codes

## Development Commands

### Initial Setup

```bash
# Backend setup - run from backend/
./scripts/local-setup.sh     # Complete environment setup
./scripts/data-start.sh      # Start Docker data services
./scripts/local-migrate.sh   # Run database migrations
./scripts/local-superuser.sh # Create admin user

# Frontend setup - run from frontend/
npm install
npm run dev
```

### Development Workflow

```bash
# Backend development server
./scripts/local-dev.sh       # Interactive Django server with service checks

# Background services (optional)
./scripts/local-celery.sh    # Celery worker (background tasks)
./scripts/local-flower.sh    # Task monitoring UI (http://localhost:5555)

# Frontend development
npm run dev                  # Next.js dev server (http://localhost:3000)
npm run build               # Production build
npm run lint                # ESLint
npm run type-check          # TypeScript checking
```

### Database Management

```bash
# Django migrations
./scripts/local-migrate.sh   # Apply Django migrations
python core/manage.py makemigrations  # Create new migrations

# Direct database access
docker exec -it gradvy-postgres psql -U gradvy_user -d gradvy_db
./scripts/mongodb-status.sh  # Check MongoDB status

# Preferences system
./scripts/preferences-seed.sh   # Seed test data
./scripts/preferences-reset.sh  # Reset preferences data
```

### Testing & Quality

```bash
# Backend tests
python core/manage.py test
python core/manage.py check

# Frontend tests/linting
npm run lint
npm run type-check

# Service validation
./scripts/validate-setup.sh
```

## Key Architecture Patterns

### Hybrid Development Setup

- **Data Services**: Run in Docker containers (PostgreSQL, Redis, MongoDB)
- **Application**: Runs locally for fast development and debugging
- **Benefits**: Hot reloading, IDE integration, persistent data, no container rebuilds

### User Data Collection System

The core feature is comprehensive user data collection following Netflix/Duolingo patterns:

**MongoDB Documents** (`backend/core/apps/preferences/models.py`):

- `UserPreference`: Main user profile with embedded analytics
- `SocialData`: LinkedIn/GitHub profiles, social learning metrics
- `BehavioralPatterns`: Learning habits, interaction sequences, performance analytics
- `PrivacySettings`: Granular consent management with GDPR compliance
- `DeviceUsagePattern`: Cross-device learning behavior tracking

**Frontend Tracking** (`frontend/src/components/`):

- Event tracking in React components
- Privacy-first data collection with consent management
- Real-time analytics dashboard
- Progressive profiling during onboarding

### Authentication & Security

- **MFA**: TOTP with QR codes + backup codes (`backend/core/apps/auth/`)
- **Session Management**: Fingerprinting, device tracking, session security
- **Privacy**: Cookie consent, data export/deletion, granular permissions
- **JWT**: Optimized tokens to prevent race conditions (24h access, 30d refresh)

### Background Processing

- **Celery Tasks**: User analytics processing, MFA cleanup, data pipeline
- **Monitoring**: Flower UI for task monitoring and debugging
- **Scheduling**: Celery Beat for periodic maintenance tasks

## File Structure Highlights

### Backend Structure

```
backend/core/
├── apps/
│   ├── auth/           # Authentication, MFA, social login
│   │   ├── api/        # REST API endpoints
│   │   ├── services/   # Business logic (auth, MFA, user services)
│   │   ├── tasks/      # Celery background tasks
│   │   └── utils/      # Device detection, error handling
│   └── preferences/    # User data collection & analytics
│       ├── models.py   # MongoDB schemas (UserPreference, SocialData)
│       ├── views.py    # Privacy controls, data export
│       └── urls.py     # Preferences API endpoints
├── core/
│   ├── settings.py     # Django configuration
│   ├── urls.py        # URL routing
│   └── middleware.py  # Security, session, cookie middleware
└── scripts/           # Development automation
```

### Frontend Structure

```
frontend/src/
├── app/               # Next.js app router pages
│   ├── onboarding/    # Multi-step user onboarding
│   ├── preferences/   # Privacy controls & data management
│   └── settings/      # Account & security settings
├── components/
│   ├── auth/          # Authentication components
│   ├── onboarding/    # Onboarding flow components
│   ├── preferences/   # Privacy dashboard, data controls
│   └── ui/            # Reusable UI components (shadcn/ui)
├── hooks/             # Custom React hooks
├── services/          # API client services
└── store/             # Redux store with RTK Query
```

## Development Tips

### Working with MongoDB

The preferences system uses MongoEngine for flexible document storage. Key models are in `backend/core/apps/preferences/models.py`. When updating schema:

1. Update the MongoEngine model classes
2. No migrations needed (schema-less)
3. Test with `./scripts/preferences-seed.sh`

### Adding New Analytics

To add new user tracking:

1. Update MongoDB embedded documents in `models.py`
2. Add React event tracking in components
3. Create Celery tasks for data processing in `tasks/`
4. Update privacy controls to include new data types

### MFA Development

The MFA system is comprehensive with TOTP and backup codes. Key files:

- `backend/core/apps/auth/services/mfa_service.py` - Core MFA logic
- `backend/core/apps/auth/api/views.py` - MFA API endpoints
- Frontend MFA components in `frontend/src/components/auth/`

### Environment Configuration

- Backend: `.env` file with PostgreSQL, Redis, MongoDB connections
- Frontend: Next.js environment variables for API endpoints
- Use `./scripts/validate-setup.sh` to verify configuration

### Debugging

- Django runs locally with full debugger support
- Background tasks visible in Flower UI (http://localhost:5555)
- MongoDB data accessible via MongoDB Compass (mongodb://localhost:27017)
- Frontend has React DevTools support

## Security Considerations

- Never commit secrets or API keys
- All user data collection requires explicit consent
- GDPR compliance built into privacy settings
- MFA backup codes are single-use and expire
- Session fingerprinting prevents session hijacking
- Cookie security middleware enforces secure cookie settings

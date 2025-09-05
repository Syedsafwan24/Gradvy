# Redis Setup for Windows

## Quick Redis Setup Options:

### Option 1: Download Redis for Windows (Recommended)

1. Download Redis from: https://github.com/tporadowski/redis/releases
2. Extract the zip file to a folder like `C:\Redis`
3. Add `C:\Redis` to your PATH environment variable
4. Open Command Prompt and run: `redis-server`

### Option 2: Use Portable Redis

We can download and set up Redis manually in our project folder.

### Option 3: Use Docker Desktop

If you prefer Docker, install Docker Desktop and run:

```bash
docker run -d -p 6379:6379 --name redis-server redis:alpine
```

## For Development: Alternative approach

For now, we can:

1. Use Django's database for simple task queuing (django-q or django-rq)
2. Or use PostgreSQL as Celery broker (less efficient but works)

Let's proceed with a manual Redis setup...

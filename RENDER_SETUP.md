# Render Setup For Daily Gemini Ingestion

This app needs more than the public API service if you want daily automatic ingestion to run.

## Required Render services

Create or verify these backend-side services:

1. Web service
   Command:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers`

2. Background worker
   Command:
   `celery -A app.tasks.ingestion_tasks worker --loglevel=info --queues=ingestion,trends`

3. Scheduler service
   Command:
   `celery -A app.tasks.ingestion_tasks beat --loglevel=info`

If only the web service exists, the site can serve pages but daily ingestion will not run automatically.

## Shared environment variables

All three backend-side services should have the same values for:

- `DATABASE_URL`
- `REDIS_URL`
- `REDIS_CACHE_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `CORS_ORIGINS`
- `PUBLIC_BASE_URL`
- `GITHUB_TOKEN`
- `HUGGINGFACE_TOKEN`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_RESULTS_PER_CATEGORY`
- `GEMINI_LOOKBACK_DAYS`

Recommended Gemini settings:

- `GEMINI_MODEL=gemini-2.5-flash`
- `GEMINI_RESULTS_PER_CATEGORY=3`
- `GEMINI_LOOKBACK_DAYS=7`

## What the scheduler does

Celery Beat schedules these jobs from `backend/app/tasks/ingestion_tasks.py`:

- daily full ingestion
- GitHub metadata refresh every 6 hours
- score recalculation every 12 hours
- daily trend generation

The daily full ingestion now includes Gemini discovery for each active category.

## Manual test after deploy

After deploying the updated backend and worker services, manually trigger one Gemini run:

`POST /api/v1/ingestion/trigger?source=gemini`

Example full URL:

`https://your-backend.onrender.com/api/v1/ingestion/trigger?source=gemini`

Then verify:

1. `GET /api/v1/ingestion/status` returns Gemini config details.
2. New rows appear in `research_items`.
3. The frontend shows the new items in lists and category pages.

## Important note about the dashboard

The dashboard currently shows source cards for enum-based sources like arXiv, GitHub, and Papers with Code.
Gemini discovery is integrated into ingestion, but it is not yet shown as its own source card in the frontend.

## Security

Do not keep real secrets committed in `.env.production`.
Rotate any exposed credentials and store the real values only in Render environment variables.

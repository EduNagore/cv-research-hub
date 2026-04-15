# CV Research Hub

A professional, modern, and scalable web application for monitoring the most important daily updates in computer vision and neural-network-based image AI.

## Overview

CV Research Hub is a comprehensive platform that automatically collects, organizes, and displays the most relevant daily updates in computer vision and deep learning for image-related tasks. It serves as a daily command center for researchers, engineers, and practitioners who want to stay current with the newest architectures, models, and practical approaches.

## Features

### Core Features

- **Home Dashboard**: Daily summary, top items, category breakdowns, and key statistics
- **Research Items**: Browse, filter, and search through papers, models, datasets, and repositories
- **Category Navigation**: Organized browsing by task type (classification, detection, segmentation, etc.)
- **Advanced Filters**: Filter by date, category, source, type, code availability, and more
- **Global Search**: Full-text search across all content
- **Detail Pages**: Comprehensive information for each research item
- **Personal Organization**: Favorites, bookmarks, and read-later lists

### Advanced Features

- **Trends Section**: Track emerging architectures, topics, methods, and keywords
- **Comparison Section**: Compare different approaches by task
- **Decision Support**: Get personalized recommendations based on your project requirements
- **Automatic Updates**: Daily ingestion from arXiv, Papers with Code, and GitHub
- **Relevance Scoring**: Intelligent ranking based on multiple factors

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Background Jobs**: Celery with Redis
- **API Documentation**: Auto-generated OpenAPI/Swagger

### Frontend
- **Framework**: React + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Task Queue**: Redis + Celery
- **Monitoring**: Flower (Celery monitoring)

## Project Structure

```
cv-research-hub/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configuration
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Celery tasks
│   │   └── main.py      # Application entry point
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # React frontend
│   └── app/
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── pages/       # Page components
│       │   ├── lib/         # Utilities and API client
│       │   └── types/       # TypeScript types
│       └── package.json
├── docker/              # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- (Optional) Node.js 20+ for local frontend development
- (Optional) Python 3.11+ for local backend development

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd cv-research-hub
```

2. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/app/.env.example frontend/app/.env
```

3. Edit the `.env` files with your configuration (especially API keys)

4. Start all services:
```bash
cd docker
docker-compose up -d
```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Flower (Celery monitoring): http://localhost:5555

### Manual Setup

#### Backend

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Make sure PostgreSQL is running
createdb cv_research_hub

# Run migrations
alembic upgrade head
```

4. Start the backend:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Install dependencies:
```bash
cd frontend/app
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Configuration

### Environment Variables

#### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/cv_research_hub` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `GITHUB_TOKEN` | GitHub API token (optional) | - |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

#### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## Data Sources

The platform ingests data from the following sources:

1. **arXiv**: Papers from cs.CV, cs.LG, cs.AI categories
2. **Papers with Code**: Research papers with implementations
3. **GitHub**: Trending repositories related to computer vision

### Adding New Sources

To add a new data source:

1. Create a new ingestion service in `backend/app/services/ingestion.py`
2. Implement the ingestion logic
3. Add the source to the `SourceType` enum
4. Update the daily ingestion task

## API Endpoints

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/dashboard/daily-summary` - Get daily summary

### Research Items
- `GET /api/v1/items` - List research items (with filters)
- `GET /api/v1/items/search` - Search research items
- `GET /api/v1/items/{slug}` - Get single item

### Categories & Tags
- `GET /api/v1/categories` - List categories
- `GET /api/v1/tags` - List tags

### User Items
- `GET /api/v1/user-items/favorites` - Get favorites
- `POST /api/v1/user-items/{id}/favorite` - Toggle favorite
- `GET /api/v1/user-items/bookmarks` - Get bookmarks
- `POST /api/v1/user-items/{id}/bookmark` - Toggle bookmark

### Trends
- `GET /api/v1/trends` - List trends
- `GET /api/v1/trends/statistics` - Get trend statistics

### Comparisons
- `GET /api/v1/comparisons` - List comparisons
- `GET /api/v1/comparisons/{slug}` - Get comparison details

### Decision Support
- `POST /api/v1/decision-support/recommend` - Get recommendations
- `GET /api/v1/decision-support/tasks` - Get supported tasks

### Ingestion (Admin)
- `POST /api/v1/ingestion/trigger` - Trigger manual ingestion
- `GET /api/v1/ingestion/status` - Get ingestion status

## Background Jobs

The platform uses Celery for background job processing:

- **Daily Ingestion**: Runs daily to fetch new papers and repositories
- **GitHub Metadata Refresh**: Updates GitHub stars and forks every 6 hours
- **Score Recalculation**: Updates relevance scores every 12 hours
- **Trend Generation**: Analyzes trends daily

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend/app
npm test
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Production Considerations

1. **Security**:
   - Use strong passwords for database
   - Set up HTTPS
   - Configure proper CORS origins
   - Use environment variables for secrets

2. **Performance**:
   - Use a production WSGI server (e.g., Gunicorn)
   - Enable database connection pooling
   - Set up Redis for caching
   - Use CDN for static assets

3. **Monitoring**:
   - Set up logging
   - Monitor Celery tasks with Flower
   - Track API performance

### Docker Deployment

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- arXiv for providing open access to research papers
- Papers with Code for curating papers with implementations
- The computer vision research community

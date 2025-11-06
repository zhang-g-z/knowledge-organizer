# Knowledge Organizer

## Description
This project integrates async FastAPI with Celery to handle background tasks and uses Vue for the frontend interface.

## Installation

```bash
pip install -r requirements.txt
```

## Run the application

To run the backend:

```bash
uvicorn app.main:app --reload
```

To run the Celery worker:

```bash
celery -A app.celery_app worker --loglevel=info
```

To run the frontend:

```bash
npm install
npm run serve
```

# API Documentation
API documentation can be accessed at /docs after running the server.


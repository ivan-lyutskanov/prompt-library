# Prompt Library

A web application for managing AI prompts with CRUD functionality.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTMX + Alpine.js + TailwindCSS

## Getting Started

### Build and start the application
```bash
docker-compose up --build
```

### Access the application
```bash
open http://localhost:8000
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

## Features

- Create, read, update, and delete prompts
- Modern, responsive UI
- No page reloads with HTMX
- Persistent SQLite database

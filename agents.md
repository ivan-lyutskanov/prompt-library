# AI Agent Instructions for Prompt Library Project

## Project Overview
**Prompt Library** is a web application for managing AI prompts with full CRUD functionality. It features a modern, responsive UI with no-reload interactions using HTMX and Alpine.js.

### Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTMX + Alpine.js + TailwindCSS
- **Containerization**: Docker + Docker Compose

## Project Structure

```
prompt-library/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point & routes
│   ├── models.py        # SQLAlchemy models (Prompt, Note)
│   ├── schemas.py       # Pydantic schemas for validation
│   ├── database.py      # Database configuration & session management
│   └── crud.py          # CRUD operations
├── templates/
│   ├── base.html        # Base HTML template
│   ├── index.html       # Main page template
│   └── components/      # HTMX partial templates
│       ├── prompt_list.html
│       ├── prompt_card.html
│       ├── prompt_edit.html
│       ├── prompt_modal.html      # Full-screen modal component
│       ├── notes_section.html
│       ├── note_card.html
│       ├── modal_notes_list.html  # Modal-specific notes list
│       └── modal_note_card.html   # Modal-specific note cards
├── static/
│   └── styles.css       # Custom CSS styles
├── data/
│   └── prompts.db       # SQLite database (created at runtime)
├── requirements.txt     # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Architecture & Design Patterns

### Backend Architecture
1. **FastAPI Application** (`app/main.py`)
   - RESTful API endpoints with CRUD operations
   - Returns HTML responses for HTMX integration
   - Dependency injection for database sessions
   - Jinja2 template rendering

2. **Data Layer**
   - **Models** (`models.py`): Two main entities
     - `Prompt`: Stores AI prompts with title, content, timestamps
     - `Note`: Stores notes associated with prompts (one-to-many relationship)
   - **Schemas** (`schemas.py`): Pydantic models for validation
     - Base, Create, Update, and full schemas for both entities
   - **CRUD** (`crud.py`): Database operations abstracted into functions
   - **Database** (`database.py`): SQLAlchemy engine and session management

3. **Database Relationships**
   - Prompts have a one-to-many relationship with Notes
   - Notes are deleted automatically when parent Prompt is deleted (cascade)

### Frontend Architecture
1. **HTMX-Driven Interactions**
   - Form submissions update parts of the page without full reload
   - Uses `hx-post`, `hx-put`, `hx-delete`, `hx-get` attributes
   - Targets specific DOM elements with `hx-target` and `hx-swap`

2. **Alpine.js State Management**
   - Used for client-side state (e.g., loading states, form visibility)
   - Reactive data binding with `x-data`, `x-show`, `x-on`

3. **Component-Based Templates**
   - Reusable HTML components in `templates/components/`
   - Each component represents a specific UI element or section

4. **Modal Architecture**
   - Full-screen modal for viewing/editing prompts with integrated notes sidebar
   - Uses Alpine.js for modal state management (show/hide, view/edit modes)
   - Change tracking to refresh main card when modal closes
   - Modal-specific component versions (e.g., `modal_note_card.html`) to avoid ID conflicts

## API Endpoints

### Prompt Endpoints
- `GET /` - Main page with all prompts
- `POST /prompts` - Create new prompt (returns updated prompt list)
- `GET /prompts/{prompt_id}/edit` - Get edit form for prompt
- `PUT /prompts/{prompt_id}` - Update prompt (returns updated card)
- `DELETE /prompts/{prompt_id}` - Delete prompt
- `GET /prompts/{prompt_id}/modal` - Get prompt data as JSON for modal
- `GET /prompts/{prompt_id}/card` - Get prompt card HTML (for refreshing)
- `GET /prompts/{prompt_id}/notes-list` - Get notes list HTML for modal

### Note Endpoints
- `POST /prompts/{prompt_id}/notes` - Create note for prompt (detects modal context via `HX-Target` header)
- `PUT /notes/{note_id}` - Update note (returns card or modal card based on `HX-Target`)
- `DELETE /notes/{note_id}` - Delete note

## Development Guidelines for AI Agents

### When Making Backend Changes

1. **Adding New Endpoints**
   - Add route handler in `main.py`
   - Use dependency injection: `db: Session = Depends(get_db)`
   - Return HTML responses for HTMX: `response_class=HTMLResponse`
   - Create corresponding CRUD functions in `crud.py`

2. **Modifying Database Models**
   - Update models in `models.py`
   - Update corresponding Pydantic schemas in `schemas.py`
   - Consider migrations (currently using `create_all()` for simplicity)
   - Update CRUD operations in `crud.py` if needed

3. **CRUD Operations**
   - All database operations should go through `crud.py` functions
   - Use type hints: `list[models.Prompt]`, `models.Prompt | None`
   - Always refresh objects after commits: `db.refresh(db_object)`
   - Update `updated_at` timestamp manually when updating entities

### When Making Frontend Changes

1. **HTMX Patterns**
   - Use `hx-post`, `hx-put`, `hx-delete` for form submissions
   - Target specific elements: `hx-target="#element-id"`
   - Use `hx-swap="outerHTML"` to replace entire element
   - Add `hx-indicator` for loading states
   - **Limitation**: HTMX doesn't support dynamic attributes via Alpine.js bindings (`:hx-post`)

2. **Alpine.js Patterns**
   - Initialize state with `x-data="{ ... }"`
   - Toggle visibility with `x-show="condition"`
   - Handle events with `x-on:click="handler"`
   - Access refs with `$refs.refName`

3. **Hybrid Approach (Alpine.js + Fetch)**
   - **When to use**: When HTMX attributes need dynamic values from Alpine.js state
   - **Example**: Modal forms where the endpoint URL depends on `currentPrompt.id`
   - **Pattern**: Use `@submit.prevent` with Alpine.js method that calls `fetch()` API
   - **After fetch**: Update DOM manually and call `htmx.process()` on new elements
   ```javascript
   async submitForm(event) {
     const response = await fetch(url, { method: 'POST', body: formData });
     const html = await response.text();
     targetElement.outerHTML = html;
     htmx.process(targetElement); // Re-enable HTMX on new elements
   }
   ```

3. **Template Components**
   - Keep components small and focused
   - Each component should be self-contained
   - Pass context variables via `TemplateResponse`
   - Follow existing naming: `{entity}_{action}.html`

### Code Style & Conventions

1. **Python**
   - Use type hints for all function parameters and returns
   - Follow PEP 8 style guide
   - Use docstrings for modules and public functions
   - Prefer `| None` over `Optional[]` for union types
   - Use `list[Type]` over `List[Type]` (Python 3.11+)

2. **Database**
   - All timestamps use `datetime.utcnow()`
   - Use cascade deletes for dependent relationships
   - Order queries: newest first (`.order_by(Model.updated_at.desc())`)
   - Use `joinedload()` when fetching relationships

3. **Templates**
   - Use TailwindCSS utility classes for styling
   - Keep JavaScript minimal (leverage HTMX + Alpine.js)
   - Use semantic HTML elements
   - Maintain consistent spacing and indentation

### Testing & Validation

1. **Manual Testing**
   - Start app: `docker-compose up --build`
   - Access at: `http://localhost:8000`
   - Test all CRUD operations through the UI
   - Verify database persistence (check `data/prompts.db`)

2. **Things to Verify**
   - Form submissions work without page reload
   - Edit mode toggles correctly
   - Delete operations remove items from UI
   - Loading states appear during operations
   - Timestamps update correctly

### Common Tasks & How to Approach Them

#### Adding a New Field to Prompts
1. Add column to `Prompt` model in `models.py`
2. Add field to schemas in `schemas.py` (Base, Create, Update)
3. Update CRUD operations in `crud.py` to handle new field
4. Update form in `index.html` or edit component
5. Update display in `prompt_card.html`

#### Adding a New Entity
1. Create model class in `models.py` (inherit from `Base`)
2. Create schemas in `schemas.py` (Base, Create, Update, full)
3. Create CRUD functions in `crud.py`
4. Add routes in `main.py`
5. Create template components as needed
6. Update main template to include new entity

#### Modifying UI/UX
1. Locate relevant template in `templates/` or `templates/components/`
2. Update HTML structure and TailwindCSS classes
3. Add HTMX attributes for dynamic behavior
4. Add Alpine.js directives for client-side interactivity

#### Working with the Modal
1. **Modal state** is managed in `index.html` root Alpine.js data
2. **Opening modal**: Call `openModal(promptId)` which fetches prompt data and notes
3. **Editing in modal**: Uses fetch API (not HTMX) due to dynamic URL requirements
4. **Change tracking**: Set `promptChanged = true` when edits/notes are modified
5. **Closing modal**: If `promptChanged`, automatically refreshes the card via `/prompts/{id}/card`
6. **Context detection**: Backend checks `HX-Target` header to return modal vs. card templates
   - Modal targets include "modal-note" or "modal-notes-list"
   - Card operations use standard element IDs

## Environment & Dependencies

### Python Dependencies
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM
- `jinja2==3.1.2` - Template engine
- `python-multipart==0.0.6` - Form data parsing

### Docker Configuration
- **Base Image**: `python:3.11-slim`
- **Port**: 8000
- **Volumes**: 
  - `.:/app` - Live code reload
  - `./data:/app/data` - Database persistence
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`


## Key Considerations for AI Agents

1. **No Page Reloads**: All interactions use HTMX, so ensure responses return appropriate HTML fragments, not JSON (except for DELETE operations)

2. **Database Persistence**: The SQLite database is in `data/` directory and persists across container restarts. Don't delete it accidentally.

3. **Hot Reload**: The Docker setup includes `--reload` flag, so Python code changes are automatically reflected without restart.

4. **No Migrations**: Currently using `create_all()` for database setup. For production, consider adding Alembic migrations.

5. **Cascade Deletes**: Notes are automatically deleted when parent Prompt is deleted. Be aware of this when modifying relationships.

6. **Timestamp Management**: `created_at` is auto-set by SQLAlchemy, but `updated_at` must be manually updated in CRUD operations.

7. **Form Handling**: All forms use `Form(...)` from FastAPI, not JSON bodies. This is intentional for HTMX compatibility.

8. **Component Returns**: Most endpoints return template components, not full pages. This enables HTMX to swap specific page sections.

9. **Context-Aware Endpoints**: Some endpoints (e.g., note operations) detect context via `HX-Target` header and return different templates for modal vs. card usage.

10. **Mixed HTMX/Fetch Pattern**: The modal uses fetch API for operations requiring dynamic URLs (due to Alpine.js binding limitations with HTMX). Standard card views continue to use pure HTMX.

## Useful Commands

```bash
# Start application
docker-compose up --build

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Access container shell
docker-compose exec web bash

# View database (if sqlite3 installed)
sqlite3 data/prompts.db

# Run Python shell in container
docker-compose exec web python
```


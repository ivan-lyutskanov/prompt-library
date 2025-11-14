"""FastAPI application entry point."""
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Prompt Library")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Render main page with all prompts."""
    prompts = crud.get_prompts(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "prompts": prompts}
    )


@app.post("/prompts", response_class=HTMLResponse)
async def create_prompt(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create new prompt and return updated prompt list."""
    prompt_create = schemas.PromptCreate(title=title, content=content)
    crud.create_prompt(db, prompt_create)
    prompts = crud.get_prompts(db)
    return templates.TemplateResponse(
        "components/prompt_list.html",
        {"request": request, "prompts": prompts}
    )


@app.get("/prompts/{prompt_id}/edit", response_class=HTMLResponse)
async def get_edit_form(
    request: Request,
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Return edit form for specific prompt."""
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return templates.TemplateResponse(
        "components/prompt_edit.html",
        {"request": request, "prompt": prompt}
    )


@app.put("/prompts/{prompt_id}", response_class=HTMLResponse)
async def update_prompt(
    request: Request,
    prompt_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update prompt and return updated card."""
    prompt_update = schemas.PromptUpdate(title=title, content=content)
    updated_prompt = crud.update_prompt(db, prompt_id, prompt_update)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return templates.TemplateResponse(
        "components/prompt_card.html",
        {"request": request, "prompt": updated_prompt}
    )


@app.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Delete prompt and return empty response."""
    success = crud.delete_prompt(db, prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"success": True}


@app.get("/health")
async def health_check():
    """Health check endpoint - test live reload by changing this message."""
    return {"status": "healthy", "message": "Live reload is working!"}

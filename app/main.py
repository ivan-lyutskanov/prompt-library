"""FastAPI application entry point."""
from fastapi import FastAPI, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

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


@app.get("/search", response_class=HTMLResponse)
async def search_prompts(
    request: Request,
    q: str = "",
    db: Session = Depends(get_db)
):
    """Search prompts by title, content, or notes and return filtered list."""
    search_query = q.strip() if q else None
    prompts = crud.get_prompts(db, search_query=search_query)
    return templates.TemplateResponse(
        "components/prompt_list.html",
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


# Note endpoints

@app.post("/prompts/{prompt_id}/notes", response_class=HTMLResponse)
async def create_note(
    request: Request,
    prompt_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create new note for a prompt and return updated notes list."""
    # Verify prompt exists
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    note_create = schemas.NoteCreate(content=content)
    crud.create_note(db, prompt_id, note_create)
    
    # Refresh prompt to get updated notes
    prompt = crud.get_prompt(db, prompt_id)
    
    # Check if request is from modal (check HX-Target header)
    hx_target = request.headers.get('HX-Target', '')
    is_modal = 'modal-notes-list' in hx_target.lower()
    
    if is_modal:
        return templates.TemplateResponse(
            "components/modal_notes_list.html",
            {"request": request, "prompt": prompt}
        )
    else:
        return templates.TemplateResponse(
            "components/notes_section.html",
            {"request": request, "prompt": prompt}
        )


@app.put("/notes/{note_id}", response_class=HTMLResponse)
async def update_note(
    request: Request,
    note_id: int,
    content: str = Form(...),
    modal: bool = False,
    db: Session = Depends(get_db)
):
    """Update note and return updated note card."""
    note_update = schemas.NoteUpdate(content=content)
    updated_note = crud.update_note(db, note_id, note_update)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check target to determine if it's from modal
    hx_target = request.headers.get('HX-Target', '')
    is_modal = 'modal-note' in hx_target.lower()
    
    template = "components/modal_note_card.html" if is_modal else "components/note_card.html"
    
    return templates.TemplateResponse(
        template,
        {"request": request, "note": updated_note}
    )


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete note and return empty response."""
    success = crud.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}


# Modal endpoints

@app.get("/prompts/{prompt_id}/modal")
async def get_prompt_modal_data(prompt_id: int, db: Session = Depends(get_db)):
    """Get prompt data in JSON format for modal."""
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {
        "id": prompt.id,
        "title": prompt.title,
        "content": prompt.content,
        "updated_at": prompt.updated_at.strftime('%Y-%m-%d %H:%M'),
        "created_at": prompt.created_at.strftime('%Y-%m-%d %H:%M')
    }


@app.get("/prompts/{prompt_id}/notes-list", response_class=HTMLResponse)
async def get_modal_notes_list(
    request: Request,
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Get notes list HTML for modal."""
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return templates.TemplateResponse(
        "components/modal_notes_list.html",
        {"request": request, "prompt": prompt}
    )


@app.get("/prompts/{prompt_id}/card", response_class=HTMLResponse)
async def get_prompt_card(
    request: Request,
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Get prompt card HTML."""
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return templates.TemplateResponse(
        "components/prompt_card.html",
        {"request": request, "prompt": prompt}
    )


@app.get("/prompts/{prompt_id}/export")
async def export_prompt_json(prompt_id: int, db: Session = Depends(get_db)):
    """Export prompt with notes in JSON format."""
    prompt = crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {
        "title": prompt.title,
        "content": prompt.content,
        "created_at": prompt.created_at.isoformat(),
        "updated_at": prompt.updated_at.isoformat(),
        "notes": [
            {
                "content": note.content,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in prompt.notes
        ]
    }


@app.post("/prompts/import", response_class=HTMLResponse)
async def import_prompt(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import prompt from JSON file and return updated prompt list."""
    try:
        # Read and parse JSON file
        contents = await file.read()
        data = json.loads(contents)
        
        # Validate required fields
        if "title" not in data or "content" not in data:
            raise HTTPException(status_code=400, detail="Invalid JSON: title and content are required")
        
        # Create prompt
        prompt_create = schemas.PromptCreate(
            title=data["title"],
            content=data["content"]
        )
        new_prompt = crud.create_prompt(db, prompt_create)
        
        # Create notes if provided
        if "notes" in data and isinstance(data["notes"], list):
            for note_data in data["notes"]:
                if "content" in note_data:
                    note_create = schemas.NoteCreate(content=note_data["content"])
                    crud.create_note(db, new_prompt.id, note_create)
        
        # Return updated prompt list
        prompts = crud.get_prompts(db)
        return templates.TemplateResponse(
            "components/prompt_list.html",
            {"request": request, "prompts": prompts}
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing prompt: {str(e)}")

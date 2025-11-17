"""CRUD operations for database."""
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app import models, schemas


def get_prompts(db: Session, search_query: str | None = None) -> list[models.Prompt]:
    """Get all prompts, ordered by updated_at descending. Optionally filter by search query."""
    query = db.query(models.Prompt)
    
    if search_query:
        search_term = f"%{search_query}%"
        # Search in prompt title, content, or notes content
        query = query.outerjoin(models.Note).filter(
            (models.Prompt.title.ilike(search_term)) |
            (models.Prompt.content.ilike(search_term)) |
            (models.Note.content.ilike(search_term))
        ).distinct()
    
    return query.order_by(models.Prompt.updated_at.desc()).all()


def get_prompt(db: Session, prompt_id: int) -> models.Prompt | None:
    """Get a single prompt by id with notes."""
    return db.query(models.Prompt).options(joinedload(models.Prompt.notes)).filter(models.Prompt.id == prompt_id).first()


def create_prompt(db: Session, prompt: schemas.PromptCreate) -> models.Prompt:
    """Create a new prompt."""
    db_prompt = models.Prompt(
        title=prompt.title,
        content=prompt.content
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


def update_prompt(db: Session, prompt_id: int, prompt: schemas.PromptUpdate) -> models.Prompt | None:
    """Update an existing prompt."""
    db_prompt = get_prompt(db, prompt_id)
    if db_prompt:
        db_prompt.title = prompt.title
        db_prompt.content = prompt.content
        db_prompt.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_prompt)
    return db_prompt


def delete_prompt(db: Session, prompt_id: int) -> bool:
    """Delete a prompt."""
    db_prompt = get_prompt(db, prompt_id)
    if db_prompt:
        db.delete(db_prompt)
        db.commit()
        return True
    return False


# Note CRUD operations

def get_notes(db: Session, prompt_id: int) -> list[models.Note]:
    """Get all notes for a specific prompt, ordered by created_at descending."""
    return db.query(models.Note).filter(models.Note.prompt_id == prompt_id).order_by(models.Note.created_at.desc()).all()


def get_note(db: Session, note_id: int) -> models.Note | None:
    """Get a single note by id."""
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def create_note(db: Session, prompt_id: int, note: schemas.NoteCreate) -> models.Note:
    """Create a new note for a prompt."""
    db_note = models.Note(
        prompt_id=prompt_id,
        content=note.content
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: schemas.NoteUpdate) -> models.Note | None:
    """Update an existing note."""
    db_note = get_note(db, note_id)
    if db_note:
        db_note.content = note.content
        db_note.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> bool:
    """Delete a note."""
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

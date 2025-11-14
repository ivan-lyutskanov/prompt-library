"""CRUD operations for database."""
from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas


def get_prompts(db: Session) -> list[models.Prompt]:
    """Get all prompts, ordered by updated_at descending."""
    return db.query(models.Prompt).order_by(models.Prompt.updated_at.desc()).all()


def get_prompt(db: Session, prompt_id: int) -> models.Prompt | None:
    """Get a single prompt by id."""
    return db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()


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

"""Pydantic schemas for validation."""
from datetime import datetime
from pydantic import BaseModel


class NoteBase(BaseModel):
    """Base schema for Note."""
    content: str


class NoteCreate(NoteBase):
    """Schema for creating a Note."""
    pass


class NoteUpdate(NoteBase):
    """Schema for updating a Note."""
    pass


class Note(NoteBase):
    """Schema for Note with all fields."""
    id: int
    prompt_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptBase(BaseModel):
    """Base schema for Prompt."""
    title: str
    content: str


class PromptCreate(PromptBase):
    """Schema for creating a Prompt."""
    pass


class PromptUpdate(PromptBase):
    """Schema for updating a Prompt."""
    pass


class Prompt(PromptBase):
    """Schema for Prompt with all fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    notes: list[Note] = []

    class Config:
        from_attributes = True

"""Pydantic schemas for validation."""
from datetime import datetime
from pydantic import BaseModel


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

    class Config:
        from_attributes = True

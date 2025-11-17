"""Utilities for markdown processing and HTML sanitization."""
import markdown2
import bleach
from typing import Any


# Allowed HTML tags and attributes for security
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'strong', 'em', 'u', 's', 'del', 'ins',
    'ul', 'ol', 'li',
    'blockquote', 'code', 'pre',
    'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'hr', 'div', 'span',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class'],
}


def render_markdown(text: str | None) -> str:
    """
    Convert markdown text to sanitized HTML.
    
    Args:
        text: Markdown text to convert
        
    Returns:
        Sanitized HTML string
    """
    if not text:
        return ""
    
    # Convert markdown to HTML with extras for better rendering
    html = markdown2.markdown(
        text,
        extras=[
            "fenced-code-blocks",  # ```code```
            "tables",              # GitHub-style tables
            "break-on-newline",    # Single newlines become <br>
            "code-friendly",       # Better code block handling
            "cuddled-lists",       # Lists without blank lines
            "strike",              # ~~strikethrough~~
            "task_list",           # - [ ] checkboxes
        ]
    )
    
    # Sanitize HTML to prevent XSS attacks
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return clean_html


def markdown_filter(text: Any) -> str:
    """
    Jinja2 filter for rendering markdown.
    
    Usage in templates: {{ prompt.content | markdown }}
    """
    if text is None:
        return ""
    return render_markdown(str(text))

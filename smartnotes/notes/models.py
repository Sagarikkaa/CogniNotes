"""
Note Model - Database Agent
Stores notes along with their AI-generated summaries and keywords.
Uses SQLite as the database backend (configured in settings.py).
"""

from django.db import models


class Note(models.Model):
    """
    Represents a user's note with AI-processed metadata.
    
    Fields:
        content   - The raw text content pasted by the user
        summary   - AI-generated summary (from BART model)
        keywords  - Comma-separated keywords (from TF-IDF extraction)
        created_at - Timestamp when the note was first created
    """
    content = models.TextField(
        help_text="The original note text entered by the user"
    )
    summary = models.TextField(
        blank=True,
        default='',
        help_text="AI-generated summary of the note"
    )
    keywords = models.TextField(
        blank=True,
        default='',
        help_text="Comma-separated keywords extracted via TF-IDF"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this note was created"
    )

    class Meta:
        ordering = ['-created_at']  # Newest notes first
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        """Display the first 50 characters of the note content."""
        return self.content[:50] + ('...' if len(self.content) > 50 else '')

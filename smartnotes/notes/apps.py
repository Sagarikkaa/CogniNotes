"""App configuration for the notes app."""

from django.apps import AppConfig


class NotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notes'
    verbose_name = 'Smart Notes'

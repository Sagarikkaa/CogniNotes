"""Admin registration for Note model."""

from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('created_at',)

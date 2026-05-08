"""
URL configuration for smartnotes project.
Routes requests to the notes app.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include all notes app URLs (frontend + API)
    path('', include('notes.urls')),
]

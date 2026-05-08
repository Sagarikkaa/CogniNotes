"""
URL configuration for the notes app.
Maps frontend pages and API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Auth routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard routes
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_workspace, name='student_workspace'),

    # Root — redirect based on auth status
    path('', views.index, name='index'),

    # API endpoint — handles all AI processing requests
    path('api/process/', views.process_api, name='process_api'),
    path('api/extract/', views.extract_api, name='extract_api'),
]

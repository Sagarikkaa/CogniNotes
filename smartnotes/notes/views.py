"""
Views - Backend API Agent
Handles HTTP requests and delegates AI processing to the Orchestrator.
Supports login, teacher dashboard, and student workspace views.
"""

import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import PyPDF2
import requests
from bs4 import BeautifulSoup

from .models import Note
from .agents.orchestrator import OrchestratorAgent

# Initialize orchestrator once — models are loaded on first request
orchestrator = None


def get_orchestrator():
    """
    Lazy-load the orchestrator (and its sub-agents/models).
    This avoids loading heavy ML models at Django startup.
    """
    global orchestrator
    if orchestrator is None:
        orchestrator = OrchestratorAgent()
    return orchestrator


def login_view(request):
    """
    Login page — dual Student/Teacher login.
    """
    # Always log out the user if they reach the login page directly
    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'student')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or role == 'teacher':
                return redirect('teacher_dashboard')
            return redirect('student_workspace')
        else:
            error = 'Invalid username or password. Please try again.'

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    """Log out and redirect to login."""
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def teacher_dashboard(request):
    """
    Teacher Dashboard — view all notes with stats.
    """
    notes = Note.objects.all().order_by('-created_at')[:20]
    notes_count = Note.objects.count()
    summaries_count = Note.objects.exclude(summary='').count()

    return render(request, 'teacher_dashboard.html', {
        'notes': notes,
        'notes_count': notes_count,
        'summaries_count': summaries_count,
        'students_count': 0,
        'queries_count': 0,
    })


@login_required(login_url='/login/')
def student_workspace(request):
    """
    Student AI Workspace — main note processing interface.
    """
    notes = Note.objects.all().order_by('-created_at')[:10]
    return render(request, 'student_workspace.html', {
        'notes': notes,
        'teacher_notes': notes,
    })


def index(request):
    """
    Root URL handler — force logout and always redirect to login.
    """
    logout(request)
    return redirect('login')


@csrf_exempt  # Allow AJAX requests without CSRF token for simplicity
@require_http_methods(["POST"])
def process_api(request):
    """
    API endpoint: POST /api/process/

    Accepts JSON body:
    {
        "text": "The note content to process",
        "action": "summarize" | "keywords" | "qa",
        "question": "Optional - required only for 'qa' action"
    }

    Returns JSON:
    {
        "status": "success" | "error",
        "action": "the action performed",
        "result": "the output (string, list, or dict)"
    }
    """
    try:
        # Parse the JSON request body
        body = json.loads(request.body)
        text = body.get('text', '').strip()
        action = body.get('action', '').strip()
        question = body.get('question', '').strip()

        # Validate required fields
        if not text:
            return JsonResponse({
                'status': 'error',
                'action': action,
                'result': 'Please paste some notes before processing.'
            }, status=400)

        if not action:
            return JsonResponse({
                'status': 'error',
                'action': '',
                'result': 'Please specify an action: summarize, keywords, or qa.'
            }, status=400)

        if action == 'qa' and not question:
            return JsonResponse({
                'status': 'error',
                'action': 'qa',
                'result': 'Please enter a question to ask about your notes.'
            }, status=400)

        # Route to the orchestrator
        orch = get_orchestrator()
        response = orch.process_request(
            input_text=text,
            action=action,
            question=question if action == 'qa' else None
        )

        # Save to database on successful summarize or keywords
        if response['status'] == 'success' and action in ('summarize', 'keywords'):
            _save_note(text, action, response['result'])

        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'action': '',
            'result': 'Invalid JSON in request body.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'action': '',
            'result': f'Server error: {str(e)}'
        }, status=500)


def _save_note(text, action, result):
    """
    Save or update a Note in the database.
    If a note with the same content exists, update it;
    otherwise create a new one.
    """
    note, created = Note.objects.get_or_create(
        content=text,
        defaults={'summary': '', 'keywords': ''}
    )
    if action == 'summarize':
        note.summary = result
    elif action == 'keywords':
        note.keywords = ', '.join(result) if isinstance(result, list) else result
    note.save()

@csrf_exempt
@require_http_methods(["POST"])
def extract_api(request):
    """
    API endpoint: POST /api/extract/
    Accepts multipart/form-data with either 'url' or 'file' (PDF).
    Returns extracted text.
    """
    try:
        url = request.POST.get('url', '').strip()
        pdf_file = request.FILES.get('file')

        text = ""
        if url:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n\n'.join([p.get_text() for p in paragraphs])
            if not text.strip():
                text = soup.get_text(separator='\n', strip=True)
                
        elif pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

        if not text.strip():
            return JsonResponse({'status': 'error', 'result': 'Could not extract text from the provided source.'}, status=400)

        return JsonResponse({'status': 'success', 'result': text.strip()})

    except Exception as e:
        return JsonResponse({'status': 'error', 'result': f'Extraction error: {str(e)}'}, status=500)

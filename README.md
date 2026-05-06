📌 CogniNotes – AI-Powered Smart Learning Platform

CogniNotes is an AI-driven web application that transforms traditional note-taking into an intelligent learning experience. It enables users to summarize content, extract key insights, and perform contextual question answering from a single unified interface.

🚀 Problem Statement

Students and professionals deal with large volumes of notes from lectures, meetings, and research.

⏳ Significant time is wasted re-reading content
📚 Increasing academic workload leads to information overload
❌ Existing tools lack intelligent summarization and Q&A features
❌ No unified platform for summarization, keyword extraction, and question answering
💡 Solution

CogniNotes provides an AI-powered multi-agent system that:

Automatically summarizes notes

Extracts important keywords

Answers user queries in real-time

Supports multiple input formats

⚙️ Core Features
🧠 Abstractive Summarization
Generates human-like summaries using Transformer-based models
🔑 Keyword Extraction
Identifies key topics using statistical NLP techniques
❓ Contextual Question Answering
Answers questions directly from the provided notes
📄 Multi-Source Input Support
Manual text input
PDF upload
Web URL scraping
👩‍🏫 Teacher Dashboard
Monitor student activity
View summaries and usage analytics
👩‍🎓 Student Workspace
Access notes
Interact with AI features
💾 Smart Persistence
Automatically saves and updates notes in the database

🏗️ System Architecture

Input → Extract API → Process API → Orchestrator → AI Models → Database → Dashboard

Workflow:

User inputs text / PDF / URL

Content is extracted and cleaned

Request sent to processing API

Orchestrator routes task to AI modules

AI models generate output

Results stored and displayed dynamically

🤖 AI Models Used

BART (facebook/bart-large-cnn)

Task: Abstractive Text Summarization

TF-IDF (Scikit-learn)

Task: Keyword Extraction

DistilBERT (distilbert-base-uncased-distilled-squad)

Task: Question Answering

🛠️ Tech Stack

Backend: Python, Django, Django REST Framework

Frontend: HTML, CSS, JavaScript (Django Templates)

AI/NLP: HuggingFace Transformers, Scikit-learn

Database: SQLite

Other Tools: BeautifulSoup, PyPDF2

⚡ Key Highlights

Real-time AI processing

Multi-agent architecture

Role-based access (Teacher & Student)

Automatic data persistence

Lightweight and responsive UI

🎯 Conclusion

CogniNotes demonstrates how AI-powered NLP systems can transform passive note-taking into an interactive and intelligent learning process. By integrating summarization, keyword extraction, and Q&A into a single platform, it significantly improves efficiency and comprehension.

💡 Tagline

“Smarter Notes. Deeper Understanding.”

"""
FastAPI entrypoint for the Smart Placement Preparation Assistant.
Initializes and seeds the SQLite database on startup, registers all REST API routers,
and serves the vanilla HTML/CSS/JS frontend.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

# Ensure project root is on sys.path whether invoked from project root or backend/
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.database import get_db_path
from backend.routers import attempts, chat, progress, questions, quizzes
from backend.seed import seed_database

FRONTEND_DIR = ROOT_DIR / "frontend"

# Initialize & seed database immediately so it is ready in all execution contexts
seed_database()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Ensure SQLite schema and seed data exist on server startup."""
    seed_database()
    yield


app = FastAPI(
    title="Smart Placement Preparation Assistant API",
    description=(
        "Full-stack placement preparation platform powered by FastAPI and SQLite. "
        "Includes Python Question Bank, Interactive MCQ Quizzes, Progress Analytics, "
        "and a Rule-Based Technical Interview Chatbot."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS so frontend works whether served by FastAPI, Live Server, or file://
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(quizzes.router)
app.include_router(progress.router)
app.include_router(chat.router)


@app.get("/", tags=["System"])
def root_health_check() -> Dict[str, Any]:
    """Root API status and endpoint directory."""
    return {
        "application": "Smart Placement Preparation Assistant",
        "version": "1.0.0",
        "status": "online",
        "database": "SQLite (placement_assistant.db)",
        "database_path": "database/placement_assistant.db",
        "frontend_url": "http://127.0.0.1:8000/index.html",
        "docs_url": "http://127.0.0.1:8000/docs",
        "endpoints": {
            "dashboard_stats": "GET /dashboard/stats",
            "questions_list": "GET /questions",
            "question_detail": "GET /questions/{question_id}",
            "submit_attempt": "POST /attempts",
            "quizzes_list": "GET /quizzes",
            "quiz_detail": "GET /quizzes/{quiz_id}",
            "submit_quiz": "POST /quizzes/{quiz_id}/submit",
            "student_progress": "GET /students/{student_id}/progress",
            "quiz_history": "GET /students/{student_id}/quiz-history",
            "recent_activity": "GET /students/{student_id}/recent-activity",
            "technical_chatbot": "POST /chat",
        },
    }


@app.get("/app", include_in_schema=False)
def redirect_to_frontend() -> RedirectResponse:
    """Convenience redirect to the frontend dashboard."""
    return RedirectResponse(url="/index.html")


# Serve frontend HTML pages and static assets directly from FastAPI
if FRONTEND_DIR.exists():
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    HTML_PAGES = [
        "index.html",
        "questions.html",
        "question-detail.html",
        "quiz.html",
        "results.html",
        "progress.html",
        "chatbot.html",
    ]

    for page_name in HTML_PAGES:
        page_path = FRONTEND_DIR / page_name

        def _make_page_handler(target: Path):
            def _serve_page() -> FileResponse:
                return FileResponse(str(target))
            return _serve_page

        app.add_api_route(
            f"/{page_name}",
            _make_page_handler(page_path),
            methods=["GET"],
            include_in_schema=False,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


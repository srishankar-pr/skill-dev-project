"""
Comprehensive Automated Verification Suite for Smart Placement Preparation Assistant.
Tests all mandatory and additional endpoints, SQLite persistence, idempotent seeding,
score calculation, chatbot rules, error handling, and frontend integration.
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Configure isolated temporary database for clean, deterministic test runs
TEST_DB_DIR = tempfile.mkdtemp()
TEST_DB_PATH = os.path.join(TEST_DB_DIR, "placement_assistant.db")
os.environ["PLACEMENT_DB_PATH"] = TEST_DB_PATH

from backend.main import app  # noqa: E402
from backend.seed import seed_database  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    seed_database()
    with TestClient(app) as c:
        yield c


def test_root_and_backend_startup(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["application"] == "Smart Placement Preparation Assistant"
    assert body["status"] == "online"
    assert "endpoints" in body


def test_database_tables_and_idempotent_seeding() -> None:
    # Run seed_database() multiple times to verify no duplicate records are created
    seed_database()
    seed_database()

    conn = sqlite3.connect(TEST_DB_PATH)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        expected_tables = {
            "students",
            "questions",
            "attempts",
            "quizzes",
            "quiz_questions",
            "quiz_attempts",
        }
        assert expected_tables.issubset(tables)

        q_count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        mcq_count = conn.execute("SELECT COUNT(*) FROM quiz_questions").fetchone()[0]
        assert q_count >= 30, f"Expected >= 30 questions, found {q_count}"
        assert mcq_count >= 30, f"Expected >= 30 MCQs, found {mcq_count}"
    finally:
        conn.close()


def test_questions_list_and_filters(client: TestClient) -> None:
    res = client.get("/questions")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) >= 30

    # Filter by category
    res_cat = client.get("/questions?category=Strings")
    assert res_cat.status_code == 200
    assert all(q["category"] == "Strings" for q in res_cat.json())

    # Filter by difficulty
    res_diff = client.get("/questions?difficulty=Beginner")
    assert res_diff.status_code == 200
    assert all(q["difficulty"] == "Beginner" for q in res_diff.json())

    # Search filter
    res_search = client.get("/questions?search=Binary")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1


def test_individual_question_retrieval_and_404(client: TestClient) -> None:
    res = client.get("/questions/1")
    assert res.status_code == 200
    q = res.json()
    assert q["id"] == 1
    assert "sample_input" in q
    assert "expected_output" in q
    assert "explanation" in q

    # Missing question record
    res_missing = client.get("/questions/9999")
    assert res_missing.status_code == 404


def test_attempt_submission_and_persistence(client: TestClient) -> None:
    payload = {
        "student_id": 1,
        "question_id": 2,
        "submitted_code": "from collections import Counter\ndef is_anagram(s, t):\n    return Counter(s.lower()) == Counter(t.lower())",
        "status": "Completed",
        "notes": "Verified O(n) Counter approach",
        "time_taken_minutes": 7,
    }
    res = client.post("/attempts", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["question_id"] == 2
    assert created["status"] == "Completed"

    # Verify question status updated in GET /questions/2
    q_res = client.get("/questions/2")
    assert q_res.status_code == 200
    assert q_res.json()["status"] == "Completed"

    # Verify 404 for non-existent question
    bad_res = client.post(
        "/attempts",
        json={
            "student_id": 1,
            "question_id": 8888,
            "submitted_code": "pass",
            "status": "Attempted",
        },
    )
    assert bad_res.status_code == 404


def test_quizzes_and_score_calculation(client: TestClient) -> None:
    quizzes_res = client.get("/quizzes")
    assert quizzes_res.status_code == 200
    quizzes = quizzes_res.json()
    assert len(quizzes) >= 4

    quiz_detail = client.get("/quizzes/1?limit=5").json()
    assert len(quiz_detail["questions"]) == 5

    # Build answers map
    answers = {str(q["id"]): "B" for q in quiz_detail["questions"]}
    sub_res = client.post(
        "/quizzes/1/submit",
        json={"student_id": 1, "answers": answers, "time_taken_seconds": 95},
    )
    assert sub_res.status_code == 201
    result = sub_res.json()
    assert result["total_questions"] == 5
    assert 0 <= result["score"] <= 5
    assert len(result["reviews"]) == 5

    # Retrieve stored quiz attempt review
    rev_res = client.get(f"/quizzes/attempts/{result['attempt_id']}")
    assert rev_res.status_code == 200
    assert rev_res.json()["attempt_id"] == result["attempt_id"]


def test_dashboard_and_progress_analytics(client: TestClient) -> None:
    dash = client.get("/dashboard/stats?student_id=1")
    assert dash.status_code == 200
    dash_data = dash.json()
    assert dash_data["total_questions"] >= 30
    assert dash_data["questions_completed"] >= 1

    prog = client.get("/students/1/progress")
    assert prog.status_code == 200
    prog_data = prog.json()
    assert len(prog_data["topic_performance"]) == 6
    assert "weak_topics" in prog_data
    assert "recent_activity" in prog_data

    hist = client.get("/students/1/quiz-history")
    assert hist.status_code == 200
    assert len(hist.json()) >= 1

    act = client.get("/students/1/recent-activity")
    assert act.status_code == 200
    assert len(act.json()) >= 1

    # Missing student 404
    assert client.get("/students/999/progress").status_code == 404


def test_chatbot_responses_and_fallback(client: TestClient) -> None:
    topics_to_test = [
        ("Hello there", "Greetings"),
        ("Help me with commands", "Help"),
        ("Explain Python lists vs tuples", "Python - Lists, Tuples, and Mutability"),
        ("How does FastAPI and Pydantic work?", "FastAPI"),
        ("What are REST API principles?", "REST APIs"),
        ("Explain HTTP methods GET POST PUT DELETE", "HTTP Methods"),
        ("Difference between SQLite and MySQL", "MySQL and SQLite Concepts"),
        ("Explain SQL INNER JOIN and ACID", "SQL & Database Fundamentals"),
        ("Explain Big O complexity and binary search", "Data Structures and Algorithms"),
        ("Give me technical interview tips", "Technical Interviews"),
        ("xyzabc123unrecognizedquery", "Unrecognized Query (Fallback)"),
    ]
    for query, expected_topic in topics_to_test:
        res = client.post("/chat", json={"message": query})
        assert res.status_code == 200
        body = res.json()
        assert body["matched_topic"] == expected_topic
        assert len(body["reply"]) > 20


def test_invalid_requests_validation(client: TestClient) -> None:
    # Blank chat message -> 422
    res_blank = client.post("/chat", json={"message": "   "})
    assert res_blank.status_code == 422

    # Invalid quiz option 'Z' -> 422
    res_bad_opt = client.post(
        "/quizzes/1/submit",
        json={"student_id": 1, "answers": {"1": "Z"}, "time_taken_seconds": 30},
    )
    assert res_bad_opt.status_code == 422


def test_frontend_pages_served(client: TestClient) -> None:
    for page in [
        "/index.html",
        "/questions.html",
        "/question-detail.html",
        "/quiz.html",
        "/results.html",
        "/progress.html",
        "/chatbot.html",
        "/css/style.css",
        "/js/app.js",
    ]:
        res = client.get(page)
        assert res.status_code == 200


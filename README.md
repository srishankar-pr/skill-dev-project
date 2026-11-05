# Smart Placement Preparation Assistant

A complete, full-stack **Smart Placement Preparation Assistant** web application engineered for college campus placement preparation. Built using **Python 3, FastAPI, Pydantic, SQLite (`sqlite3`), HTML5, CSS3, and Vanilla JavaScript (Fetch API)**.

---

## 1. Project Overview

The **Smart Placement Preparation Assistant** is a unified self-study and assessment platform designed for engineering students preparing for technical coding rounds, MCQ screening tests, and technical interviews. All statistics, question statuses, quiz scores, and topic mastery breakdowns are dynamically computed from live **SQLite** database records (`database/placement_assistant.db`).

---

## 2. Core Features

1. **Dynamic Placement Dashboard (`index.html`)**
   - Personalized student welcome banner and placement readiness indicator.
   - Live KPIs: Total Available Questions (`32`), Questions Attempted, Questions Completed, Average Quiz Score, and Overall Preparation Progress (`%`).
   - Difficulty-tier completion bars (`Beginner`, `Intermediate`, `Advanced`).
   - Recently attempted coding problems and recommended weak topics to practice next.

2. **Python Question Bank (`questions.html` and `question-detail.html`)**
   - **32 curated Python coding questions** across **6 mandatory categories**:
     - `Strings` (6 questions)
     - `Lists` (6 questions)
     - `Dictionaries` (5 questions)
     - `Functions` (5 questions)
     - `Number problems` (5 questions)
     - `Basic algorithms` (5 questions)
   - Three difficulty levels: `Beginner`, `Intermediate`, and `Advanced`.
   - Real-time search, category filter, difficulty filter, and completion status filter.
   - Dedicated problem workspace with sample input, expected output, toggleable optimal approach hints, starter Python code editor, revision notes, and one-click attempt/completion logging.

3. **Interactive MCQ Quiz Module (`quiz.html` and `results.html`)**
   - **34 technical Multiple-Choice Questions (MCQs)** organized across **4 themed quizzes** (including a Comprehensive Placement Readiness Mock).
   - Randomized question selection on every quiz launch (`GET /quizzes/{quiz_id}?randomize=true`).
   - Live timer, progress counter, automatic server-side score calculation, grade classification, and SQLite persistence.
   - Detailed **Quiz Results and Answer Review** page showing user selections, correct answers, and technical explanations for every question, plus historical quiz attempt logs.

4. **Progress Analytics (`progress.html`)**
   - Comprehensive topic-wise mastery breakdown combining coding completion (60%) and MCQ quiz accuracy (40%).
   - Visual CSS bar charts for topic mastery and historical quiz score trajectory.
   - Automatic **Weak Topics Diagnostics** highlighting categories below 65% mastery.
   - Unified chronological activity timeline merging coding attempts and quiz submissions.

5. **Rule-Based Technical Chatbot (`chatbot.html` and `backend/chatbot.py`)**
   - Modular, deterministic Python keyword- and phrase-matching chatbot (`POST /chat`) with zero external LLM or paid API dependencies.
   - Covers 10+ technical domains: **Python, FastAPI, REST APIs, HTTP Methods, SQLite vs. MySQL, SQL and ACID, Data Structures and Algorithms, Technical Interviews, Greetings, and Help**.
   - Returns structured replies, code examples, matched topic badges, confidence scores, and interactive follow-up suggestion chips, plus graceful fallback handling for unrecognized queries.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) | Responsive SaaS UI, interactive charts, state management |
| **API Client** | Browser `fetch()` API | Asynchronous REST communication with FastAPI |
| **Backend** | Python 3, FastAPI, Uvicorn | REST API routing, static asset serving, OpenAPI docs |
| **Validation** | Pydantic v2 | Request payload validation and response serialization |
| **Database** | SQLite 3 (`sqlite3` standard library) | Serverless relational persistence (`placement_assistant.db`) |
| **Chatbot** | Python Rule-Based Engine (`chatbot.py`) | Keyword scoring and predefined technical knowledge base |
| **Testing** | Pytest, FastAPI `TestClient` (`httpx`) | Automated integration and API verification |

---

## 4. System Architecture

```text
+-------------------------------------------------------------------+
|                   FRONTEND (HTML5 / CSS3 / JS)                    |
|  index.html | questions.html | question-detail.html | quiz.html   |
|  results.html | progress.html | chatbot.html                      |
+---------------------------------+---------------------------------+
                                  |  HTTP / JSON (Fetch API)
                                  v
+-------------------------------------------------------------------+
|                     FASTAPI BACKEND (main.py)                     |
|  Routers: questions.py | attempts.py | quizzes.py | progress.py   |
|           chat.py <---> Rule-Based Engine (chatbot.py)            |
|  Validation: Pydantic Schemas (schemas.py)                        |
+---------------------------------+---------------------------------+
                                  |  Parameterized SQL
                                  v
+-------------------------------------------------------------------+
|             DATA ACCESS & SQLITE (models.py / database.py)        |
|  File: database/placement_assistant.db                            |
|  Tables: students, questions, attempts, quizzes,                  |
|          quiz_questions, quiz_attempts                            |
+-------------------------------------------------------------------+
```

---

## 5. Folder Structure

```text
smart-placement-assistant/
|
+-- backend/
|   +-- __init__.py
|   +-- main.py              # FastAPI application entrypoint & static file mount
|   +-- database.py          # SQLite connection management & table DDL
|   +-- models.py            # Parameterized SQL data access layer
|   +-- schemas.py           # Pydantic request/response models
|   +-- chatbot.py           # Modular rule-based technical chatbot
|   +-- seed.py              # Idempotent database seeder (32 Questions, 34 MCQs)
|   +-- requirements.txt     # Backend Python dependencies
|   +-- routers/
|       +-- __init__.py
|       +-- questions.py     # GET /questions, GET /questions/{id}
|       +-- attempts.py      # POST /attempts
|       +-- quizzes.py       # GET /quizzes, GET /quizzes/{id}, POST /quizzes/{id}/submit
|       +-- progress.py      # GET /dashboard/stats, GET /students/{id}/progress, etc.
|       +-- chat.py          # POST /chat
|
+-- frontend/
|   +-- index.html           # Dashboard page
|   +-- questions.html       # Python Question Bank page
|   +-- question-detail.html # Coding problem workspace page
|   +-- quiz.html            # Interactive MCQ Quiz page
|   +-- results.html         # Quiz Results & Answer Review page
|   +-- progress.html        # Progress Analytics & Charts page
|   +-- chatbot.html         # Technical Chatbot interface page
|   +-- css/
|   |   +-- style.css        # Modern SaaS stylesheet
|   +-- js/
|       +-- app.js           # Shared Fetch API wrapper, toast & badge utilities
|       +-- dashboard.js     # Dashboard dynamic logic
|       +-- questions.js     # Question Bank & Detail workspace logic
|       +-- quiz.js          # Quiz runner & Results review logic
|       +-- progress.js      # Analytics & chart rendering logic
|       +-- chatbot.js       # Chatbot UI logic
|
+-- database/
|   +-- .gitkeep
|   +-- placement_assistant.db  # Auto-generated SQLite database file
|
+-- tests/
|   +-- test_api.py          # Automated Pytest verification suite
|
+-- screenshots/
|   +-- .gitkeep
+-- run.py                   # One-command Python full-stack launcher
+-- .gitignore
+-- requirements.txt
+-- README.md
```

---

## 6. Installation and Local Setup Instructions

### Quick Start (One-Command Project Launcher)
To initialize the SQLite database, start the FastAPI server, and open the frontend dashboard automatically in your browser:
```bash
python run.py
```

### Manual Setup Steps

1. **Create and Activate a Virtual Environment (Optional):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Initialization:**
   Automatically handled on startup (`backend/seed.py` creates `database/placement_assistant.db`, all 6 tables, and seeds 32 questions + 34 MCQs idempotently).
4. **Start the Server via Uvicorn:**
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
5. **Access URLs:**
   - **Frontend Dashboard**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)
   - **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **API Health Check**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 7. API Endpoint Documentation and Sample Payloads

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API health check and endpoint directory |
| `GET` | `/dashboard/stats` | Dynamic dashboard KPIs, recent attempts, recommended topics |
| `GET` | `/questions` | List all 32 Python questions (supports `category`, `difficulty`, `search`, `status` query filters) |
| `GET` | `/questions/{question_id}` | Full problem details, starter code, and latest student attempt |
| `POST` | `/attempts` | Submit a coding problem attempt (`Attempted` or `Completed`) |
| `GET` | `/quizzes` | List all available MCQ quizzes and student best scores |
| `GET` | `/quizzes/{quiz_id}` | Fetch a quiz with randomized MCQ questions |
| `POST` | `/quizzes/{quiz_id}/submit` | Submit quiz answers, compute score, persist to SQLite, and return full review |
| `GET` | `/quizzes/attempts/{attempt_id}` | Retrieve a saved quiz attempt report with explanations |
| `GET` | `/students/{student_id}/progress` | Full analytics, topic mastery, weak areas, and study time |
| `GET` | `/students/{student_id}/quiz-history` | Historical list of all quiz attempts for the student |
| `GET` | `/students/{student_id}/recent-activity` | Unified activity timeline of coding attempts and quizzes |
| `POST` | `/chat` | Send a technical query to the rule-based chatbot |

### Sample API Requests and Expected Responses

#### 1. `GET /questions/1`
```bash
curl -X GET "http://127.0.0.1:8000/questions/1?student_id=1"
```
```json
{
  "id": 1,
  "title": "Reverse Words in a Sentence",
  "category": "Strings",
  "difficulty": "Beginner",
  "sample_input": "s = \"  smart   placement  assistant \"",
  "expected_output": "\"assistant placement smart\"",
  "status": "Completed",
  "attempts_count": 1
}
```

#### 2. `POST /attempts`
```bash
curl -X POST "http://127.0.0.1:8000/attempts" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "question_id": 3,
    "submitted_code": "def first_unique_char(s: str) -> int:\n    return 0",
    "status": "Completed",
    "notes": "Two-pass frequency dictionary O(n)",
    "time_taken_minutes": 10
  }'
```

#### 3. `POST /chat`
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Difference between SQLite and MySQL"}'
```

---

## 8. Testing Instructions

Run the automated test suite from the project root:
```bash
pytest -v
```

---

## 9. College Project Demonstration Workflow

1. **Dashboard Overview (`index.html`)**: Show live KPI cards, readiness badge, difficulty completion bars, and recommended weak topics fetched from SQLite.
2. **Question Bank and Workspace (`questions.html` -> `question-detail.html`)**: Filter questions by category or difficulty, open a problem, toggle the approach hint, and submit a solution as **Completed**.
3. **Interactive Timed Quiz (`quiz.html` -> `results.html`)**: Launch a quiz, answer the randomized MCQs, submit, and inspect the **Question-by-Question Answer Review**.
4. **Progress Analytics (`progress.html`)**: Highlight topic mastery bars, quiz score trajectory chart, and priority weak topics list.
5. **Technical Chatbot (`chatbot.html`)**: Query *"SQLite vs MySQL"*, *"Python lists vs tuples"*, *"FastAPI"*, and an unknown query to demonstrate deterministic keyword matching and fallback handling.

---

## 10. Known Limitations and Future Enhancements

- **No Server-Side Arbitrary Code Execution**: For security, submitted Python code is stored in SQLite rather than executed on the host server.
- **Single-File Embedded Database**: SQLite is ideal for local deployments; high-concurrency production setups can migrate to PostgreSQL.
- **Future Enhancements**: In-browser WebAssembly (Pyodide) code runner, multi-student authentication, and spaced-repetition flashcards.

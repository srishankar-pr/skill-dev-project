"""
Rule-based Technical Interview & Placement Preparation Assistant Chatbot.
Uses deterministic keyword scoring and pattern matching without external LLMs or paid APIs.
"""

import re
from typing import Any, Dict, List, Optional

KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "topic": "Greetings",
        "keywords": ["hello", "hi", "hey", "good morning", "good evening", "good afternoon", "greetings", "start"],
        "exact_words": {"hi", "hey", "hello", "greetings"},
        "reply": (
            "Hello! I am the **Rule-Based Technical Placement Assistant**.\n\n"
            "I use deterministic keyword and pattern matching to help you revise core technical concepts for placement drives. "
            "You can ask me about:\n"
            "- **Python Core** (lists vs tuples, decorators, generators, GIL, OOP, comprehensions)\n"
            "- **FastAPI & Backend** (Pydantic, dependency injection, async endpoints, Uvicorn)\n"
            "- **REST APIs & HTTP Methods** (GET, POST, PUT, PATCH, DELETE, status codes, idempotency)\n"
            "- **Databases & SQL** (SQLite vs MySQL, JOINs, indexing, ACID, normalization, SQL injection)\n"
            "- **Data Structures & Algorithms** (Big-O complexity, hash maps, two pointers, binary search, recursion)\n"
            "- **Technical Interview Strategy** (coding round approach, HR questions, system design basics)"
        ),
        "code_example": None,
        "suggestions": [
            "Explain Python lists vs tuples",
            "How does FastAPI validate requests?",
            "Difference between SQLite and MySQL",
            "Explain HTTP methods and idempotency",
        ],
    },
    {
        "topic": "Help",
        "keywords": ["help", "support", "what can you do", "commands", "topics", "guide", "how to use", "menu", "options"],
        "exact_words": {"help", "menu", "topics", "commands"},
        "reply": (
            "### How to Use the Technical Knowledge Assistant\n\n"
            "This module is a **rule-based technical reference bot** built in Python (`chatbot.py`). "
            "Type any technical keyword or question related to campus placements:\n\n"
            "1. **Python**: Ask about `decorators`, `generators`, `GIL`, `mutable vs immutable`, `dict comprehension`, or `*args and **kwargs`.\n"
            "2. **FastAPI**: Ask about `FastAPI`, `Pydantic validation`, `Uvicorn`, or `APIRouter`.\n"
            "3. **REST APIs & HTTP**: Ask about `REST principles`, `GET vs POST`, `PUT vs PATCH`, or `HTTP status codes`.\n"
            "4. **SQL & Databases**: Ask about `SQLite vs MySQL`, `SQL JOINs`, `ACID properties`, `Primary vs Foreign Key`, or `parameterized queries`.\n"
            "5. **DSA**: Ask about `Big O complexity`, `binary search`, `hash tables`, `stack vs queue`, or `dynamic programming`.\n"
            "6. **Interviews**: Ask about `interview tips`, `how to approach coding problems`, or `common placement mistakes`."
        ),
        "code_example": None,
        "suggestions": [
            "What are Python decorators?",
            "Explain SQL INNER JOIN vs LEFT JOIN",
            "What is Big-O time complexity?",
            "Top coding interview tips",
        ],
    },
    {
        "topic": "Python - Lists, Tuples, and Mutability",
        "keywords": ["list", "tuple", "mutable", "immutable", "lists vs tuples", "difference between list and tuple", "slicing", "comprehension"],
        "exact_words": {"list", "lists", "tuple", "tuples", "mutable", "immutable"},
        "reply": (
            "### Python Lists vs. Tuples & Mutability\n\n"
            "- **List (`list`)**: Mutable, ordered sequence (`[1, 2, 3]`). Supports in-place modification (`append`, `extend`, `pop`, `sort`). Dynamic array under the hood; cannot be used as a dictionary key.\n"
            "- **Tuple (`tuple`)**: Immutable, ordered sequence (`(1, 2, 3)`). Faster iteration, smaller memory footprint, and **hashable** (if all elements are hashable), allowing it to be used as a `dict` key or `set` element.\n"
            "- **Interview Tip**: Mention that copying a list with `b = a` only copies the reference. Use `a.copy()` or `a[:]` for a shallow copy, and `copy.deepcopy(a)` for nested mutable structures."
        ),
        "code_example": (
            "# List Comprehension (Mutable)\n"
            "squares = [x * x for x in range(5) if x % 2 == 0]  # [0, 4, 16]\n\n"
            "# Tuple as a Dictionary Key (Immutable & Hashable)\n"
            "grid_cache = {(0, 0): 'Origin', (1, 2): 'Checkpoint'}"
        ),
        "suggestions": [
            "What are Python decorators and generators?",
            "How do Python dictionaries work internally?",
            "Explain *args and **kwargs in Python",
        ],
    },
    {
        "topic": "Python - Advanced Concepts (Decorators, Generators, GIL, OOP)",
        "keywords": [
            "python", "decorator", "decorators", "generator", "generators", "yield",
            "gil", "global interpreter lock", "lambda", "args", "kwargs", "oop",
            "inheritance", "init", "self", "dunder", "magic methods", "dictionary", "dict"
        ],
        "exact_words": {"python", "decorator", "generator", "yield", "gil", "lambda", "oop", "dict"},
        "reply": (
            "### Core Python Interview Concepts\n\n"
            "1. **Decorators**: Higher-order functions that wrap another function to extend behavior (logging, auth, caching) without modifying its source code (`@functools.wraps`).\n"
            "2. **Generators (`yield`)**: Produce items lazily one at a time, maintaining state between calls with $O(1)$ auxiliary memory instead of storing an entire list in memory.\n"
            "3. **Dictionaries (`dict`)**: Implemented as open-addressed hash tables with $O(1)$ average time complexity for lookup, insertion, and deletion. Since Python 3.7+, insertion order is guaranteed.\n"
            "4. **Global Interpreter Lock (GIL)**: A mutex in CPython that allows only one native thread to execute Python bytecodes at a time. Use `multiprocessing` for CPU-bound tasks and `asyncio`/`threading` for I/O-bound tasks."
        ),
        "code_example": (
            "def fibonacci_gen(limit: int):\n"
            "    a, b = 0, 1\n"
            "    for _ in range(limit):\n"
            "        yield a\n"
            "        a, b = b, a + b\n\n"
            "print(list(fibonacci_gen(6)))  # [0, 1, 1, 2, 3, 5]"
        ),
        "suggestions": [
            "Explain Python lists vs tuples",
            "How does FastAPI work?",
            "Explain Big-O time complexity",
        ],
    },
    {
        "topic": "FastAPI",
        "keywords": ["fastapi", "pydantic", "uvicorn", "asgi", "apirouter", "dependency injection", "depends", "openapi", "swagger"],
        "exact_words": {"fastapi", "pydantic", "uvicorn", "asgi"},
        "reply": (
            "### FastAPI Architecture & Key Features\n\n"
            "**FastAPI** is a modern, high-performance Python web framework for building APIs based on standard Python type hints.\n\n"
            "- **ASGI & Uvicorn**: Built on Starlette (ASGI), enabling asynchronous request handling (`async def`) and high throughput via Uvicorn.\n"
            "- **Pydantic Validation**: Request bodies, query parameters, and response schemas are automatically validated and serialized using Pydantic models. Invalid payloads immediately return HTTP `422 Unprocessable Entity`.\n"
            "- **Automatic OpenAPI Docs**: Generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) out of the box.\n"
            "- **Modular Routing**: Uses `APIRouter` to organize endpoints cleanly across domain modules (`questions`, `quizzes`, `progress`, `chat`)."
        ),
        "code_example": (
            "from fastapi import FastAPI, HTTPException\n"
            "from pydantic import BaseModel, Field\n\n"
            "app = FastAPI()\n\n"
            "class AttemptInput(BaseModel):\n"
            "    question_id: int = Field(..., ge=1)\n"
            "    status: str\n\n"
            "@app.post('/attempts', status_code=201)\n"
            "def log_attempt(payload: AttemptInput):\n"
            "    return {'saved': True, 'question_id': payload.question_id}"
        ),
        "suggestions": [
            "What are REST API design principles?",
            "Explain HTTP methods GET, POST, PUT, DELETE",
            "How does SQLite compare to MySQL?",
        ],
    },
    {
        "topic": "REST APIs",
        "keywords": ["rest", "restful", "rest api", "rest apis", "stateless", "endpoint", "json", "resource", "api design", "status code", "status codes"],
        "exact_words": {"rest", "restful", "api", "apis", "json", "stateless"},
        "reply": (
            "### REST API Principles & HTTP Status Codes\n\n"
            "**REST (Representational State Transfer)** is an architectural style for designing networked APIs:\n"
            "1. **Statelessness**: Every client request must contain all information necessary to process it; the server stores no client session context between requests.\n"
            "2. **Resource-Based URLs**: Use nouns for resources (`/questions`, `/students/1/progress`) rather than verbs.\n"
            "3. **Uniform Interface & JSON**: Standard representations (JSON) and standard HTTP status codes:\n"
            "   - `200 OK`: Successful read/update.\n"
            "   - `201 Created`: New resource created (`POST /attempts`).\n"
            "   - `400 Bad Request`: Malformed syntax or domain rule violation.\n"
            "   - `404 Not Found`: Resource ID does not exist.\n"
            "   - `422 Unprocessable Entity`: Schema validation failure.\n"
            "   - `500 Internal Server Error`: Unexpected server fault."
        ),
        "code_example": (
            "// Fetch API call from Vanilla JS to FastAPI\n"
            "const res = await fetch('/questions?category=Strings&difficulty=Beginner');\n"
            "if (!res.ok) throw new Error(`HTTP ${res.status}`);\n"
            "const questions = await res.json();"
        ),
        "suggestions": [
            "Explain HTTP methods and idempotency",
            "How does FastAPI validate requests?",
            "How to prevent SQL injection?",
        ],
    },
    {
        "topic": "HTTP Methods",
        "keywords": ["http", "http methods", "get", "post", "put", "patch", "delete", "idempotent", "idempotency", "headers", "request"],
        "exact_words": {"http", "get", "post", "put", "patch", "delete", "idempotent"},
        "reply": (
            "### HTTP Methods & Idempotency\n\n"
            "| Method | Purpose | Request Body | Safe? | Idempotent? |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **GET** | Retrieve resource(s) | No | Yes | Yes |\n"
            "| **POST** | Create new resource / trigger action | Yes | No | **No** |\n"
            "| **PUT** | Replace entire resource | Yes | No | Yes |\n"
            "| **PATCH** | Partially update resource fields | Yes | No | Yes (typically) |\n"
            "| **DELETE** | Remove resource | Optional | No | Yes |\n\n"
            "- **Idempotent**: Making multiple identical requests produces the same server state as making a single request (`GET`, `PUT`, `DELETE` are idempotent; `POST` creates duplicates unless deduplicated)."
        ),
        "code_example": None,
        "suggestions": [
            "What are common HTTP status codes?",
            "Explain REST API principles",
            "How does FastAPI handle POST requests?",
        ],
    },
    {
        "topic": "MySQL and SQLite Concepts",
        "keywords": ["sqlite", "mysql", "sqlite3", "database server", "serverless", "rdbms", "sqlite vs mysql", "difference between mysql and sqlite", "wal"],
        "exact_words": {"sqlite", "mysql", "sqlite3", "rdbms"},
        "reply": (
            "### SQLite vs. MySQL (RDBMS Comparison)\n\n"
            "| Feature | SQLite (`sqlite3`) | MySQL |\n"
            "| :--- | :--- | :--- |\n"
            "| **Architecture** | Serverless, embedded single-file DB (`placement_assistant.db`) | Client-server architecture (`mysqld` daemon) |\n"
            "| **Setup** | Zero configuration; built into Python standard library | Requires server installation, user grants, port binding |\n"
            "| **Concurrency** | File-level locking (readers concurrent with WAL mode; single writer) | Row-level locking (InnoDB) for high multi-user write concurrency |\n"
            "| **Typing** | Dynamic typing with type affinity (`TEXT`, `INTEGER`, `REAL`, `BLOB`) | Strict static column data types (`VARCHAR`, `INT`, `DATETIME`) |\n"
            "| **Best Use Case** | Local apps, embedded systems, prototyping, academic projects, testing | Large-scale distributed web applications with heavy concurrent writes |\n\n"
            "**Note**: Always enable foreign keys in SQLite via `PRAGMA foreign_keys = ON;` because they are disabled by default for backward compatibility."
        ),
        "code_example": (
            "import sqlite3\n\n"
            "conn = sqlite3.connect('placement_assistant.db')\n"
            "conn.row_factory = sqlite3.Row\n"
            "conn.execute('PRAGMA foreign_keys = ON;')\n"
            "# Parameterized query prevents SQL injection\n"
            "row = conn.execute('SELECT * FROM questions WHERE id = ?', (1,)).fetchone()"
        ),
        "suggestions": [
            "Explain SQL JOINs and indexing",
            "What are ACID properties in DBMS?",
            "How do parameterized SQL queries prevent SQL injection?",
        ],
    },
    {
        "topic": "SQL & Database Fundamentals",
        "keywords": [
            "sql", "join", "inner join", "left join", "primary key", "foreign key",
            "index", "indexing", "acid", "normalization", "group by", "having",
            "where", "sql injection", "parameterized", "transaction", "dbms"
        ],
        "exact_words": {"sql", "join", "joins", "acid", "index", "normalization", "dbms"},
        "reply": (
            "### Essential SQL & DBMS Interview Concepts\n\n"
            "1. **JOIN Types**:\n"
            "   - `INNER JOIN`: Returns rows with matching keys in both tables.\n"
            "   - `LEFT JOIN`: Returns all rows from the left table and matched rows from the right table (`NULL` if no match).\n"
            "2. **WHERE vs. HAVING**:\n"
            "   - `WHERE` filters individual rows **before** `GROUP BY` aggregation.\n"
            "   - `HAVING` filters aggregated groups **after** `GROUP BY`.\n"
            "3. **ACID Properties**: **A**tomicity (all-or-nothing), **C**onsistency (valid schema constraints), **I**solation (concurrent transactions don't interfere), **D**urability (committed changes survive crashes).\n"
            "4. **SQL Injection Prevention**: Never use Python f-strings to build SQL queries. Always use parameterized placeholders (`?` in `sqlite3`) so user input is treated strictly as literal data."
        ),
        "code_example": (
            "SELECT q.category,\n"
            "       COUNT(DISTINCT q.id) AS total_questions,\n"
            "       COUNT(DISTINCT a.question_id) AS attempted\n"
            "FROM questions q\n"
            "LEFT JOIN attempts a ON q.id = a.question_id AND a.student_id = ?\n"
            "GROUP BY q.category\n"
            "HAVING COUNT(DISTINCT q.id) > 0;"
        ),
        "suggestions": [
            "Compare SQLite and MySQL",
            "Explain Big-O complexity and hash maps",
            "Tips for technical interviews",
        ],
    },
    {
        "topic": "Data Structures and Algorithms",
        "keywords": [
            "dsa", "algorithm", "algorithms", "data structure", "data structures",
            "big o", "complexity", "time complexity", "space complexity", "binary search",
            "two pointers", "sliding window", "hash map", "hashmap", "stack", "queue",
            "recursion", "dynamic programming", "sorting", "array", "linked list", "tree", "graph"
        ],
        "exact_words": {"dsa", "algorithm", "algorithms", "complexity", "stack", "queue", "recursion", "sorting"},
        "reply": (
            "### High-Yield Data Structures & Algorithms for Placements\n\n"
            "1. **Hash Maps (`dict` / `set`)**: Reduce $O(n^2)$ nested loops to $O(n)$ time for Two-Sum, frequency counting, anagram grouping, and duplicate detection.\n"
            "2. **Two Pointers & Sliding Window**: Ideal for sorted arrays, palindromes, and longest substring/subarray problems in $O(n)$ time and $O(1)$ space.\n"
            "3. **Binary Search**: Whenever the search space is sorted or monotonic, halve the search range each step for $O(\\log n)$ time complexity.\n"
            "4. **Stack & Queue**:\n"
            "   - **Stack (LIFO)**: Use Python `list` (`append`/`pop`) for balanced parentheses, monotonic stacks, and DFS.\n"
            "   - **Queue (FIFO)**: Use `collections.deque` (`append`/`popleft` in $O(1)$) for BFS and level-order traversal.\n"
            "5. **Sorting (`Timsort`)**: Python's `sorted()` and `.sort()` run in $O(n \\log n)$ worst-case time and $O(n)$ space, and are stable."
        ),
        "code_example": (
            "# Two-Sum in O(n) Time using a Hash Map\n"
            "def two_sum(nums: list[int], target: int) -> list[int]:\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        complement = target - num\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[num] = i\n"
            "    return []"
        ),
        "suggestions": [
            "How to approach a coding interview problem?",
            "Explain Python lists vs tuples",
            "Practice questions in the Question Bank",
        ],
    },
    {
        "topic": "Technical Interviews",
        "keywords": [
            "interview", "interviews", "placement", "placements", "hr", "coding round",
            "tips", "preparation", "resume", "project", "explain project", "viva",
            "campus", "crack", "strategy"
        ],
        "exact_words": {"interview", "interviews", "placement", "placements", "viva", "hr", "resume"},
        "reply": (
            "### Technical Interview & Campus Placement Framework\n\n"
            "Use the **UMPIRE** method during live coding interviews:\n"
            "1. **U - Understand**: Clarify input constraints, data types, empty/negative edge cases, and expected output format.\n"
            "2. **M - Match**: Identify the pattern (Hash Map, Two Pointers, Sliding Window, Binary Search, Recursion).\n"
            "3. **P - Plan**: State the brute-force approach first, then explain the optimized algorithm before typing code.\n"
            "4. **I - Implement**: Write clean, modular Python code with meaningful variable names and type hints.\n"
            "5. **R - Review**: Dry-run your code line by line with a small sample input and boundary cases.\n"
            "6. **E - Evaluate**: Explicitly state both **Time Complexity** and **Space Complexity** in Big-O notation.\n\n"
            "**Project Viva Tip**: Be ready to explain how your Frontend (`fetch`), Backend (`FastAPI` routers + `Pydantic`), and Database (`SQLite` parameterized queries) interact end-to-end."
        ),
        "code_example": None,
        "suggestions": [
            "Explain FastAPI architecture",
            "Compare SQLite and MySQL",
            "Top Data Structures & Algorithms patterns",
        ],
    },
]


def get_chatbot_response(user_message: str) -> Dict[str, Any]:
    """
    Match a user query against the rule-based knowledge base using token and phrase scoring.
    Returns a structured response dictionary.
    """
    cleaned = user_message.strip().lower()
    tokens = set(re.findall(r"[a-z0-9_*]+", cleaned))

    best_entry: Optional[Dict[str, Any]] = None
    best_score = 0
    best_matched_keywords: List[str] = []

    for entry in KNOWLEDGE_BASE:
        score = 0
        matched_kw: List[str] = []

        # Exact token match bonus
        for word in entry.get("exact_words", set()):
            if word in tokens:
                score += 4
                if word not in matched_kw:
                    matched_kw.append(word)

        # Phrase / substring match
        for kw in entry["keywords"]:
            if kw in cleaned:
                weight = 5 if " " in kw else 2
                score += weight
                if kw not in matched_kw:
                    matched_kw.append(kw)

        if score > best_score:
            best_score = score
            best_entry = entry
            best_matched_keywords = matched_kw

    if best_entry is None or best_score == 0:
        return {
            "reply": (
                "I couldn't find an exact rule matching that query in my technical knowledge base.\n\n"
                "As a **rule-based technical assistant**, I specialize in:\n"
                "- **Python** (`lists vs tuples`, `decorators`, `generators`, `GIL`, `dict`)\n"
                "- **FastAPI & REST APIs** (`FastAPI`, `Pydantic`, `REST`, `HTTP methods`, `status codes`)\n"
                "- **Databases & SQL** (`SQLite vs MySQL`, `SQL JOINs`, `ACID`, `SQL injection`)\n"
                "- **DSA & Interviews** (`Big O complexity`, `binary search`, `hash map`, `interview tips`)\n\n"
                "Try rephrasing your question using one of the keywords above or click a suggested topic chip below!"
            ),
            "matched_topic": "Unrecognized Query (Fallback)",
            "confidence": "Low (Rule Fallback)",
            "matched_keywords": [],
            "follow_up_suggestions": [
                "Help - Show all supported topics",
                "Explain Python lists vs tuples",
                "Compare SQLite and MySQL",
                "Explain REST APIs and HTTP methods",
                "Top coding interview tips",
            ],
            "code_example": None,
        }

    confidence = "High (Exact Keyword Match)" if best_score >= 5 else "Medium (Keyword Match)"
    return {
        "reply": best_entry["reply"],
        "matched_topic": best_entry["topic"],
        "confidence": confidence,
        "matched_keywords": best_matched_keywords[:5],
        "follow_up_suggestions": best_entry["suggestions"],
        "code_example": best_entry["code_example"],
    }


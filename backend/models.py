"""
Data access layer (models/repository) for Smart Placement Preparation Assistant.
All database queries are parameterized and decoupled from HTTP route handlers.
"""

import json
import random
from typing import Any, Dict, List, Optional
from backend.database import db_session


def get_student_by_id(student_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a student record by ID."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT id, name, email, branch, graduation_year, target_role, created_at FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()
        return dict(row) if row else None


def update_student_profile(
    student_id: int,
    name: str,
    branch: str,
    graduation_year: int,
    target_role: str,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a student's profile details in SQLite."""
    with db_session() as conn:
        existing = conn.execute(
            "SELECT id, email FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()
        if not existing:
            raise LookupError(f"Student with ID {student_id} not found.")

        final_email = (email or existing["email"] or f"student{student_id}@university.edu").strip()
        conn.execute(
            """
            UPDATE students
            SET name = ?, email = ?, branch = ?, graduation_year = ?, target_role = ?
            WHERE id = ?
            """,
            (name, final_email, branch, graduation_year, target_role, student_id),
        )
        updated = conn.execute(
            "SELECT id, name, email, branch, graduation_year, target_role, created_at FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()
        return dict(updated)


def get_all_questions(
    student_id: int = 1,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve questions with dynamic attempt status for the given student."""
    with db_session() as conn:
        query = """
            SELECT
                q.id,
                q.title,
                q.description,
                q.category,
                q.difficulty,
                q.sample_input,
                q.expected_output,
                q.explanation,
                q.starter_code,
                COUNT(a.id) AS attempts_count,
                MAX(CASE WHEN a.status = 'Completed' THEN 2 WHEN a.status = 'Attempted' THEN 1 ELSE 0 END) AS status_rank,
                MAX(a.attempted_at) AS last_attempted_at
            FROM questions q
            LEFT JOIN attempts a ON q.id = a.question_id AND a.student_id = ?
            WHERE 1 = 1
        """
        params: List[Any] = [student_id]

        if category and category.lower() != "all":
            query += " AND LOWER(q.category) = LOWER(?)"
            params.append(category.strip())

        if difficulty and difficulty.lower() != "all":
            query += " AND LOWER(q.difficulty) = LOWER(?)"
            params.append(difficulty.strip())

        if search and search.strip():
            like_term = f"%{search.strip()}%"
            query += " AND (q.title LIKE ? OR q.description LIKE ? OR q.category LIKE ?)"
            params.extend([like_term, like_term, like_term])

        query += " GROUP BY q.id ORDER BY q.id ASC"
        rows = conn.execute(query, params).fetchall()

        results: List[Dict[str, Any]] = []
        for r in rows:
            item = dict(r)
            rank = item.pop("status_rank", 0) or 0
            if rank == 2:
                item["status"] = "Completed"
            elif rank == 1:
                item["status"] = "Attempted"
            else:
                item["status"] = "Not Started"

            if status_filter and status_filter.lower() != "all":
                if item["status"].lower() != status_filter.strip().lower():
                    continue

            results.append(item)
        return results


def get_question_by_id(question_id: int, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Retrieve full details for a single question including latest student attempt."""
    with db_session() as conn:
        row = conn.execute(
            """
            SELECT id, title, description, category, difficulty,
                   sample_input, expected_output, explanation, starter_code
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        ).fetchone()

        if not row:
            return None

        question = dict(row)

        attempts = conn.execute(
            """
            SELECT id, submitted_code, status, notes, time_taken_minutes, attempted_at
            FROM attempts
            WHERE question_id = ? AND student_id = ?
            ORDER BY attempted_at DESC, id DESC
            """,
            (question_id, student_id),
        ).fetchall()

        question["attempts_count"] = len(attempts)
        if attempts:
            has_completed = any(a["status"] == "Completed" for a in attempts)
            question["status"] = "Completed" if has_completed else "Attempted"
            question["latest_code"] = attempts[0]["submitted_code"]
            question["latest_notes"] = attempts[0]["notes"]
            question["last_attempted_at"] = attempts[0]["attempted_at"]
        else:
            question["status"] = "Not Started"
            question["latest_code"] = None
            question["latest_notes"] = None
            question["last_attempted_at"] = None

        return question


def create_attempt(
    student_id: int,
    question_id: int,
    submitted_code: str,
    status: str,
    notes: str,
    time_taken_minutes: int,
) -> Dict[str, Any]:
    """Record a new coding question attempt for a student."""
    with db_session() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise ValueError(f"Student with ID {student_id} not found.")

        question = conn.execute(
            "SELECT id, title, category, difficulty FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()
        if not question:
            raise LookupError(f"Question with ID {question_id} not found.")

        cursor = conn.execute(
            """
            INSERT INTO attempts (student_id, question_id, submitted_code, status, notes, time_taken_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, question_id, submitted_code, status, notes, time_taken_minutes),
        )
        attempt_id = cursor.lastrowid

        row = conn.execute(
            """
            SELECT a.id, a.student_id, a.question_id, q.title AS question_title,
                   q.category, q.difficulty, a.submitted_code, a.status,
                   a.notes, a.time_taken_minutes, a.attempted_at
            FROM attempts a
            JOIN questions q ON a.question_id = q.id
            WHERE a.id = ?
            """,
            (attempt_id,),
        ).fetchone()
        return dict(row)


def list_quizzes(student_id: int = 1) -> List[Dict[str, Any]]:
    """Retrieve all available quizzes with question pool count and student's best score."""
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT
                qz.id,
                qz.title,
                qz.description,
                qz.category,
                qz.difficulty,
                qz.duration_minutes,
                qz.total_questions,
                (SELECT COUNT(*) FROM quiz_questions qq WHERE qq.quiz_id = qz.id) AS available_pool_count,
                (SELECT MAX(qa.percentage) FROM quiz_attempts qa WHERE qa.quiz_id = qz.id AND qa.student_id = ?) AS best_score_percentage,
                (SELECT COUNT(*) FROM quiz_attempts qa WHERE qa.quiz_id = qz.id AND qa.student_id = ?) AS attempts_count
            FROM quizzes qz
            ORDER BY qz.id ASC
            """,
            (student_id, student_id),
        ).fetchall()

        total_pool = conn.execute("SELECT COUNT(*) AS cnt FROM quiz_questions").fetchone()["cnt"]
        result: List[Dict[str, Any]] = []
        for r in rows:
            item = dict(r)
            if item["category"].lower() == "comprehensive" or item["available_pool_count"] == 0:
                item["available_pool_count"] = total_pool
            if item["best_score_percentage"] is not None:
                item["best_score_percentage"] = round(float(item["best_score_percentage"]), 1)
            result.append(item)
        return result


def get_quiz_with_questions(quiz_id: int, limit: Optional[int] = None, randomize: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve a quiz and a randomized subset of its MCQ questions (without exposing correct_option)."""
    with db_session() as conn:
        quiz_row = conn.execute(
            """
            SELECT id, title, description, category, difficulty, duration_minutes, total_questions
            FROM quizzes
            WHERE id = ?
            """,
            (quiz_id,),
        ).fetchone()

        if not quiz_row:
            return None

        quiz = dict(quiz_row)

        # Fetch questions specifically linked to this quiz; if comprehensive quiz, can pull from entire pool
        q_rows = conn.execute(
            """
            SELECT id, quiz_id, question_text, category, difficulty,
                   option_a, option_b, option_c, option_d
            FROM quiz_questions
            WHERE quiz_id = ?
            """,
            (quiz_id,),
        ).fetchall()

        if not q_rows:
            q_rows = conn.execute(
                """
                SELECT id, quiz_id, question_text, category, difficulty,
                       option_a, option_b, option_c, option_d
                FROM quiz_questions
                """
            ).fetchall()

        questions = [dict(r) for r in q_rows]
        if randomize:
            random.shuffle(questions)

        target_count = limit if limit is not None else quiz["total_questions"]
        if target_count and len(questions) > target_count:
            questions = questions[:target_count]

        quiz["questions"] = questions
        quiz["total_questions"] = len(questions)
        return quiz


def submit_quiz_attempt(
    quiz_id: int,
    student_id: int,
    answers: Dict[str, str],
    time_taken_seconds: int,
) -> Dict[str, Any]:
    """Score a submitted quiz attempt, persist to SQLite, and return detailed answer reviews."""
    with db_session() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise ValueError(f"Student with ID {student_id} not found.")

        quiz = conn.execute(
            "SELECT id, title, category FROM quizzes WHERE id = ?",
            (quiz_id,),
        ).fetchone()
        if not quiz:
            raise LookupError(f"Quiz with ID {quiz_id} not found.")

        question_ids = [int(qid) for qid in answers.keys() if str(qid).isdigit()]
        if not question_ids:
            raise ValueError("No valid numeric question IDs provided in answers.")

        placeholders = ",".join(["?"] * len(question_ids))
        q_rows = conn.execute(
            f"""
            SELECT id, question_text, category, difficulty,
                   option_a, option_b, option_c, option_d,
                   correct_option, explanation
            FROM quiz_questions
            WHERE id IN ({placeholders})
            """,
            question_ids,
        ).fetchall()

        if not q_rows:
            raise ValueError("Submitted question IDs do not match any quiz questions in the database.")

        score = 0
        reviews: List[Dict[str, Any]] = []
        q_map = {r["id"]: dict(r) for r in q_rows}

        for qid in question_ids:
            if qid not in q_map:
                continue
            q_data = q_map[qid]
            selected = answers.get(str(qid), "").upper()
            correct = q_data["correct_option"].upper()
            is_correct = selected == correct
            if is_correct:
                score += 1

            reviews.append(
                {
                    "question_id": qid,
                    "question_text": q_data["question_text"],
                    "category": q_data["category"],
                    "difficulty": q_data["difficulty"],
                    "option_a": q_data["option_a"],
                    "option_b": q_data["option_b"],
                    "option_c": q_data["option_c"],
                    "option_d": q_data["option_d"],
                    "selected_option": selected,
                    "correct_option": correct,
                    "is_correct": is_correct,
                    "explanation": q_data["explanation"],
                }
            )

        total_evaluated = len(reviews)
        if total_evaluated == 0:
            raise ValueError("No valid quiz questions evaluated.")

        percentage = round((score / total_evaluated) * 100.0, 2)
        if percentage >= 85:
            grade = "Excellent (Placement Ready)"
        elif percentage >= 70:
            grade = "Good (Strong Foundation)"
        elif percentage >= 50:
            grade = "Fair (Needs Practice)"
        else:
            grade = "Needs Improvement"

        cursor = conn.execute(
            """
            INSERT INTO quiz_attempts (
                student_id, quiz_id, score, total_questions,
                percentage, time_taken_seconds, answers_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                quiz_id,
                score,
                total_evaluated,
                percentage,
                time_taken_seconds,
                json.dumps(answers),
            ),
        )
        attempt_id = cursor.lastrowid
        attempt_row = conn.execute(
            "SELECT attempted_at FROM quiz_attempts WHERE id = ?",
            (attempt_id,),
        ).fetchone()

        return {
            "attempt_id": attempt_id,
            "quiz_id": quiz_id,
            "quiz_title": quiz["title"],
            "student_id": student_id,
            "score": score,
            "total_questions": total_evaluated,
            "percentage": percentage,
            "grade": grade,
            "time_taken_seconds": time_taken_seconds,
            "attempted_at": attempt_row["attempted_at"],
            "reviews": reviews,
        }


def get_quiz_attempt_detail(attempt_id: int) -> Optional[Dict[str, Any]]:
    """Reconstruct full quiz attempt result & question review from a stored quiz_attempts row."""
    with db_session() as conn:
        row = conn.execute(
            """
            SELECT qa.id AS attempt_id, qa.quiz_id, qz.title AS quiz_title,
                   qa.student_id, qa.score, qa.total_questions,
                   qa.percentage, qa.time_taken_seconds, qa.answers_json, qa.attempted_at
            FROM quiz_attempts qa
            JOIN quizzes qz ON qa.quiz_id = qz.id
            WHERE qa.id = ?
            """,
            (attempt_id,),
        ).fetchone()

        if not row:
            return None

        data = dict(row)
        answers: Dict[str, str] = json.loads(data.pop("answers_json", "{}") or "{}")
        question_ids = [int(k) for k in answers.keys() if str(k).isdigit()]

        reviews: List[Dict[str, Any]] = []
        if question_ids:
            placeholders = ",".join(["?"] * len(question_ids))
            q_rows = conn.execute(
                f"""
                SELECT id, question_text, category, difficulty,
                       option_a, option_b, option_c, option_d,
                       correct_option, explanation
                FROM quiz_questions
                WHERE id IN ({placeholders})
                """,
                question_ids,
            ).fetchall()
            q_map = {r["id"]: dict(r) for r in q_rows}
            for qid in question_ids:
                if qid not in q_map:
                    continue
                q_data = q_map[qid]
                selected = answers.get(str(qid), "").upper()
                correct = q_data["correct_option"].upper()
                reviews.append(
                    {
                        "question_id": qid,
                        "question_text": q_data["question_text"],
                        "category": q_data["category"],
                        "difficulty": q_data["difficulty"],
                        "option_a": q_data["option_a"],
                        "option_b": q_data["option_b"],
                        "option_c": q_data["option_c"],
                        "option_d": q_data["option_d"],
                        "selected_option": selected,
                        "correct_option": correct,
                        "is_correct": selected == correct,
                        "explanation": q_data["explanation"],
                    }
                )

        pct = float(data["percentage"])
        if pct >= 85:
            grade = "Excellent (Placement Ready)"
        elif pct >= 70:
            grade = "Good (Strong Foundation)"
        elif pct >= 50:
            grade = "Fair (Needs Practice)"
        else:
            grade = "Needs Improvement"

        data["grade"] = grade
        data["reviews"] = reviews
        return data


def get_student_quiz_history(student_id: int) -> List[Dict[str, Any]]:
    """Retrieve all past quiz attempts for a student ordered most recent first."""
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT
                qa.id AS attempt_id,
                qa.quiz_id,
                qz.title AS quiz_title,
                qz.category,
                qa.score,
                qa.total_questions,
                ROUND(qa.percentage, 1) AS percentage,
                qa.time_taken_seconds,
                qa.attempted_at
            FROM quiz_attempts qa
            JOIN quizzes qz ON qa.quiz_id = qz.id
            WHERE qa.student_id = ?
            ORDER BY qa.attempted_at DESC, qa.id DESC
            """,
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_student_recent_activity(student_id: int, limit: int = 12) -> List[Dict[str, Any]]:
    """Combine coding question attempts and quiz submissions into a unified timeline."""
    with db_session() as conn:
        q_attempts = conn.execute(
            """
            SELECT
                'question_attempt' AS activity_type,
                q.title AS title,
                ('Coding Problem | ' || q.difficulty) AS subtitle,
                a.status AS status_or_score,
                q.category AS category,
                a.attempted_at AS timestamp,
                q.id AS reference_id
            FROM attempts a
            JOIN questions q ON a.question_id = q.id
            WHERE a.student_id = ?
            ORDER BY a.attempted_at DESC, a.id DESC
            LIMIT ?
            """,
            (student_id, limit),
        ).fetchall()

        qz_attempts = conn.execute(
            """
            SELECT
                'quiz_attempt' AS activity_type,
                qz.title AS title,
                ('MCQ Assessment | ' || qa.score || '/' || qa.total_questions || ' Correct') AS subtitle,
                (CAST(ROUND(qa.percentage, 1) AS TEXT) || '%') AS status_or_score,
                qz.category AS category,
                qa.attempted_at AS timestamp,
                qa.id AS reference_id
            FROM quiz_attempts qa
            JOIN quizzes qz ON qa.quiz_id = qz.id
            WHERE qa.student_id = ?
            ORDER BY qa.attempted_at DESC, qa.id DESC
            LIMIT ?
            """,
            (student_id, limit),
        ).fetchall()

        combined = [dict(r) for r in q_attempts] + [dict(r) for r in qz_attempts]
        combined.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return combined[:limit]


def _compute_topic_performance(conn: Any, student_id: int) -> List[Dict[str, Any]]:
    """Compute per-category question completion and MCQ accuracy dynamically."""
    cat_rows = conn.execute(
        """
        SELECT
            q.category,
            COUNT(DISTINCT q.id) AS total_questions,
            COUNT(DISTINCT CASE WHEN a.status IN ('Attempted', 'Completed') THEN q.id END) AS attempted_questions,
            COUNT(DISTINCT CASE WHEN a.status = 'Completed' THEN q.id END) AS completed_questions
        FROM questions q
        LEFT JOIN attempts a ON q.id = a.question_id AND a.student_id = ?
        GROUP BY q.category
        ORDER BY q.category ASC
        """,
        (student_id,),
    ).fetchall()

    # Calculate per-category quiz question accuracy from answers_json
    qa_rows = conn.execute(
        "SELECT answers_json FROM quiz_attempts WHERE student_id = ?",
        (student_id,),
    ).fetchall()

    all_qq_rows = conn.execute(
        "SELECT id, category, correct_option FROM quiz_questions"
    ).fetchall()
    qq_map = {r["id"]: (r["category"], r["correct_option"].upper()) for r in all_qq_rows}

    cat_quiz_totals: Dict[str, List[int]] = {}  # category -> [correct, total]
    for r in qa_rows:
        try:
            ans_map = json.loads(r["answers_json"] or "{}")
        except Exception:
            ans_map = {}
        for qid_str, choice in ans_map.items():
            if not str(qid_str).isdigit():
                continue
            qid = int(qid_str)
            if qid in qq_map:
                cat_name, corr_opt = qq_map[qid]
                if cat_name not in cat_quiz_totals:
                    cat_quiz_totals[cat_name] = [0, 0]
                cat_quiz_totals[cat_name][1] += 1
                if str(choice).upper() == corr_opt:
                    cat_quiz_totals[cat_name][0] += 1

    topic_stats: List[Dict[str, Any]] = []
    for row in cat_rows:
        cat = row["category"]
        total_q = row["total_questions"] or 1
        attempted_q = row["attempted_questions"] or 0
        completed_q = row["completed_questions"] or 0
        completion_rate = round((completed_q / total_q) * 100.0, 1)

        quiz_acc: Optional[float] = None
        if cat in cat_quiz_totals and cat_quiz_totals[cat][1] > 0:
            c_corr, c_tot = cat_quiz_totals[cat]
            quiz_acc = round((c_corr / c_tot) * 100.0, 1)

        if quiz_acc is not None:
            mastery = round((completion_rate * 0.6) + (quiz_acc * 0.4), 1)
        else:
            mastery = completion_rate

        if mastery >= 70:
            status_label = "Strong"
        elif mastery >= 40:
            status_label = "In Progress"
        else:
            status_label = "Needs Focus"

        topic_stats.append(
            {
                "category": cat,
                "total_questions": row["total_questions"],
                "attempted_questions": attempted_q,
                "completed_questions": completed_q,
                "completion_rate": completion_rate,
                "quiz_accuracy": quiz_acc,
                "mastery_score": mastery,
                "status": status_label,
            }
        )

    return topic_stats


def get_dashboard_stats(student_id: int = 1) -> Dict[str, Any]:
    """Calculate dynamic dashboard metrics for the student."""
    student = get_student_by_id(student_id)
    if not student:
        raise LookupError(f"Student with ID {student_id} not found.")

    with db_session() as conn:
        total_questions = conn.execute("SELECT COUNT(*) AS cnt FROM questions").fetchone()["cnt"]

        attempt_summary = conn.execute(
            """
            SELECT
                COUNT(DISTINCT question_id) AS questions_attempted,
                COUNT(DISTINCT CASE WHEN status = 'Completed' THEN question_id END) AS questions_completed,
                COUNT(*) AS total_attempts_logged
            FROM attempts
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        questions_attempted = attempt_summary["questions_attempted"] or 0
        questions_completed = attempt_summary["questions_completed"] or 0
        total_attempts_logged = attempt_summary["total_attempts_logged"] or 0

        quiz_summary = conn.execute(
            """
            SELECT
                COUNT(*) AS quizzes_taken,
                COALESCE(AVG(percentage), 0.0) AS average_quiz_score,
                COALESCE(MAX(percentage), 0.0) AS best_quiz_score
            FROM quiz_attempts
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        quizzes_taken = quiz_summary["quizzes_taken"] or 0
        avg_quiz_score = round(float(quiz_summary["average_quiz_score"] or 0.0), 1)
        best_quiz_score = round(float(quiz_summary["best_quiz_score"] or 0.0), 1)

        question_progress = (questions_completed / total_questions * 100.0) if total_questions > 0 else 0.0
        if quizzes_taken > 0:
            overall_progress = round((question_progress * 0.65) + (avg_quiz_score * 0.35), 1)
        else:
            overall_progress = round(question_progress, 1)

        if overall_progress >= 80:
            readiness_label = "Interview Ready"
        elif overall_progress >= 50:
            readiness_label = "Steady Progress"
        elif overall_progress >= 20:
            readiness_label = "Building Momentum"
        else:
            readiness_label = "Getting Started"

        recent_attempts_rows = conn.execute(
            """
            SELECT a.id, a.student_id, a.question_id, q.title AS question_title,
                   q.category, q.difficulty, a.submitted_code, a.status,
                   a.notes, a.time_taken_minutes, a.attempted_at
            FROM attempts a
            JOIN questions q ON a.question_id = q.id
            WHERE a.student_id = ?
            ORDER BY a.attempted_at DESC, a.id DESC
            LIMIT 6
            """,
            (student_id,),
        ).fetchall()
        recently_attempted = [dict(r) for r in recent_attempts_rows]

        topic_stats = _compute_topic_performance(conn, student_id)
        recommended_topics = sorted(topic_stats, key=lambda t: (t["mastery_score"], t["completed_questions"]))[:4]

        diff_rows = conn.execute(
            """
            SELECT
                q.difficulty,
                COUNT(DISTINCT q.id) AS total,
                COUNT(DISTINCT CASE WHEN a.status = 'Completed' THEN q.id END) AS completed
            FROM questions q
            LEFT JOIN attempts a ON q.id = a.question_id AND a.student_id = ?
            GROUP BY q.difficulty
            """,
            (student_id,),
        ).fetchall()

        difficulty_breakdown: Dict[str, Dict[str, int]] = {
            "Beginner": {"total": 0, "completed": 0},
            "Intermediate": {"total": 0, "completed": 0},
            "Advanced": {"total": 0, "completed": 0},
        }
        for r in diff_rows:
            difficulty_breakdown[r["difficulty"]] = {
                "total": r["total"],
                "completed": r["completed"],
            }

        return {
            "student": student,
            "total_questions": total_questions,
            "questions_attempted": questions_attempted,
            "questions_completed": questions_completed,
            "total_attempts_logged": total_attempts_logged,
            "quizzes_taken": quizzes_taken,
            "average_quiz_score": avg_quiz_score,
            "best_quiz_score": best_quiz_score,
            "overall_progress_percentage": overall_progress,
            "readiness_label": readiness_label,
            "recently_attempted_questions": recently_attempted,
            "recommended_topics": recommended_topics,
            "difficulty_breakdown": difficulty_breakdown,
        }


def get_student_progress_analytics(student_id: int = 1) -> Dict[str, Any]:
    """Calculate comprehensive progress analytics for a student."""
    student = get_student_by_id(student_id)
    if not student:
        raise LookupError(f"Student with ID {student_id} not found.")

    with db_session() as conn:
        total_questions = conn.execute("SELECT COUNT(*) AS cnt FROM questions").fetchone()["cnt"]

        att_row = conn.execute(
            """
            SELECT
                COUNT(DISTINCT question_id) AS attempted,
                COUNT(DISTINCT CASE WHEN status = 'Completed' THEN question_id END) AS completed,
                COALESCE(SUM(time_taken_minutes), 0) AS coding_minutes
            FROM attempts
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        questions_attempted = att_row["attempted"] or 0
        questions_completed = att_row["completed"] or 0
        coding_minutes = att_row["coding_minutes"] or 0
        completion_pct = round((questions_completed / total_questions * 100.0), 1) if total_questions > 0 else 0.0

        qz_row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_quizzes,
                COALESCE(AVG(percentage), 0.0) AS avg_score,
                COALESCE(MAX(percentage), 0.0) AS max_score,
                COALESCE(SUM(time_taken_seconds), 0) AS quiz_seconds
            FROM quiz_attempts
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        total_quizzes = qz_row["total_quizzes"] or 0
        avg_quiz_score = round(float(qz_row["avg_score"] or 0.0), 1)
        highest_quiz_score = round(float(qz_row["max_score"] or 0.0), 1)
        quiz_minutes = round((qz_row["quiz_seconds"] or 0) / 60)
        total_study_minutes = int(coding_minutes + quiz_minutes)

        if total_quizzes > 0:
            readiness = round((completion_pct * 0.6) + (avg_quiz_score * 0.4), 1)
        else:
            readiness = completion_pct

        topic_performance = _compute_topic_performance(conn, student_id)
        sorted_by_mastery = sorted(topic_performance, key=lambda x: x["mastery_score"])
        weak_topics = [t for t in sorted_by_mastery if t["mastery_score"] < 65][:3]
        if not weak_topics:
            weak_topics = sorted_by_mastery[:2]
        strong_topics = [t for t in reversed(sorted_by_mastery) if t["mastery_score"] >= 50][:3]

    quiz_history = get_student_quiz_history(student_id)
    recent_activity = get_student_recent_activity(student_id, limit=12)

    return {
        "student": student,
        "total_questions": total_questions,
        "questions_attempted": questions_attempted,
        "questions_completed": questions_completed,
        "completion_percentage": completion_pct,
        "total_quizzes_taken": total_quizzes,
        "average_quiz_score": avg_quiz_score,
        "highest_quiz_score": highest_quiz_score,
        "total_study_minutes": total_study_minutes,
        "overall_readiness_score": readiness,
        "topic_performance": topic_performance,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "quiz_history": quiz_history,
        "recent_activity": recent_activity,
    }


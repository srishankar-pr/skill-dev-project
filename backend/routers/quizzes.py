"""
Router for interactive MCQ Quizzes:
- GET /quizzes
- GET /quizzes/{quiz_id}
- POST /quizzes/{quiz_id}/submit
- GET /quizzes/attempts/{attempt_id}
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend import models
from backend.schemas import (
    QuizDetailOut,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizSummaryOut,
)

router = APIRouter(tags=["Quizzes"])


@router.get("/quizzes", response_model=List[QuizSummaryOut], status_code=status.HTTP_200_OK)
def get_quizzes(student_id: int = Query(default=1, ge=1)) -> List[QuizSummaryOut]:
    """List all available MCQ quizzes with metadata and student best score."""
    quizzes = models.list_quizzes(student_id=student_id)
    return [QuizSummaryOut(**q) for q in quizzes]


@router.get("/quizzes/attempts/{attempt_id}", response_model=QuizSubmitResponse, status_code=status.HTTP_200_OK)
def get_quiz_attempt_result(attempt_id: int) -> QuizSubmitResponse:
    """Retrieve a previously saved quiz attempt result with full answer reviews."""
    result = models.get_quiz_attempt_detail(attempt_id=attempt_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz attempt with ID {attempt_id} not found.",
        )
    return QuizSubmitResponse(**result)


@router.get("/quizzes/{quiz_id}", response_model=QuizDetailOut, status_code=status.HTTP_200_OK)
def get_quiz(
    quiz_id: int,
    limit: Optional[int] = Query(default=None, ge=1, le=34, description="Number of questions to draw"),
    randomize: bool = Query(default=True, description="Randomize question order"),
) -> QuizDetailOut:
    """Fetch a quiz with randomized MCQ questions ready for taking."""
    quiz = models.get_quiz_with_questions(quiz_id=quiz_id, limit=limit, randomize=randomize)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found.",
        )
    return QuizDetailOut(**quiz)


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmitResponse, status_code=status.HTTP_201_CREATED)
def submit_quiz(quiz_id: int, payload: QuizSubmitRequest) -> QuizSubmitResponse:
    """Evaluate a submitted quiz, save results to SQLite, and return score + question-by-question review."""
    try:
        result = models.submit_quiz_attempt(
            quiz_id=quiz_id,
            student_id=payload.student_id,
            answers=payload.answers,
            time_taken_seconds=payload.time_taken_seconds,
        )
        return QuizSubmitResponse(**result)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


"""
Router for Python Question Bank endpoints:
- GET /questions
- GET /questions/{question_id}
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend import models
from backend.schemas import QuestionOut

router = APIRouter(tags=["Questions"])


@router.get("/questions", response_model=List[QuestionOut], status_code=status.HTTP_200_OK)
def list_questions(
    student_id: int = Query(default=1, ge=1, description="Student ID for status tracking"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
    search: Optional[str] = Query(default=None, description="Search keyword in title or description"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by completion status"),
) -> List[QuestionOut]:
    """Retrieve all Python programming questions with optional filters and student status."""
    questions = models.get_all_questions(
        student_id=student_id,
        category=category,
        difficulty=difficulty,
        search=search,
        status_filter=status_filter,
    )
    return [QuestionOut(**q) for q in questions]


@router.get("/questions/{question_id}", response_model=QuestionOut, status_code=status.HTTP_200_OK)
def get_question_detail(
    question_id: int,
    student_id: int = Query(default=1, ge=1, description="Student ID for attempt status"),
) -> QuestionOut:
    """Retrieve a single programming question by ID with full details and latest attempt."""
    if question_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question ID must be a positive integer.",
        )

    question = models.get_question_by_id(question_id=question_id, student_id=student_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found.",
        )
    return QuestionOut(**question)


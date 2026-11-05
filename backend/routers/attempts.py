"""
Router for recording student coding attempts:
- POST /attempts
"""

from fastapi import APIRouter, HTTPException, status
from backend import models
from backend.schemas import AttemptCreate, AttemptOut

router = APIRouter(tags=["Attempts"])


@router.post("/attempts", response_model=AttemptOut, status_code=status.HTTP_201_CREATED)
def submit_attempt(payload: AttemptCreate) -> AttemptOut:
    """Record a coding question attempt or completion in SQLite."""
    try:
        created = models.create_attempt(
            student_id=payload.student_id,
            question_id=payload.question_id,
            submitted_code=payload.submitted_code,
            status=payload.status,
            notes=payload.notes,
            time_taken_minutes=payload.time_taken_minutes,
        )
        return AttemptOut(**created)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


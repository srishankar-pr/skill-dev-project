"""
Router for Dashboard and Progress Tracking endpoints:
- GET /dashboard/stats
- GET /students/{student_id}/progress
- GET /students/{student_id}/quiz-history
- GET /students/{student_id}/recent-activity
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from backend import models
from backend.schemas import (
    ActivityItem,
    DashboardStatsOut,
    ProgressAnalyticsOut,
    QuizHistoryItem,
    StudentOut,
    StudentUpdate,
)

router = APIRouter(tags=["Progress & Analytics"])


@router.get("/students/{student_id}", response_model=StudentOut, status_code=status.HTTP_200_OK)
def read_student_profile(student_id: int) -> StudentOut:
    """Retrieve student profile details by ID."""
    student = models.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return StudentOut(**student)


@router.put("/students/{student_id}", response_model=StudentOut, status_code=status.HTTP_200_OK)
def update_student_profile_endpoint(student_id: int, payload: StudentUpdate) -> StudentOut:
    """Update student name, branch, graduation year, and target role in SQLite."""
    try:
        updated = models.update_student_profile(
            student_id=student_id,
            name=payload.name,
            branch=payload.branch,
            graduation_year=payload.graduation_year,
            target_role=payload.target_role,
            email=payload.email,
        )
        return StudentOut(**updated)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/dashboard/stats", response_model=DashboardStatsOut, status_code=status.HTTP_200_OK)
def read_dashboard_stats(student_id: int = Query(default=1, ge=1)) -> DashboardStatsOut:
    """Retrieve dynamic dashboard metrics, recent attempts, and recommended topics from SQLite."""
    try:
        stats = models.get_dashboard_stats(student_id=student_id)
        return DashboardStatsOut(**stats)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/students/{student_id}/progress", response_model=ProgressAnalyticsOut, status_code=status.HTTP_200_OK)
def read_student_progress(student_id: int) -> ProgressAnalyticsOut:
    """Retrieve comprehensive student progress analytics, topic breakdown, and weak areas."""
    try:
        analytics = models.get_student_progress_analytics(student_id=student_id)
        return ProgressAnalyticsOut(**analytics)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/students/{student_id}/quiz-history", response_model=List[QuizHistoryItem], status_code=status.HTTP_200_OK)
def read_student_quiz_history(student_id: int) -> List[QuizHistoryItem]:
    """Retrieve all quiz attempts for a specific student."""
    student = models.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    history = models.get_student_quiz_history(student_id=student_id)
    return [QuizHistoryItem(**item) for item in history]


@router.get("/students/{student_id}/recent-activity", response_model=List[ActivityItem], status_code=status.HTTP_200_OK)
def read_student_recent_activity(
    student_id: int,
    limit: int = Query(default=12, ge=1, le=50),
) -> List[ActivityItem]:
    """Retrieve unified recent activity feed (coding attempts + quizzes) for a student."""
    student = models.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    items = models.get_student_recent_activity(student_id=student_id, limit=limit)
    return [ActivityItem(**item) for item in items]


"""
Pydantic schemas for request validation and response serialization.
"""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class StudentOut(BaseModel):
    id: int
    name: str
    email: str
    branch: str
    graduation_year: int
    target_role: str
    created_at: Optional[str] = None


class StudentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    email: Optional[str] = Field(default="student@university.edu", max_length=120)
    branch: str = Field(default="Computer Science", min_length=1, max_length=100)
    graduation_year: int = Field(default=2026, ge=2020, le=2035)
    target_role: str = Field(default="Software Development Engineer", min_length=1, max_length=120)

    @field_validator("name", "branch", "target_role")
    @classmethod
    def strip_text_fields(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned


class QuestionOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    sample_input: str
    expected_output: str
    explanation: str
    starter_code: str = ""
    status: str = "Not Started"
    attempts_count: int = 0
    latest_code: Optional[str] = None
    latest_notes: Optional[str] = None
    last_attempted_at: Optional[str] = None


class AttemptCreate(BaseModel):
    student_id: int = Field(default=1, ge=1, description="Student ID")
    question_id: int = Field(..., ge=1, description="Question ID")
    submitted_code: str = Field(default="", max_length=15000, description="Submitted solution or notes")
    status: Literal["Attempted", "Completed"] = Field(default="Completed")
    notes: str = Field(default="", max_length=2000)
    time_taken_minutes: int = Field(default=10, ge=1, le=600)

    @field_validator("submitted_code")
    @classmethod
    def sanitize_code(cls, v: str) -> str:
        return v.strip()


class AttemptOut(BaseModel):
    id: int
    student_id: int
    question_id: int
    question_title: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    submitted_code: str
    status: str
    notes: str
    time_taken_minutes: int
    attempted_at: str


class QuizSummaryOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    duration_minutes: int
    total_questions: int
    available_pool_count: int = 0
    best_score_percentage: Optional[float] = None
    attempts_count: int = 0


class QuizQuestionPublic(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    category: str
    difficulty: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class QuizDetailOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    duration_minutes: int
    total_questions: int
    questions: List[QuizQuestionPublic]


class QuizSubmitRequest(BaseModel):
    student_id: int = Field(default=1, ge=1)
    answers: Dict[str, str] = Field(..., description="Map of question_id (as str) to selected option (A/B/C/D)")
    time_taken_seconds: int = Field(default=120, ge=0, le=7200)

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("Answers dictionary cannot be empty.")
        normalized: Dict[str, str] = {}
        for q_id, choice in v.items():
            c = str(choice).strip().upper()
            if c not in {"A", "B", "C", "D"}:
                raise ValueError(f"Invalid option '{choice}' for question {q_id}. Must be A, B, C, or D.")
            normalized[str(q_id).strip()] = c
        return normalized


class QuizQuestionReview(BaseModel):
    question_id: int
    question_text: str
    category: str
    difficulty: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    selected_option: Optional[str]
    correct_option: str
    is_correct: bool
    explanation: str


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    student_id: int
    score: int
    total_questions: int
    percentage: float
    grade: str
    time_taken_seconds: int
    attempted_at: str
    reviews: List[QuizQuestionReview]


class QuizHistoryItem(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    category: str
    score: int
    total_questions: int
    percentage: float
    time_taken_seconds: int
    attempted_at: str


class TopicStat(BaseModel):
    category: str
    total_questions: int
    attempted_questions: int
    completed_questions: int
    completion_rate: float
    quiz_accuracy: Optional[float] = None
    mastery_score: float
    status: str


class ActivityItem(BaseModel):
    activity_type: Literal["question_attempt", "quiz_attempt"]
    title: str
    subtitle: str
    status_or_score: str
    category: str
    timestamp: str
    reference_id: int


class DashboardStatsOut(BaseModel):
    student: StudentOut
    total_questions: int
    questions_attempted: int
    questions_completed: int
    total_attempts_logged: int
    quizzes_taken: int
    average_quiz_score: float
    best_quiz_score: float
    overall_progress_percentage: float
    readiness_label: str
    recently_attempted_questions: List[AttemptOut]
    recommended_topics: List[TopicStat]
    difficulty_breakdown: Dict[str, Dict[str, int]]


class ProgressAnalyticsOut(BaseModel):
    student: StudentOut
    total_questions: int
    questions_attempted: int
    questions_completed: int
    completion_percentage: float
    total_quizzes_taken: int
    average_quiz_score: float
    highest_quiz_score: float
    total_study_minutes: int
    overall_readiness_score: float
    topic_performance: List[TopicStat]
    weak_topics: List[TopicStat]
    strong_topics: List[TopicStat]
    quiz_history: List[QuizHistoryItem]
    recent_activity: List[ActivityItem]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User query to the technical assistant")
    student_id: Optional[int] = Field(default=1, ge=1)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Message cannot be blank.")
        return cleaned


class ChatResponse(BaseModel):
    reply: str
    matched_topic: str
    confidence: str
    matched_keywords: List[str]
    follow_up_suggestions: List[str]
    code_example: Optional[str] = None


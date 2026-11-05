"""
Router for Technical Rule-Based Chatbot:
- POST /chat
"""

from fastapi import APIRouter, status
from backend.chatbot import get_chatbot_response
from backend.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["Technical Chatbot"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_assistant(payload: ChatRequest) -> ChatResponse:
    """Process a user query using the modular Python rule-based chatbot engine."""
    result = get_chatbot_response(payload.message)
    return ChatResponse(**result)


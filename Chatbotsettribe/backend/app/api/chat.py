from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.database.models import ChatMessage
from app.rag.chains import answer_question
from app.chatbot.classifier import classify_query
import re

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: str
    sources: list[str] = []
    suggested_actions: list[str] = []
    requires_human: bool = False

def is_greeting(message: str) -> bool:
    normalized = re.sub(r"[^a-z\s]", "", message.lower()).strip()
    return normalized in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if is_greeting(request.message):
        raw_answer = (
            "Hi! I am the SETTribe AI Assistant. "
            "I can help you with courses, internships, fees and careers.  What would you like to know?"
        )
        db_message = ChatMessage(
            session_id=request.session_id,
            question=request.message,
            answer=raw_answer,
            intent="GENERAL_FAQ",
            requires_human=False
        )
        db.add(db_message)
        db.commit()
        return ChatResponse(
            answer=raw_answer,
            intent="GENERAL_FAQ",
            suggested_actions=["View Courses", "Ask About Fees", "Submit Enquiry"]
        )

    intent = classify_query(request.message)
    raw_answer = answer_question(
        request.message,
        request.session_id,
        intent
    )
    
    requires_human = False
    suggested_actions = ["Submit Enquiry"]
    
    if intent in ["HUMAN_SUPPORT", "ENQUIRY_REQUEST", "UNKNOWN"]:
        requires_human = True
        suggested_actions.insert(0, "Talk to Career Advisor")
        
    if "I couldn't find that information" in raw_answer:
        requires_human = True
        raw_answer += "\n\nI want to make sure you get accurate information. This question is better handled by a SETTribe career advisor."
        if "Talk to Career Advisor" not in suggested_actions:
            suggested_actions.insert(0, "Talk to Career Advisor")
            
    if intent in ["COURSE_ENQUIRY", "COURSE_FEE", "COURSE_RECOMMENDATION"]:
        suggested_actions.insert(0, "View Course Details")
        
    # Analytics Tracking
    db_message = ChatMessage(
        session_id=request.session_id,
        question=request.message,
        answer=raw_answer,
        intent=intent,
        requires_human=requires_human
    )
    db.add(db_message)
    db.commit()
        
    return ChatResponse(
        answer=raw_answer,
        intent=intent,
        requires_human=requires_human,
        suggested_actions=suggested_actions,
        sources=[] 
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.database.models import Enquiry, ChatMessage

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_enquiries = db.query(func.count(Enquiry.id)).scalar()
    total_messages = db.query(func.count(ChatMessage.id)).scalar()
    human_handoffs = db.query(func.count(ChatMessage.id)).filter(ChatMessage.requires_human == True).scalar()
    
    # Top intents
    intents = db.query(ChatMessage.intent, func.count(ChatMessage.intent).label("count"))\
                .group_by(ChatMessage.intent).order_by(func.count(ChatMessage.intent).desc()).limit(5).all()
                
    intent_breakdown = [{"intent": i[0], "count": i[1]} for i in intents]

    return {
        "total_enquiries": total_enquiries,
        "total_messages": total_messages,
        "human_handoffs": human_handoffs,
        "intent_breakdown": intent_breakdown
    }

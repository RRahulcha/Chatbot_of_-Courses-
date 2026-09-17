from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.database.models import Enquiry

router = APIRouter(prefix="/api/enquiry", tags=["enquiry"])

class EnquiryCreate(BaseModel):
    name: str
    phone: str
    email: str
    qualification: str = None
    course_interest: str = None
    preference: str = None
    message: str = None

@router.post("/")
def create_enquiry(enquiry: EnquiryCreate, db: Session = Depends(get_db)):
    db_enquiry = Enquiry(
        name=enquiry.name,
        phone=enquiry.phone,
        email=enquiry.email,
        qualification=enquiry.qualification,
        course_interest=enquiry.course_interest,
        preference=enquiry.preference,
        message=enquiry.message
    )
    db.add(db_enquiry)
    db.commit()
    db.refresh(db_enquiry)
    return {"status": "success", "enquiry_id": db_enquiry.id, "message": "Enquiry submitted successfully."}

@router.get("/")
def list_enquiries(db: Session = Depends(get_db)):
    return db.query(Enquiry).all()

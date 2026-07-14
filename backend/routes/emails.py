from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import EmailDraft, Lead, AppSettings
from schemas import EmailGenerateRequest, EmailUpdate, EmailOut
from services.email_service import create_email_for_lead, mark_email_sent

router = APIRouter(prefix="/api/emails", tags=["Emails"])


def to_out(email: EmailDraft) -> EmailOut:
    data = EmailOut.model_validate(email)
    if email.lead:
        data.lead_name = email.lead.full_name
        data.lead_company = email.lead.company
    return data


@router.get("", response_model=list[EmailOut])
def list_emails(
    lead_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(EmailDraft).options(joinedload(EmailDraft.lead))
    if lead_id:
        query = query.filter(EmailDraft.lead_id == lead_id)
    if status:
        query = query.filter(EmailDraft.status == status)
    emails = query.order_by(EmailDraft.created_at.desc()).all()
    return [to_out(e) for e in emails]


@router.post("/generate/{lead_id}", response_model=EmailOut)
async def generate_email(
    lead_id: int,
    payload: EmailGenerateRequest,
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    settings = db.query(AppSettings).first()
    email = await create_email_for_lead(
        db, lead, payload.email_type, settings, previous_email=payload.previous_email
    )
    email = db.query(EmailDraft).options(joinedload(EmailDraft.lead)).filter(EmailDraft.id == email.id).first()
    return to_out(email)


@router.put("/{email_id}", response_model=EmailOut)
def update_email(email_id: int, payload: EmailUpdate, db: Session = Depends(get_db)):
    email = db.query(EmailDraft).options(joinedload(EmailDraft.lead)).filter(EmailDraft.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    data = payload.model_dump(exclude_unset=True)
    mark_sent = data.get("status") == "Sent" and email.status != "Sent"
    for key, value in data.items():
        setattr(email, key, value)
    db.commit()
    if mark_sent:
        email = mark_email_sent(db, email)
        email = db.query(EmailDraft).options(joinedload(EmailDraft.lead)).filter(EmailDraft.id == email_id).first()
    else:
        db.refresh(email)
    return to_out(email)


@router.delete("/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(EmailDraft).filter(EmailDraft.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    db.delete(email)
    db.commit()
    return {"message": "Email deleted"}

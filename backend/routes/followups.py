from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from database import get_db
from models import FollowUp, FollowUpStatus, Lead
from schemas import FollowUpCreate, FollowUpUpdate, FollowUpOut
from utils.date_utils import utcnow, today

router = APIRouter(prefix="/api/followups", tags=["Follow-ups"])


def to_out(item: FollowUp) -> FollowUpOut:
    data = FollowUpOut.model_validate(item)
    if item.lead:
        data.lead_name = item.lead.full_name
        data.lead_company = item.lead.company
        data.lead_score = item.lead.ai_score
        data.lead_classification = item.lead.ai_classification
    return data


def sync_overdue(db: Session):
    for item in db.query(FollowUp).filter(FollowUp.status == FollowUpStatus.PENDING.value).all():
        if item.due_date < today():
            item.status = FollowUpStatus.OVERDUE.value
    db.commit()


@router.get("", response_model=list[FollowUpOut])
def list_followups(
    status: Optional[str] = None,
    upcoming: Optional[bool] = None,
    overdue: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    sync_overdue(db)
    query = db.query(FollowUp).options(joinedload(FollowUp.lead))
    if status:
        query = query.filter(FollowUp.status == status)
    if upcoming:
        query = query.filter(
            FollowUp.status == FollowUpStatus.PENDING.value,
            FollowUp.due_date >= today(),
        )
    if overdue:
        query = query.filter(FollowUp.status == FollowUpStatus.OVERDUE.value)
    items = query.order_by(FollowUp.due_date.asc()).all()
    return [to_out(i) for i in items]


@router.post("", response_model=FollowUpOut)
def create_followup(payload: FollowUpCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == payload.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    item = FollowUp(
        lead_id=payload.lead_id,
        due_date=payload.due_date,
        notes=payload.notes,
        status=FollowUpStatus.OVERDUE.value
        if payload.due_date < today()
        else FollowUpStatus.PENDING.value,
    )
    lead.next_follow_up_date = payload.due_date
    db.add(item)
    db.commit()
    db.refresh(item)
    item = db.query(FollowUp).options(joinedload(FollowUp.lead)).filter(FollowUp.id == item.id).first()
    return to_out(item)


@router.put("/{followup_id}", response_model=FollowUpOut)
def update_followup(followup_id: int, payload: FollowUpUpdate, db: Session = Depends(get_db)):
    item = db.query(FollowUp).options(joinedload(FollowUp.lead)).filter(FollowUp.id == followup_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    if data.get("status") == FollowUpStatus.COMPLETED.value:
        item.completed_at = utcnow()
    if "due_date" in data and item.status != FollowUpStatus.COMPLETED.value:
        item.status = (
            FollowUpStatus.OVERDUE.value
            if data["due_date"] < today()
            else FollowUpStatus.PENDING.value
        )
        if item.lead:
            item.lead.next_follow_up_date = data["due_date"]
    db.commit()
    db.refresh(item)
    return to_out(item)


@router.delete("/{followup_id}")
def delete_followup(followup_id: int, db: Session = Depends(get_db)):
    item = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    db.delete(item)
    db.commit()
    return {"message": "Follow-up deleted"}

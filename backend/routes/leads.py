from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
import io

from database import get_db
from models import Lead, LeadStatus, PipelineActivity, AppSettings
from schemas import LeadCreate, LeadUpdate, LeadOut, LeadListResponse, ImportSummary, MessageOut
from services.csv_service import import_leads_from_csv
from utils.file_utils import leads_to_csv, EXPORT_FIELDS

router = APIRouter(prefix="/api/leads", tags=["Leads"])


def serialize_lead(lead: Lead) -> LeadOut:
    return LeadOut.model_validate(lead)


@router.get("", response_model=LeadListResponse)
def list_leads(
    q: Optional[str] = None,
    status: Optional[str] = None,
    classification: Optional[str] = None,
    lead_source: Optional[str] = None,
    industry: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|ai_score|full_name|company)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Lead).options(joinedload(Lead.qualification))

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Lead.full_name.ilike(like),
                Lead.company.ilike(like),
                Lead.email.ilike(like),
                Lead.requirement.ilike(like),
            )
        )
    if status:
        query = query.filter(Lead.status == status)
    if classification:
        query = query.filter(Lead.ai_classification == classification)
    if lead_source:
        query = query.filter(Lead.lead_source == lead_source)
    if industry:
        query = query.filter(Lead.industry == industry)
    if min_score is not None:
        query = query.filter(Lead.ai_score >= min_score)
    if max_score is not None:
        query = query.filter(Lead.ai_score <= max_score)

    total = query.count()
    sort_col = getattr(Lead, sort_by)
    sort_col = sort_col.desc() if sort_dir == "desc" else sort_col.asc()
    items = (
        query.order_by(sort_col)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return LeadListResponse(
        items=[serialize_lead(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=LeadOut)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    existing = db.query(Lead).filter(Lead.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="A lead with this email already exists")
    data = payload.model_dump()
    data["email"] = data["email"].lower()
    lead = Lead(**data)
    db.add(lead)
    try:
        db.flush()
        db.add(
            PipelineActivity(
                lead_id=lead.id,
                from_status=None,
                to_status=lead.status or LeadStatus.NEW.value,
                note="Lead created",
            )
        )
        db.commit()
        db.refresh(lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A lead with this email already exists")
    return serialize_lead(lead)


@router.get("/export-csv")
def export_leads_csv(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    rows = [{field: getattr(lead, field, None) for field in EXPORT_FIELDS} for lead in leads]
    csv_text = leads_to_csv(rows)
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )


@router.post("/import-csv", response_model=ImportSummary)
async def import_leads_csv(
    file: UploadFile = File(...),
    run_ai: bool = True,
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    content = await file.read()
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="CSV file is empty")
    try:
        content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded")
    settings = db.query(AppSettings).first()
    summary = await import_leads_from_csv(db, content, settings, run_ai=run_ai)
    return ImportSummary(**summary)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = (
        db.query(Lead)
        .options(joinedload(Lead.qualification))
        .filter(Lead.id == lead_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return serialize_lead(lead)


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"]:
        data["email"] = data["email"].lower()
        clash = db.query(Lead).filter(Lead.email == data["email"], Lead.id != lead_id).first()
        if clash:
            raise HTTPException(status_code=409, detail="Another lead already uses this email")
    old_status = lead.status
    for key, value in data.items():
        setattr(lead, key, value)
    if "status" in data and data["status"] != old_status:
        db.add(
            PipelineActivity(
                lead_id=lead.id,
                from_status=old_status,
                to_status=data["status"],
                note="Status updated",
            )
        )
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return serialize_lead(lead)


@router.delete("/{lead_id}", response_model=MessageOut)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return MessageOut(message="Lead deleted")

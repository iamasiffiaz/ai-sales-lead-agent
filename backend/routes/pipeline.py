from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Lead, PipelineActivity, LeadStatus
from schemas import PipelineResponse, PipelineColumn, PipelineMoveRequest, LeadOut

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])

STAGES = [
    LeadStatus.NEW.value,
    LeadStatus.CONTACTED.value,
    LeadStatus.QUALIFIED.value,
    LeadStatus.PROPOSAL_SENT.value,
    LeadStatus.WON.value,
    LeadStatus.LOST.value,
]


@router.get("", response_model=PipelineResponse)
def get_pipeline(db: Session = Depends(get_db)):
    leads = db.query(Lead).options(joinedload(Lead.qualification)).all()
    columns = []
    for status in STAGES:
        stage_leads = [LeadOut.model_validate(l) for l in leads if l.status == status]
        columns.append(PipelineColumn(status=status, leads=stage_leads, count=len(stage_leads)))
    return PipelineResponse(columns=columns)


@router.put("/move-lead/{lead_id}", response_model=LeadOut)
def move_lead(lead_id: int, payload: PipelineMoveRequest, db: Session = Depends(get_db)):
    if payload.status not in STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {STAGES}")
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    old = lead.status
    lead.status = payload.status
    db.add(
        PipelineActivity(
            lead_id=lead.id,
            from_status=old,
            to_status=payload.status,
            note=payload.note or f"Moved from {old} to {payload.status}",
        )
    )
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)

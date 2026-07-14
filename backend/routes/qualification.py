from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Lead, LeadQualification, AppSettings
from schemas import QualificationOut, BulkScoreResponse
from services import ai_service
from services.lead_scoring_service import factors_to_json

router = APIRouter(prefix="/api/qualification", tags=["Qualification"])


def _upsert_qualification(db: Session, lead: Lead, result: dict) -> LeadQualification:
    lead.ai_score = result["score"]
    lead.ai_classification = result["classification"]
    lead.priority = result.get("priority", lead.priority)
    lead.next_action = result["suggested_next_action"]

    qual = db.query(LeadQualification).filter(LeadQualification.lead_id == lead.id).first()
    if not qual:
        qual = LeadQualification(lead_id=lead.id)
        db.add(qual)

    qual.score = result["score"]
    qual.classification = result["classification"]
    qual.reason = result["reason"]
    qual.buyer_intent = result["buyer_intent"]
    qual.budget_fit = result["budget_fit"]
    qual.urgency_level = result["urgency_level"]
    qual.suggested_next_action = result["suggested_next_action"]
    qual.recommended_approach = result["recommended_approach"]
    qual.risk_factors = result["risk_factors"]
    qual.personalization_notes = result["personalization_notes"]
    qual.scoring_factors = factors_to_json(result.get("scoring_factors"))
    db.commit()
    db.refresh(qual)
    return qual


@router.post("/score/{lead_id}", response_model=QualificationOut)
async def score_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    settings = db.query(AppSettings).first()
    result = await ai_service.qualify_lead(lead, settings)
    return _upsert_qualification(db, lead, result)


@router.post("/bulk-score", response_model=BulkScoreResponse)
async def bulk_score(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    settings = db.query(AppSettings).first()
    results = []
    failed = 0
    for lead in leads:
        try:
            result = await ai_service.qualify_lead(lead, settings)
            qual = _upsert_qualification(db, lead, result)
            results.append(qual)
        except Exception:
            failed += 1
    return BulkScoreResponse(scored=len(results), failed=failed, results=results)


@router.get("/{lead_id}", response_model=QualificationOut)
def get_qualification(lead_id: int, db: Session = Depends(get_db)):
    qual = db.query(LeadQualification).filter(LeadQualification.lead_id == lead_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="Qualification not found — score the lead first")
    return qual

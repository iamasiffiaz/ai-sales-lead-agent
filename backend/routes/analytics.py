from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Lead, EmailDraft, FollowUp, FollowUpStatus, Recommendation, PipelineActivity
from schemas import DashboardStats, AnalyticsLeads, AnalyticsPipeline, LeadOut, PipelineActivityOut
from utils.date_utils import today

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    total = len(leads)
    hot = sum(1 for l in leads if l.ai_classification == "Hot")
    warm = sum(1 for l in leads if l.ai_classification == "Warm")
    cold = sum(1 for l in leads if l.ai_classification == "Cold")
    scores = [l.ai_score for l in leads if l.ai_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    follow_ups_due = (
        db.query(FollowUp)
        .filter(FollowUp.status.in_([FollowUpStatus.PENDING.value, FollowUpStatus.OVERDUE.value]))
        .filter(FollowUp.due_date <= today())
        .count()
    )
    emails_generated = db.query(EmailDraft).count()
    won = sum(1 for l in leads if l.status == "Won")
    lost = sum(1 for l in leads if l.status == "Lost")

    statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]
    pipeline_chart = [
        {"status": s, "count": sum(1 for l in leads if l.status == s)} for s in statuses
    ]

    sources: dict[str, int] = {}
    for lead in leads:
        src = lead.lead_source or "Unknown"
        sources[src] = sources.get(src, 0) + 1
    source_breakdown = [{"source": k, "count": v} for k, v in sorted(sources.items(), key=lambda x: -x[1])]

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.is_active.is_(True))
        .order_by(Recommendation.created_at.desc())
        .limit(5)
        .all()
    )
    recent_recommendations = [
        {"id": r.id, "title": r.title, "category": r.category, "content": r.content, "priority": r.priority}
        for r in recs
    ]

    return DashboardStats(
        total_leads=total,
        hot_leads=hot,
        warm_leads=warm,
        cold_leads=cold,
        average_score=avg_score,
        follow_ups_due=follow_ups_due,
        emails_generated=emails_generated,
        won_count=won,
        lost_count=lost,
        pipeline_chart=pipeline_chart,
        source_breakdown=source_breakdown,
        recent_recommendations=recent_recommendations,
    )


@router.get("/leads", response_model=AnalyticsLeads)
def analytics_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).options(joinedload(Lead.qualification)).all()

    by_classification = []
    for label in ["Hot", "Warm", "Cold"]:
        by_classification.append(
            {"name": label, "value": sum(1 for l in leads if l.ai_classification == label)}
        )

    sources: dict[str, int] = {}
    statuses: dict[str, int] = {}
    industry_scores: dict[str, list[int]] = {}
    for lead in leads:
        src = lead.lead_source or "Unknown"
        sources[src] = sources.get(src, 0) + 1
        statuses[lead.status] = statuses.get(lead.status, 0) + 1
        ind = lead.industry or "Unknown"
        if lead.ai_score is not None:
            industry_scores.setdefault(ind, []).append(lead.ai_score)

    by_source = [{"name": k, "value": v} for k, v in sources.items()]
    by_status = [{"name": k, "value": v} for k, v in statuses.items()]
    avg_score_by_industry = [
        {"industry": k, "average_score": round(sum(v) / len(v), 1)}
        for k, v in industry_scores.items()
    ]
    avg_score_by_industry.sort(key=lambda x: x["average_score"], reverse=True)

    top = sorted(
        [l for l in leads if l.ai_score is not None],
        key=lambda l: l.ai_score or 0,
        reverse=True,
    )[:10]

    total_fu = db.query(FollowUp).count()
    completed = db.query(FollowUp).filter(FollowUp.status == FollowUpStatus.COMPLETED.value).count()
    rate = round((completed / total_fu) * 100, 1) if total_fu else 0.0

    return AnalyticsLeads(
        by_classification=by_classification,
        by_source=by_source,
        by_status=by_status,
        avg_score_by_industry=avg_score_by_industry,
        top_high_value_leads=[LeadOut.model_validate(l) for l in top],
        follow_up_completion_rate=rate,
        won_lost_summary={
            "won": sum(1 for l in leads if l.status == "Won"),
            "lost": sum(1 for l in leads if l.status == "Lost"),
        },
    )


@router.get("/pipeline", response_model=AnalyticsPipeline)
def analytics_pipeline(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    stages_order = ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]
    counts = {s: sum(1 for l in leads if l.status == s) for s in stages_order}
    stages = [{"status": s, "count": counts[s]} for s in stages_order]

    conversion_rates = []
    for i in range(len(stages_order) - 2):  # exclude Lost from linear conversion
        current = stages_order[i]
        nxt = stages_order[i + 1]
        c = counts[current]
        n = counts[nxt]
        rate = round((n / c) * 100, 1) if c else 0.0
        conversion_rates.append({"from": current, "to": nxt, "rate": rate})

    activities = (
        db.query(PipelineActivity)
        .order_by(PipelineActivity.created_at.desc())
        .limit(20)
        .all()
    )
    return AnalyticsPipeline(
        stages=stages,
        conversion_rates=conversion_rates,
        recent_activity=[PipelineActivityOut.model_validate(a) for a in activities],
    )

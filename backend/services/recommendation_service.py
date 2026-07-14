from sqlalchemy.orm import Session

from models import Lead, Recommendation, AppSettings
from services import ai_service


def get_active_recommendations(db: Session) -> list[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.is_active.is_(True))
        .order_by(Recommendation.created_at.desc())
        .all()
    )


async def regenerate_recommendations(db: Session) -> list[Recommendation]:
    leads = db.query(Lead).all()
    settings = db.query(AppSettings).first()

    pipeline_data = {}
    for status in ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]:
        pipeline_data[status] = sum(1 for l in leads if l.status == status)

    generated = await ai_service.generate_sales_recommendations(leads, pipeline_data, settings)

    # Deactivate old
    for old in db.query(Recommendation).all():
        old.is_active = False

    created = []
    for item in generated:
        rec = Recommendation(
            title=item["title"],
            category=item["category"],
            content=item["content"],
            priority=item.get("priority", "Medium"),
            is_active=True,
        )
        db.add(rec)
        created.append(rec)

    db.commit()
    for rec in created:
        db.refresh(rec)
    return created

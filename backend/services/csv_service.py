from typing import Any

from sqlalchemy.orm import Session

from models import Lead, LeadQualification, LeadStatus, PipelineActivity
from services import ai_service
from services.lead_scoring_service import factors_to_json
from utils.file_utils import normalize_csv_lead, parse_csv_bytes


async def import_leads_from_csv(
    db: Session,
    content: bytes,
    business_settings,
    run_ai: bool = True,
) -> dict[str, Any]:
    rows = parse_csv_bytes(content)
    successful = 0
    failed = 0
    duplicates = 0
    errors: list[dict[str, Any]] = []
    imported_ids: list[int] = []

    existing_emails = {
        e.lower()
        for (e,) in db.query(Lead.email).all()
        if e
    }

    for row in rows:
        row_number = row.get("_row_number", 0)
        try:
            data = normalize_csv_lead(row)
            if not data["full_name"] or not data["company"] or not data["email"]:
                failed += 1
                errors.append(
                    {
                        "row": row_number,
                        "error": "Missing required fields: name, company, or email",
                    }
                )
                continue
            if data["email"] in existing_emails:
                duplicates += 1
                errors.append({"row": row_number, "error": f"Duplicate email: {data['email']}"})
                continue

            lead = Lead(
                **data,
                status=LeadStatus.NEW.value,
            )
            db.add(lead)
            db.flush()

            db.add(
                PipelineActivity(
                    lead_id=lead.id,
                    from_status=None,
                    to_status=LeadStatus.NEW.value,
                    note="Imported via CSV",
                )
            )

            if run_ai:
                result = await ai_service.qualify_lead(lead, business_settings)
                lead.ai_score = result["score"]
                lead.ai_classification = result["classification"]
                lead.priority = result.get("priority", "Medium")
                lead.next_action = result["suggested_next_action"]
                db.add(
                    LeadQualification(
                        lead_id=lead.id,
                        score=result["score"],
                        classification=result["classification"],
                        reason=result["reason"],
                        buyer_intent=result["buyer_intent"],
                        budget_fit=result["budget_fit"],
                        urgency_level=result["urgency_level"],
                        suggested_next_action=result["suggested_next_action"],
                        recommended_approach=result["recommended_approach"],
                        risk_factors=result["risk_factors"],
                        personalization_notes=result["personalization_notes"],
                        scoring_factors=factors_to_json(result.get("scoring_factors")),
                    )
                )

            existing_emails.add(data["email"])
            imported_ids.append(lead.id)
            successful += 1
        except Exception as exc:
            failed += 1
            errors.append({"row": row_number, "error": str(exc)})

    db.commit()
    return {
        "total_rows": len(rows),
        "successful": successful,
        "failed": failed,
        "duplicates": duplicates,
        "errors": errors[:50],
        "imported_ids": imported_ids,
    }

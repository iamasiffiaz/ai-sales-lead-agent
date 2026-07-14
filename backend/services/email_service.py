from sqlalchemy.orm import Session

from models import EmailDraft, EmailStatus, Lead
from services import ai_service
from utils.date_utils import utcnow


async def create_email_for_lead(
    db: Session,
    lead: Lead,
    email_type: str,
    business_settings,
    previous_email: str | None = None,
) -> EmailDraft:
    if email_type == "Follow-up" and previous_email:
        draft = await ai_service.generate_followup_email(lead, previous_email, business_settings)
    else:
        draft = await ai_service.generate_email_draft(lead, email_type, business_settings)

    email = EmailDraft(
        lead_id=lead.id,
        email_type=email_type,
        subject=draft["subject"],
        body=draft["body"],
        status=EmailStatus.DRAFT.value,
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def mark_email_sent(db: Session, email: EmailDraft) -> EmailDraft:
    email.status = EmailStatus.SENT.value
    email.sent_at = utcnow()
    lead = db.query(Lead).filter(Lead.id == email.lead_id).first()
    if lead:
        lead.last_contacted_at = utcnow()
    db.commit()
    db.refresh(email)
    return email

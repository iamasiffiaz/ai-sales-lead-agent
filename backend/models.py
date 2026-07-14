from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
import enum


class LeadStatus(str, enum.Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL_SENT = "Proposal Sent"
    WON = "Won"
    LOST = "Lost"


class Classification(str, enum.Enum):
    HOT = "Hot"
    WARM = "Warm"
    COLD = "Cold"


class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class EmailType(str, enum.Enum):
    FIRST_OUTREACH = "First Outreach"
    FOLLOW_UP = "Follow-up"
    PROPOSAL_FOLLOW_UP = "Proposal Follow-up"
    RE_ENGAGEMENT = "Re-engagement"
    MEETING_REQUEST = "Meeting Request"


class EmailStatus(str, enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    ARCHIVED = "Archived"


class FollowUpStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    leads: Mapped[list["Lead"]] = relationship(back_populates="owner")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    full_name: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    budget: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    requirement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default=LeadStatus.NEW.value, index=True)
    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    ai_classification: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(20), default=Priority.MEDIUM.value)
    next_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    owner: Mapped[Optional["User"]] = relationship(back_populates="leads")
    qualification: Mapped[Optional["LeadQualification"]] = relationship(
        back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    email_drafts: Mapped[list["EmailDraft"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    follow_ups: Mapped[list["FollowUp"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    pipeline_activities: Mapped[list["PipelineActivity"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class LeadQualification(Base):
    __tablename__ = "lead_qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), unique=True)

    score: Mapped[int] = mapped_column(Integer)
    classification: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(Text)
    buyer_intent: Mapped[str] = mapped_column(String(50))
    budget_fit: Mapped[str] = mapped_column(String(50))
    urgency_level: Mapped[str] = mapped_column(String(50))
    suggested_next_action: Mapped[str] = mapped_column(Text)
    recommended_approach: Mapped[str] = mapped_column(Text)
    risk_factors: Mapped[str] = mapped_column(Text)
    personalization_notes: Mapped[str] = mapped_column(Text)
    scoring_factors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lead: Mapped["Lead"] = relationship(back_populates="qualification")


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)

    email_type: Mapped[str] = mapped_column(String(50))
    subject: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=EmailStatus.DRAFT.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    lead: Mapped["Lead"] = relationship(back_populates="email_drafts")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)

    due_date: Mapped[date] = mapped_column(Date, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=FollowUpStatus.PENDING.value, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship(back_populates="follow_ups")


class PipelineActivity(Base):
    __tablename__ = "pipeline_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)

    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50))
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship(back_populates="pipeline_activities")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default=Priority.MEDIUM.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(255), default="Acme Growth Labs")
    target_industry: Mapped[str] = mapped_column(String(255), default="SaaS, FinTech, B2B Services")
    ideal_customer_profile: Mapped[str] = mapped_column(
        Text,
        default="Series A-C B2B SaaS companies with 20-200 employees seeking sales automation.",
    )
    minimum_budget_preference: Mapped[str] = mapped_column(String(100), default="$5,000+")
    default_follow_up_interval_days: Mapped[int] = mapped_column(Integer, default=3)
    ai_provider: Mapped[str] = mapped_column(String(100), default="OpenAI Compatible")
    api_key_placeholder: Mapped[str] = mapped_column(String(255), default="")
    email_signature: Mapped[str] = mapped_column(
        Text,
        default="Best regards,\nSales Team\nAcme Growth Labs",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

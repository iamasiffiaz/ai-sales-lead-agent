from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Leads ----------
class LeadBase(BaseModel):
    full_name: str
    company: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    budget: Optional[str] = None
    requirement: Optional[str] = None
    lead_source: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "New"
    priority: Optional[str] = "Medium"
    next_follow_up_date: Optional[date] = None
    last_contacted_at: Optional[datetime] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    budget: Optional[str] = None
    requirement: Optional[str] = None
    lead_source: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    ai_score: Optional[int] = None
    ai_classification: Optional[str] = None
    next_action: Optional[str] = None
    next_follow_up_date: Optional[date] = None
    last_contacted_at: Optional[datetime] = None


class QualificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    score: int
    classification: str
    reason: str
    buyer_intent: str
    budget_fit: str
    urgency_level: str
    suggested_next_action: str
    recommended_approach: str
    risk_factors: str
    personalization_notes: str
    scoring_factors: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LeadOut(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ai_score: Optional[int] = None
    ai_classification: Optional[str] = None
    next_action: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    qualification: Optional[QualificationOut] = None


class LeadListResponse(BaseModel):
    items: list[LeadOut]
    total: int
    page: int
    page_size: int


class ImportSummary(BaseModel):
    total_rows: int
    successful: int
    failed: int
    duplicates: int
    errors: list[dict[str, Any]] = []
    imported_ids: list[int] = []


# ---------- Qualification ----------
class QualificationResult(BaseModel):
    score: int
    classification: str
    reason: str
    buyer_intent: str
    budget_fit: str
    urgency_level: str
    suggested_next_action: str
    recommended_approach: str
    risk_factors: str
    personalization_notes: str
    scoring_factors: Optional[dict[str, Any]] = None


class BulkScoreResponse(BaseModel):
    scored: int
    failed: int
    results: list[QualificationOut]


# ---------- Emails ----------
class EmailGenerateRequest(BaseModel):
    email_type: str = "First Outreach"
    previous_email: Optional[str] = None


class EmailUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    email_type: Optional[str] = None


class EmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    email_type: str
    subject: str
    body: str
    status: str
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    lead_name: Optional[str] = None
    lead_company: Optional[str] = None


# ---------- Follow-ups ----------
class FollowUpCreate(BaseModel):
    lead_id: int
    due_date: date
    notes: Optional[str] = None


class FollowUpUpdate(BaseModel):
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    due_date: date
    notes: Optional[str] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    lead_name: Optional[str] = None
    lead_company: Optional[str] = None
    lead_score: Optional[int] = None
    lead_classification: Optional[str] = None


# ---------- Pipeline ----------
class PipelineMoveRequest(BaseModel):
    status: str
    note: Optional[str] = None


class PipelineColumn(BaseModel):
    status: str
    leads: list[LeadOut]
    count: int


class PipelineResponse(BaseModel):
    columns: list[PipelineColumn]


class PipelineActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    from_status: Optional[str] = None
    to_status: str
    note: Optional[str] = None
    created_at: datetime


# ---------- Analytics ----------
class DashboardStats(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    average_score: float
    follow_ups_due: int
    emails_generated: int
    won_count: int
    lost_count: int
    pipeline_chart: list[dict[str, Any]]
    source_breakdown: list[dict[str, Any]]
    recent_recommendations: list[dict[str, Any]]


class AnalyticsLeads(BaseModel):
    by_classification: list[dict[str, Any]]
    by_source: list[dict[str, Any]]
    by_status: list[dict[str, Any]]
    avg_score_by_industry: list[dict[str, Any]]
    top_high_value_leads: list[LeadOut]
    follow_up_completion_rate: float
    won_lost_summary: dict[str, int]


class AnalyticsPipeline(BaseModel):
    stages: list[dict[str, Any]]
    conversion_rates: list[dict[str, Any]]
    recent_activity: list[PipelineActivityOut]


# ---------- Recommendations ----------
class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    content: str
    priority: str
    is_active: bool
    created_at: datetime


# ---------- Settings ----------
class SettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    target_industry: Optional[str] = None
    ideal_customer_profile: Optional[str] = None
    minimum_budget_preference: Optional[str] = None
    default_follow_up_interval_days: Optional[int] = None
    ai_provider: Optional[str] = None
    api_key_placeholder: Optional[str] = None
    email_signature: Optional[str] = None


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str
    target_industry: str
    ideal_customer_profile: str
    minimum_budget_preference: str
    default_follow_up_interval_days: int
    ai_provider: str
    api_key_placeholder: str
    email_signature: str
    updated_at: datetime


class MessageOut(BaseModel):
    message: str
    detail: Optional[Any] = None

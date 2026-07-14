"""OpenAI-compatible AI service with rich mock fallbacks."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from config import get_settings
from services.lead_scoring_service import score_lead


EMAIL_TYPES = [
    "First Outreach",
    "Follow-up",
    "Proposal Follow-up",
    "Re-engagement",
    "Meeting Request",
]


def _lead_dict(lead_data: Any) -> dict[str, Any]:
    if isinstance(lead_data, dict):
        return lead_data
    return {
        "full_name": getattr(lead_data, "full_name", ""),
        "company": getattr(lead_data, "company", ""),
        "email": getattr(lead_data, "email", ""),
        "phone": getattr(lead_data, "phone", None),
        "job_title": getattr(lead_data, "job_title", None),
        "industry": getattr(lead_data, "industry", None),
        "company_size": getattr(lead_data, "company_size", None),
        "budget": getattr(lead_data, "budget", None),
        "requirement": getattr(lead_data, "requirement", None),
        "lead_source": getattr(lead_data, "lead_source", None),
        "website": getattr(lead_data, "website", None),
        "linkedin_url": getattr(lead_data, "linkedin_url", None),
        "notes": getattr(lead_data, "notes", None),
        "status": getattr(lead_data, "status", None),
        "ai_score": getattr(lead_data, "ai_score", None),
        "ai_classification": getattr(lead_data, "ai_classification", None),
    }


def _settings_dict(business_settings: Any) -> dict[str, Any]:
    if not business_settings:
        return {}
    if isinstance(business_settings, dict):
        return business_settings
    return {
        "business_name": getattr(business_settings, "business_name", "Our Company"),
        "target_industry": getattr(business_settings, "target_industry", ""),
        "ideal_customer_profile": getattr(business_settings, "ideal_customer_profile", ""),
        "minimum_budget_preference": getattr(business_settings, "minimum_budget_preference", ""),
        "email_signature": getattr(business_settings, "email_signature", "Best regards"),
    }


async def _chat_completion(messages: list[dict[str, str]], temperature: float = 0.4) -> str | None:
    settings = get_settings()
    if not settings.has_ai_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.chat_model,
                    "messages": messages,
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as exc:
        print(f"[ai_service] Chat completion failed, using mock fallback: {exc}")
        return None


def _extract_json(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
    return None


def generate_mock_qualification(lead_data: dict[str, Any], business_settings: dict[str, Any] | None = None) -> dict[str, Any]:
    return score_lead(lead_data, business_settings)


def generate_mock_email(
    lead_data: dict[str, Any],
    email_type: str,
    business_settings: dict[str, Any] | None = None,
) -> dict[str, str]:
    settings = business_settings or {}
    business = settings.get("business_name") or "QualifyAI"
    signature = settings.get("email_signature") or f"Best regards,\n{business} Sales Team"
    first = (lead_data.get("full_name") or "there").split()[0]
    company = lead_data.get("company") or "your team"
    industry = lead_data.get("industry") or "your industry"
    requirement = lead_data.get("requirement") or "improving pipeline quality and response speed"
    title = lead_data.get("job_title") or "leader"
    budget = lead_data.get("budget") or "your current budget range"
    source = lead_data.get("lead_source") or "your recent inquiry"
    classification = lead_data.get("ai_classification") or "Warm"
    score = lead_data.get("ai_score")

    cta = (
        "Are you free for a 15-minute walkthrough tomorrow or Thursday?"
        if classification == "Hot"
        else "Worth a short call this week — or would a one-pager be better for now?"
        if classification == "Warm"
        else "Happy to send a short checklist you can keep on file for later."
    )

    proof = (
        f"For {industry} teams with budgets around {budget}, {business} typically surfaces "
        f"Hot leads in the first scoring pass and cuts manual triage time dramatically."
    )

    templates = {
        "First Outreach": {
            "subject": f"{first} — idea for {company}'s {industry} qualification workflow",
            "body": (
                f"Hi {first},\n\n"
                f"Saw your note via {source} about {requirement}. As {title} at {company}, "
                f"you're probably balancing speed-to-lead with SDR capacity.\n\n"
                f"{proof}\n\n"
                f"{cta}\n\n"
                f"{signature}"
            ),
        },
        "Follow-up": {
            "subject": f"Re: {company} — prioritizing the right {industry} opportunities",
            "body": (
                f"Hi {first},\n\n"
                f"Quick follow-up on helping {company} move faster on {requirement}. "
                f"I know calendars get noisy — here's the short version:\n\n"
                f"• Score inbound by budget, urgency, and title fit\n"
                f"• Auto-draft outreach that cites the prospect's actual pain\n"
                f"• Keep next follow-up dates visible on the pipeline\n\n"
                f"{cta}\n\n"
                f"{signature}"
            ),
        },
        "Proposal Follow-up": {
            "subject": f"{company} proposal — decision blockers?",
            "body": (
                f"Hi {first},\n\n"
                f"Following up on the proposal for {company}. It maps to {requirement} with "
                f"phased rollout and clear scorecards your team can run weekly.\n\n"
                f"Commercial context we assumed: ~{budget}. If stakeholders need a narrower pilot "
                f"or revised timeline, tell me what would make this a yes this quarter.\n\n"
                f"{signature}"
            ),
        },
        "Re-engagement": {
            "subject": f"{first}, still battling messy {industry} inbound?",
            "body": (
                f"Hi {first},\n\n"
                f"Reconnecting about {company}. If lead prioritization and follow-up discipline "
                f"are still on the roadmap, we shipped CSV re-score + AI insights that help "
                f"{industry} teams revive dormant opportunities without expanding headcount.\n\n"
                f"{cta}\n\n"
                f"{signature}"
            ),
        },
        "Meeting Request": {
            "subject": f"15 min — {company} scorecard walkthrough",
            "body": (
                f"Hi {first},\n\n"
                f"I'd like 15 minutes to show how {business} would score leads like yours "
                f"(classification: {classification}"
                f"{f', score {score}' if score else ''}) and draft outreach tied to "
                f"{requirement}.\n\n"
                f"I'll bring a sample ICP scorecard for {industry} accounts near {budget}. "
                f"Does Tuesday or Thursday afternoon work?\n\n"
                f"{signature}"
            ),
        },
    }
    return templates.get(email_type, templates["First Outreach"])


def generate_mock_recommendations(
    leads: list[dict[str, Any]],
    pipeline_data: dict[str, Any] | None = None,
    business_settings: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    from datetime import date

    today = date.today()
    hot = [l for l in leads if l.get("ai_classification") == "Hot" or (l.get("ai_score") or 0) >= 75]
    warm = [l for l in leads if l.get("ai_classification") == "Warm" or 45 <= (l.get("ai_score") or 0) < 75]
    cold = [l for l in leads if l.get("ai_classification") == "Cold" or (l.get("ai_score") or 0) < 45]

    overdue = []
    for lead in leads:
        due = lead.get("next_follow_up_date")
        if not due:
            continue
        try:
            due_date = due if hasattr(due, "year") else date.fromisoformat(str(due)[:10])
            if due_date < today and lead.get("status") not in ("Won", "Lost"):
                overdue.append(lead)
        except Exception:
            continue

    by_industry: dict[str, list[int]] = {}
    for lead in leads:
        ind = lead.get("industry") or "Unknown"
        if lead.get("ai_score") is not None:
            by_industry.setdefault(ind, []).append(lead["ai_score"])
    industry_avg = sorted(
        ((k, sum(v) / len(v), len(v)) for k, v in by_industry.items() if v),
        key=lambda x: x[1],
        reverse=True,
    )
    top_industry, top_avg, top_n = industry_avg[0] if industry_avg else ("SaaS", 0, 0)

    hot_sorted = sorted(hot, key=lambda x: x.get("ai_score") or 0, reverse=True)
    hot_names = ", ".join(f"{l.get('full_name')} ({l.get('company')})" for l in hot_sorted[:3]) or "none yet"
    overdue_names = ", ".join(f"{l.get('full_name')}" for l in overdue[:3]) or "none"

    pipeline = pipeline_data or {}
    proposal = pipeline.get("Proposal Sent", sum(1 for l in leads if l.get("status") == "Proposal Sent"))
    qualified = pipeline.get("Qualified", sum(1 for l in leads if l.get("status") == "Qualified"))
    contacted = pipeline.get("Contacted", sum(1 for l in leads if l.get("status") == "Contacted"))
    new_count = pipeline.get("New", sum(1 for l in leads if l.get("status") == "New"))
    won = pipeline.get("Won", sum(1 for l in leads if l.get("status") == "Won"))
    lost = pipeline.get("Lost", sum(1 for l in leads if l.get("status") == "Lost"))

    settings = business_settings or {}
    icp = settings.get("target_industry") or "your ICP industries"

    return [
        {
            "title": "Contact Hot leads first",
            "category": "Priority Outreach",
            "content": (
                f"{len(hot)} Hot lead(s) deserve same-day outreach. Start with: {hot_names}. "
                f"Book discovery calls within 24 hours while intent is fresh — protect calendar "
                f"from Cold volume ({len(cold)} accounts)."
            ),
            "priority": "High",
        },
        {
            "title": "Clear overdue follow-ups",
            "category": "Follow-up",
            "content": (
                f"{len(overdue)} lead(s) are past their next follow-up date"
                f"{f' (including {overdue_names})' if overdue else ''}. "
                f"Close or reschedule before adding net-new outbound. Warm book size: {len(warm)}."
            ),
            "priority": "High",
        },
        {
            "title": f"{top_industry} outperforms other industries",
            "category": "Industry Insight",
            "content": (
                f"{top_industry} averages {top_avg:.0f}/100 across {top_n} lead(s). "
                f"Double down on channels feeding that segment this week. ICP focus: {icp}."
            ),
            "priority": "Medium",
        },
        {
            "title": "Advance mid-funnel opportunities",
            "category": "Conversion",
            "content": (
                f"Pipeline snapshot — New {new_count}, Contacted {contacted}, Qualified {qualified}, "
                f"Proposal Sent {proposal}. Push the {proposal} open proposal(s) to a decision meeting "
                f"with ROI proof and a clear yes/no ask."
            ),
            "priority": "Medium",
        },
        {
            "title": "Two-track sales motion",
            "category": "Strategy",
            "content": (
                "Track A (Hot): meeting CTA + same-day personalization. "
                "Track B (Warm): case study + light audit offer within 48 hours. "
                "Track C (Cold): quarterly re-engagement CSV batch — do not burn SDR hours."
            ),
            "priority": "Medium",
        },
        {
            "title": "Tighten pipeline hygiene",
            "category": "Pipeline",
            "content": (
                f"Won {won} / Lost {lost}. Require a next follow-up date before moving past Contacted, "
                f"and define exit criteria for Qualified → Proposal Sent. Recycle stalled Cold cards "
                f"monthly instead of leaving them to clog the board."
            ),
            "priority": "Low",
        },
    ]


async def qualify_lead(lead_data: Any, business_settings: Any = None) -> dict[str, Any]:
    lead = _lead_dict(lead_data)
    settings = _settings_dict(business_settings)
    base = generate_mock_qualification(lead, settings)

    prompt = (
        "You are a senior B2B sales qualification analyst. "
        "Given lead JSON and business ICP settings, refine the qualification. "
        "Return JSON with keys: score (1-100), classification (Hot|Warm|Cold), reason, "
        "buyer_intent, budget_fit, urgency_level, suggested_next_action, "
        "recommended_approach, risk_factors, personalization_notes. "
        "Hot=75-100, Warm=45-74, Cold=1-44. Be specific and business-focused."
    )
    content = await _chat_completion(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {"lead": lead, "business_settings": settings, "rules_based_baseline": base},
                    default=str,
                ),
            },
        ]
    )
    if not content:
        return base
    parsed = _extract_json(content)
    if not parsed:
        return base

    try:
        score = int(parsed.get("score", base["score"]))
        score = max(1, min(100, score))
        classification = parsed.get("classification") or (
            "Hot" if score >= 75 else "Warm" if score >= 45 else "Cold"
        )
        return {
            "score": score,
            "classification": classification,
            "reason": parsed.get("reason") or base["reason"],
            "buyer_intent": parsed.get("buyer_intent") or base["buyer_intent"],
            "budget_fit": parsed.get("budget_fit") or base["budget_fit"],
            "urgency_level": parsed.get("urgency_level") or base["urgency_level"],
            "suggested_next_action": parsed.get("suggested_next_action") or base["suggested_next_action"],
            "recommended_approach": parsed.get("recommended_approach") or base["recommended_approach"],
            "risk_factors": parsed.get("risk_factors") or base["risk_factors"],
            "personalization_notes": parsed.get("personalization_notes") or base["personalization_notes"],
            "scoring_factors": base.get("scoring_factors"),
            "priority": "High" if score >= 75 else "Medium" if score >= 45 else "Low",
        }
    except Exception:
        return base


async def generate_email_draft(
    lead_data: Any,
    email_type: str,
    business_settings: Any = None,
) -> dict[str, str]:
    lead = _lead_dict(lead_data)
    settings = _settings_dict(business_settings)
    mock = generate_mock_email(lead, email_type, settings)

    content = await _chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "You write concise, personalized B2B sales emails. "
                    "Return JSON with subject and body. Include personalized opening, value proposition, "
                    "relevant solution angle, CTA, and professional closing. No fluff."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"lead": lead, "email_type": email_type, "business_settings": settings},
                    default=str,
                ),
            },
        ],
        temperature=0.6,
    )
    if not content:
        return mock
    parsed = _extract_json(content)
    if not parsed or "subject" not in parsed or "body" not in parsed:
        return mock
    return {"subject": parsed["subject"], "body": parsed["body"]}


async def generate_followup_email(
    lead_data: Any,
    previous_email: str | None,
    business_settings: Any = None,
) -> dict[str, str]:
    lead = _lead_dict(lead_data)
    settings = _settings_dict(business_settings)
    mock = generate_mock_email(lead, "Follow-up", settings)
    if previous_email:
        mock["body"] = (
            mock["body"].split("\n\n")[0]
            + f"\n\nPreviously we discussed:\n---\n{previous_email[:500]}\n---\n\n"
            + "\n\n".join(mock["body"].split("\n\n")[1:])
        )

    content = await _chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "Write a short B2B follow-up email that references prior outreach. "
                    "Return JSON with subject and body."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "lead": lead,
                        "previous_email": previous_email,
                        "business_settings": settings,
                    },
                    default=str,
                ),
            },
        ],
        temperature=0.55,
    )
    if not content:
        return mock
    parsed = _extract_json(content)
    if not parsed:
        return mock
    return {"subject": parsed.get("subject", mock["subject"]), "body": parsed.get("body", mock["body"])}


async def generate_sales_recommendations(
    leads: list[Any],
    pipeline_data: Any = None,
    business_settings: Any = None,
) -> list[dict[str, str]]:
    lead_dicts = [_lead_dict(l) for l in leads]
    settings = _settings_dict(business_settings)
    mock = generate_mock_recommendations(lead_dicts, pipeline_data, settings)

    content = await _chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are a sales operations coach. Return JSON {\"recommendations\": ["
                    "{\"title\",\"category\",\"content\",\"priority\"}] } with 6 actionable items "
                    "covering contact priority, follow-ups, industry performance, conversion, strategy, and pipeline tips."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "leads_sample": lead_dicts[:40],
                        "pipeline_data": pipeline_data,
                        "business_settings": settings,
                    },
                    default=str,
                ),
            },
        ],
        temperature=0.5,
    )
    if not content:
        return mock
    parsed = _extract_json(content)
    if not parsed:
        return mock
    recs = parsed.get("recommendations") or parsed.get("items")
    if not isinstance(recs, list) or not recs:
        return mock
    cleaned = []
    for rec in recs[:8]:
        cleaned.append(
            {
                "title": rec.get("title", "Recommendation"),
                "category": rec.get("category", "General"),
                "content": rec.get("content", ""),
                "priority": rec.get("priority", "Medium"),
            }
        )
    return cleaned or mock

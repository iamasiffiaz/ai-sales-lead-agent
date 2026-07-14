"""Rules-based hybrid lead scoring engine with explainable factors."""

from __future__ import annotations

import json
import re
from typing import Any


DECISION_MAKER_TITLES = [
    "ceo", "cto", "cfo", "coo", "cmo", "cro", "founder", "co-founder", "owner",
    "president", "vp ", "vp of", "vice president", "director", "head of", "chief",
    "managing partner", "general manager",
]

INFLUENCER_TITLES = ["manager", "lead", "senior", "specialist", "ops"]

URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "this week", "this month", "need now",
    "quickly", "deadline", "q1", "q2", "q3", "q4", "budget approved", "ready to buy",
    "this quarter", "30 days", "end of month",
]

SOURCE_WEIGHTS = {
    "inbound demo": 11,
    "referral": 10,
    "partner": 9,
    "website form": 8,
    "webinar": 7,
    "event": 6,
    "content download": 6,
    "linkedin": 5,
    "ads": 3,
    "outbound": 3,
    "cold email": 2,
}

BUDGET_PATTERNS = [
    (r"\$?\s*1[0-9]{2,}k|\$?\s*[2-9][0-9]{2,}k|\$?\s*1m|\$1,?000,?000|100k\+", 16),
    (r"\$?\s*(5[0-9]|[6-9][0-9])k|\$?\s*5[0-9],?000|\$?\s*[6-9][0-9],?000", 14),
    (r"\$?\s*(2[5-9]|[3-4][0-9])k|\$?\s*2[5-9],?000|\$?\s*[3-4][0-9],?000", 11),
    (r"\$?\s*(1[0-9]|2[0-4])k|\$?\s*1[0-9],?000|\$?\s*2[0-4],?000", 8),
    (r"\$?\s*[5-9]k|\$?\s*[5-9],?000", 5),
    (r"enterprise|flexible|open budget|approved", 10),
]


def _clamp(score: int, low: int = 1, high: int = 100) -> int:
    return max(low, min(high, score))


def _parse_budget_amount(text: str) -> float | None:
    if not text:
        return None
    t = text.lower().replace(",", "")
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*k", t)
    if m:
        return float(m.group(1)) * 1000
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*m", t)
    if m:
        return float(m.group(1)) * 1_000_000
    m = re.search(r"\$\s*(\d+(?:\.\d+)?)", t)
    if m:
        return float(m.group(1))
    return None


def _min_budget_from_settings(settings: dict[str, Any]) -> float | None:
    pref = (settings.get("minimum_budget_preference") or "").strip()
    if not pref:
        return None
    return _parse_budget_amount(pref) or 10000.0


def _title_score(job_title: str | None) -> tuple[int, str]:
    if not job_title:
        return 2, "No job title provided — buyer authority unknown"
    title = f" {job_title.lower()} "
    if any(f" {t} " in title or title.strip().startswith(t) for t in DECISION_MAKER_TITLES):
        return 12, f"Decision-maker / economic buyer signal ({job_title})"
    if any(t in title for t in INFLUENCER_TITLES):
        return 6, f"Influencer-level contact ({job_title}) — map champion to economic buyer"
    return 3, f"Individual contributor ({job_title}) — needs multi-threading"


def _budget_score(budget: str | None, settings: dict[str, Any] | None = None) -> tuple[int, str]:
    settings = settings or {}
    if not budget:
        return 1, "Budget not disclosed — qualify commercial fit early"
    text = budget.lower()
    if any(w in text for w in ["unknown", "n/a", "none", "free", "low / n/a", "low"]):
        return 1, f"Weak budget posture ({budget})"

    points = 4
    reason = f"Budget mentioned ({budget})"
    for pattern, pts in BUDGET_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            points = pts
            reason = f"Commercial signal: {budget}"
            break

    min_pref = _min_budget_from_settings(settings)
    amount = _parse_budget_amount(budget)
    if min_pref and amount is not None:
        if amount >= min_pref:
            points = min(16, points + 2)
            reason += f"; meets ICP floor (~${int(min_pref):,}+)"
        elif amount < min_pref * 0.5:
            points = max(1, points - 4)
            reason += f"; below ICP budget preference (~${int(min_pref):,})"
        else:
            points = max(1, points - 1)
            reason += "; near lower end of ICP budget"

    return points, reason


def _urgency_score(requirement: str | None, notes: str | None) -> tuple[int, str]:
    text = f"{requirement or ''} {notes or ''}".lower()
    if not text.strip():
        return 1, "No timing cues in requirement/notes"
    hits = [k for k in URGENT_KEYWORDS if k in text]
    if len(hits) >= 2:
        return 12, f"High urgency language: {', '.join(hits[:3])}"
    if hits:
        return 8, f"Urgency cue present: {hits[0]}"
    if any(w in text for w in ["exploring", "researching", "someday", "next year", "maybe", "free tools"]):
        return 1, "Exploratory timing — nurture, don't over-invest"
    return 4, "Moderate timing — confirm quarter goal on discovery call"


def _requirement_score(requirement: str | None) -> tuple[int, str]:
    if not requirement:
        return 1, "Requirement blank — discovery needed before demo"
    length = len(requirement.strip())
    if length > 120:
        return 10, "Clear, detailed problem statement"
    if length > 40:
        return 7, "Solid requirement; tighten success metrics"
    return 3, "Brief requirement — probe pain, timeline, and stakeholders"


def _company_size_score(company_size: str | None) -> tuple[int, str]:
    if not company_size:
        return 2, "Company size unknown"
    text = company_size.lower().replace(",", "")
    if any(x in text for x in ["200", "500", "1000", "enterprise", "1000+", "201-500", "500+"]):
        return 8, f"Larger account potential ({company_size})"
    if any(x in text for x in ["50", "100", "51-200", "11-50", "20-200"]):
        return 7, f"Strong mid-market fit ({company_size})"
    if any(x in text for x in ["1-10", "startup", "solo"]):
        return 2, f"Early-stage size ({company_size}) — validate budget reality"
    return 4, f"Company size noted ({company_size})"


def _industry_score(industry: str | None, target_industry: str | None) -> tuple[int, str]:
    if not industry:
        return 1, "Industry not specified"
    if not target_industry:
        return 4, f"Industry present: {industry}"
    targets = [t.strip().lower() for t in re.split(r"[,/;|]", target_industry) if t.strip()]
    industry_l = industry.lower()
    if any(t in industry_l or industry_l in t for t in targets):
        return 10, f"Strong ICP industry fit ({industry})"
    related = ["saas", "software", "tech", "fintech", "b2b", "agency", "ecommerce", "hr"]
    if any(r in industry_l for r in related):
        return 5, f"Adjacent GTM market ({industry})"
    return 2, f"Outside core ICP ({industry}) — only pursue if budget is exceptional"


def _source_score(lead_source: str | None) -> tuple[int, str]:
    if not lead_source:
        return 1, "Source unknown — attribution gap"
    key = lead_source.lower().strip()
    for name, points in SOURCE_WEIGHTS.items():
        if name in key:
            return points, f"Source quality: {lead_source} (+{points})"
    return 3, f"Source recorded: {lead_source}"


def _engagement_score(notes: str | None, linkedin_url: str | None, website: str | None) -> tuple[int, str]:
    points = 0
    reasons = []
    if notes and len(notes) > 30:
        points += 4
        reasons.append("Useful engagement notes")
    if linkedin_url:
        points += 2
        reasons.append("LinkedIn available for multi-thread")
    if website:
        points += 1
        reasons.append("Website context available")
    if not reasons:
        return 0, "Thin engagement context"
    return min(points, 7), "; ".join(reasons)


def classify_score(score: int) -> str:
    if score >= 75:
        return "Hot"
    if score >= 45:
        return "Warm"
    return "Cold"


def priority_from_score(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def score_lead(lead_data: dict[str, Any], business_settings: dict[str, Any] | None = None) -> dict[str, Any]:
    """Hybrid rules-based score with explainable factor breakdown."""
    settings = business_settings or {}
    factors: dict[str, Any] = {}
    total = 5  # baseline presence

    t_pts, t_reason = _title_score(lead_data.get("job_title"))
    factors["decision_maker"] = {"points": t_pts, "reason": t_reason}
    total += t_pts

    b_pts, b_reason = _budget_score(lead_data.get("budget"), settings)
    factors["budget"] = {"points": b_pts, "reason": b_reason}
    total += b_pts

    u_pts, u_reason = _urgency_score(lead_data.get("requirement"), lead_data.get("notes"))
    factors["urgency"] = {"points": u_pts, "reason": u_reason}
    total += u_pts

    r_pts, r_reason = _requirement_score(lead_data.get("requirement"))
    factors["requirement_clarity"] = {"points": r_pts, "reason": r_reason}
    total += r_pts

    c_pts, c_reason = _company_size_score(lead_data.get("company_size"))
    factors["company_size"] = {"points": c_pts, "reason": c_reason}
    total += c_pts

    i_pts, i_reason = _industry_score(lead_data.get("industry"), settings.get("target_industry"))
    factors["industry_fit"] = {"points": i_pts, "reason": i_reason}
    total += i_pts

    s_pts, s_reason = _source_score(lead_data.get("lead_source"))
    factors["lead_source"] = {"points": s_pts, "reason": s_reason}
    total += s_pts

    e_pts, e_reason = _engagement_score(
        lead_data.get("notes"), lead_data.get("linkedin_url"), lead_data.get("website")
    )
    factors["engagement"] = {"points": e_pts, "reason": e_reason}
    total += e_pts

    score = _clamp(total)
    classification = classify_score(score)

    buyer_intent = "High" if score >= 75 else "Medium" if score >= 45 else "Low"
    budget_fit = "Strong" if b_pts >= 11 else "Moderate" if b_pts >= 5 else "Weak"
    urgency_level = "High" if u_pts >= 8 else "Medium" if u_pts >= 4 else "Low"

    ranked = sorted(factors.items(), key=lambda x: x[1]["points"], reverse=True)
    top = ranked[:3]
    weak = [item for item in ranked if item[1]["points"] <= 3][:2]

    name = lead_data.get("full_name") or "This lead"
    company = lead_data.get("company") or "the company"
    industry = lead_data.get("industry") or "their market"
    title = lead_data.get("job_title") or "a contact"
    source = lead_data.get("lead_source") or "unknown source"
    budget = lead_data.get("budget") or "undisclosed budget"

    top_bits = [
        f"{k.replace('_', ' ')} ({v['points']} pts) — {v['reason']}" for k, v in top
    ]
    reason = (
        f"{name} ({title}) at {company} scores {score}/100 → {classification}. "
        f"Top drivers: {'; '.join(top_bits)}. "
        f"Channel: {source}. Budget signal: {budget}. Industry context: {industry}."
    )
    if weak:
        weak_bits = [f"{k.replace('_', ' ')} — {v['reason']}" for k, v in weak]
        reason += " Watch-outs: " + "; ".join(weak_bits) + "."

    if score >= 75:
        next_action = (
            f"Book a discovery call with {name.split()[0]} within 24 hours; bring a one-page ROI "
            f"tied to {industry} and confirm budget/timeline on the call."
        )
        approach = (
            "Consultative close: lead with outcome metrics, multi-thread to economic buyer if needed, "
            "propose a short pilot with clear success criteria."
        )
    elif score >= 45:
        next_action = (
            f"Send a personalized value note referencing {company}'s stated need, then schedule a "
            "15-min qualification call this week to confirm budget and decision process."
        )
        approach = (
            "Value-led nurture: educate with a relevant case study, map stakeholders, offer a "
            "light audit or teardown call before heavy pitch."
        )
    else:
        next_action = (
            f"Park {company} in a low-touch nurture sequence; re-score after new intent "
            "(demo request, content download, or budget update)."
        )
        approach = (
            "Protect SDRs' calendar: light content + quarterly check-in. Escalate only if "
            "budget/title/urgency improve."
        )

    risks = []
    if b_pts < 5:
        risks.append("Budget unclear or below ICP preference")
    if t_pts < 6:
        risks.append("May lack purchasing authority")
    if u_pts < 4:
        risks.append("Weak urgency / longer cycle risk")
    if i_pts < 5:
        risks.append("Industry fit outside core ICP")
    if not lead_data.get("requirement"):
        risks.append("Pain not fully defined")
    if not risks:
        risks.append("No major red flags from available fields")

    first_name = (lead_data.get("full_name") or "there").split()[0]
    req = (lead_data.get("requirement") or "pipeline quality and faster follow-ups")[:140]
    personalization = (
        f"Open with {first_name}'s role at {company} and their focus on {req}. "
        f"Anchor proof in {industry}, reference {budget} commercial context, and end with a "
        f"single concrete CTA appropriate for a {classification} lead."
    )

    return {
        "score": score,
        "classification": classification,
        "reason": reason,
        "buyer_intent": buyer_intent,
        "budget_fit": budget_fit,
        "urgency_level": urgency_level,
        "suggested_next_action": next_action,
        "recommended_approach": approach,
        "risk_factors": "; ".join(risks),
        "personalization_notes": personalization,
        "scoring_factors": factors,
        "priority": priority_from_score(score),
    }


def factors_to_json(factors: dict[str, Any] | None) -> str | None:
    if not factors:
        return None
    return json.dumps(factors)

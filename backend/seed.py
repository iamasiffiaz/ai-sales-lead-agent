"""Seed demo data for local development and portfolio demos.

Usage (from backend/):
  python seed.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, date
import json

from passlib.context import CryptContext

from database import SessionLocal, init_db, engine, Base
from models import (
    User,
    Lead,
    LeadQualification,
    EmailDraft,
    FollowUp,
    PipelineActivity,
    Recommendation,
    AppSettings,
)
from services.lead_scoring_service import score_lead, factors_to_json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SEED_LEADS = [
    {
        "full_name": "Aisha Rahman",
        "company": "Northstar Analytics",
        "email": "aisha@northstaranalytics.io",
        "phone": "+1-415-555-0101",
        "job_title": "VP of Sales",
        "industry": "SaaS",
        "company_size": "51-200",
        "budget": "$40,000",
        "requirement": "Need AI lead scoring ASAP this quarter to cut SDR research time.",
        "lead_source": "Inbound Demo",
        "website": "https://northstaranalytics.io",
        "linkedin_url": "https://linkedin.com/in/aisharahman",
        "notes": "Booked demo; budget approved by CFO.",
        "status": "Qualified",
    },
    {
        "full_name": "Marcus Chen",
        "company": "BrightLedger",
        "email": "marcus@brightledger.com",
        "phone": "+1-646-555-0142",
        "job_title": "Founder & CEO",
        "industry": "FinTech",
        "company_size": "11-50",
        "budget": "$25k",
        "requirement": "Automate inbound qualification from website forms and LinkedIn.",
        "lead_source": "Referral",
        "website": "https://brightledger.com",
        "linkedin_url": "https://linkedin.com/in/marcuschen",
        "notes": "Referred by existing customer; urgent pilot.",
        "status": "Proposal Sent",
    },
    {
        "full_name": "Sofia Alvarez",
        "company": "Cascade Agency",
        "email": "sofia@cascade.agency",
        "phone": "+1-312-555-0198",
        "job_title": "Head of Client Growth",
        "industry": "Agency",
        "company_size": "51-200",
        "budget": "$15,000",
        "requirement": "Centralize multi-client lead pipelines and personalized outreach.",
        "lead_source": "LinkedIn",
        "website": "https://cascade.agency",
        "linkedin_url": "https://linkedin.com/in/sofiaa",
        "notes": "Manages 12 B2B accounts.",
        "status": "Contacted",
    },
    {
        "full_name": "James Okafor",
        "company": "Helix Health Ops",
        "email": "james@helixhealthops.com",
        "phone": "+1-617-555-0177",
        "job_title": "Director of Partnerships",
        "industry": "Healthcare",
        "company_size": "201-500",
        "budget": "$60,000",
        "requirement": "Qualify clinic partnership leads with compliance-aware messaging.",
        "lead_source": "Webinar",
        "website": "https://helixhealthops.com",
        "linkedin_url": "https://linkedin.com/in/jamesokafor",
        "notes": "Strong ICP adjacent; security review needed.",
        "status": "New",
    },
    {
        "full_name": "Priya Nair",
        "company": "ShopNest Commerce",
        "email": "priya@shopnest.co",
        "phone": "+1-206-555-0133",
        "job_title": "Growth Manager",
        "industry": "E-commerce",
        "company_size": "51-200",
        "budget": "$8,000",
        "requirement": "Improve follow-up cadence for abandoned enterprise store demos.",
        "lead_source": "Website Form",
        "website": "https://shopnest.co",
        "linkedin_url": "https://linkedin.com/in/priyanair",
        "notes": "Evaluating multiple vendors.",
        "status": "Contacted",
    },
    {
        "full_name": "Daniel Brooks",
        "company": "Summit Logistics",
        "email": "dbrooks@summitlogistics.com",
        "phone": "+1-704-555-0110",
        "job_title": "Operations Analyst",
        "industry": "Logistics",
        "company_size": "500+",
        "budget": "Unknown",
        "requirement": "Exploring tools for partner lead tracking.",
        "lead_source": "Cold Email",
        "website": "https://summitlogistics.com",
        "linkedin_url": None,
        "notes": "Not a decision maker.",
        "status": "New",
    },
    {
        "full_name": "Elena Petrova",
        "company": "Voxel Design Studio",
        "email": "elena@voxel.studio",
        "phone": "+1-503-555-0188",
        "job_title": "Co-Founder",
        "industry": "Creative Services",
        "company_size": "1-10",
        "budget": "$3,000",
        "requirement": "Need lightweight CRM and email templates for outbound.",
        "lead_source": "Ads",
        "website": "https://voxel.studio",
        "linkedin_url": "https://linkedin.com/in/elenapetrova",
        "notes": "Budget-sensitive design studio.",
        "status": "New",
    },
    {
        "full_name": "Ryan Patel",
        "company": "CloudMeter",
        "email": "ryan@cloudmeter.ai",
        "phone": "+1-650-555-0129",
        "job_title": "CTO",
        "industry": "SaaS",
        "company_size": "11-50",
        "budget": "$50k enterprise",
        "requirement": "Integrate AI qualification into existing CRM within 30 days.",
        "lead_source": "Partner",
        "website": "https://cloudmeter.ai",
        "linkedin_url": "https://linkedin.com/in/ryanpatel",
        "notes": "Technical evaluation underway; urgent timeline.",
        "status": "Qualified",
    },
    {
        "full_name": "Natalie Gomez",
        "company": "Harbor Legal Tech",
        "email": "natalie@harborlegal.io",
        "phone": "+1-212-555-0166",
        "job_title": "Chief Revenue Officer",
        "industry": "LegalTech",
        "company_size": "51-200",
        "budget": "$75,000",
        "requirement": "Score inbound law-firm leads and auto-draft meeting requests.",
        "lead_source": "Inbound Demo",
        "website": "https://harborlegal.io",
        "linkedin_url": "https://linkedin.com/in/nataliegomez",
        "notes": "Board-level visibility; wants ROI dashboard.",
        "status": "Proposal Sent",
    },
    {
        "full_name": "Omar Haddad",
        "company": "Desert Palm Hotels",
        "email": "omar@desertpalm.com",
        "phone": "+1-480-555-0155",
        "job_title": "Marketing Director",
        "industry": "Hospitality",
        "company_size": "201-500",
        "budget": "$12,000",
        "requirement": "Qualify corporate booking inquiries from campaigns.",
        "lead_source": "Event",
        "website": "https://desertpalm.com",
        "linkedin_url": "https://linkedin.com/in/omarhaddad",
        "notes": "Met at hospitality summit.",
        "status": "Contacted",
    },
    {
        "full_name": "Grace Kim",
        "company": "EduSpark Learning",
        "email": "grace@eduspark.edu",
        "phone": "+1-919-555-0144",
        "job_title": "VP Partnerships",
        "industry": "EdTech",
        "company_size": "51-200",
        "budget": "$20,000",
        "requirement": "Prioritize school district RFPs due this month.",
        "lead_source": "Content Download",
        "website": "https://eduspark.edu",
        "linkedin_url": "https://linkedin.com/in/gracekim",
        "notes": "Downloaded pricing guide.",
        "status": "Qualified",
    },
    {
        "full_name": "Tom Nguyen",
        "company": "ByteForge Studios",
        "email": "tom@byteforge.gg",
        "phone": "+1-408-555-0190",
        "job_title": "Product Manager",
        "industry": "Gaming",
        "company_size": "11-50",
        "budget": "$5,000",
        "requirement": "Researching sales tools for creator partnerships.",
        "lead_source": "LinkedIn",
        "website": "https://byteforge.gg",
        "linkedin_url": "https://linkedin.com/in/tomnguyen",
        "notes": "Early research only.",
        "status": "New",
    },
    {
        "full_name": "Isabelle Moreau",
        "company": "Lumen Sustainability",
        "email": "isabelle@lumensustain.com",
        "phone": "+1-303-555-0171",
        "job_title": "CEO",
        "industry": "CleanTech",
        "company_size": "11-50",
        "budget": "$35k",
        "requirement": "Qualify ESG consulting inbound leads with urgency for Q3 close.",
        "lead_source": "Referral",
        "website": "https://lumensustain.com",
        "linkedin_url": "https://linkedin.com/in/isabellemoreau",
        "notes": "Ready to buy; asks for case studies.",
        "status": "Won",
    },
    {
        "full_name": "Chris Walker",
        "company": "RetailPilot",
        "email": "chris@retailpilot.com",
        "phone": "+1-512-555-0121",
        "job_title": "Sales Ops Lead",
        "industry": "Retail Tech",
        "company_size": "51-200",
        "budget": "$18,000",
        "requirement": "CSV import + scoring for 2,000 store manager leads.",
        "lead_source": "Website Form",
        "website": "https://retailpilot.com",
        "linkedin_url": "https://linkedin.com/in/chriswalker",
        "notes": "Ops-owned purchase, strong volume need.",
        "status": "Contacted",
    },
    {
        "full_name": "Fatima Zahra",
        "company": "Orbit HR Suite",
        "email": "fatima@orbithr.io",
        "phone": "+1-857-555-0182",
        "job_title": "Head of Sales",
        "industry": "HR Tech",
        "company_size": "51-200",
        "budget": "$45,000",
        "requirement": "Need AI outreach for enterprise HRIS pilots this week.",
        "lead_source": "Inbound Demo",
        "website": "https://orbithr.io",
        "linkedin_url": "https://linkedin.com/in/fatimazahra",
        "notes": "Hot — competitor contract ending.",
        "status": "Proposal Sent",
    },
    {
        "full_name": "Ben Cooper",
        "company": "QuietOak Farms",
        "email": "ben@quietoak.farm",
        "phone": "+1-515-555-0112",
        "job_title": "Owner",
        "industry": "Agriculture",
        "company_size": "1-10",
        "budget": "$1,500",
        "requirement": "Maybe need a simple contact spreadsheet tool later.",
        "lead_source": "Ads",
        "website": None,
        "linkedin_url": None,
        "notes": "Not ICP.",
        "status": "Lost",
    },
    {
        "full_name": "Hannah Lee",
        "company": "SignalWire CRM",
        "email": "hannah@signalwirecrm.com",
        "phone": "+1-415-555-0199",
        "job_title": "VP Product",
        "industry": "SaaS",
        "company_size": "201-500",
        "budget": "Open budget / flexible",
        "requirement": "Embed qualification APIs into platform roadmap ASAP.",
        "lead_source": "Partner",
        "website": "https://signalwirecrm.com",
        "linkedin_url": "https://linkedin.com/in/hannahlee",
        "notes": "Strategic partnership potential.",
        "status": "Qualified",
    },
    {
        "full_name": "Luis Romero",
        "company": "Nova Insurance Group",
        "email": "luis@novainsurance.com",
        "phone": "+1-305-555-0138",
        "job_title": "Regional Sales Director",
        "industry": "Insurance",
        "company_size": "500+",
        "budget": "$30,000",
        "requirement": "Score agent-sourced commercial leads and automate follow-ups.",
        "lead_source": "Event",
        "website": "https://novainsurance.com",
        "linkedin_url": "https://linkedin.com/in/luisromero",
        "notes": "Procurement cycle ~60 days.",
        "status": "Contacted",
    },
    {
        "full_name": "Emily Foster",
        "company": "PacketWave Networks",
        "email": "emily@packetwave.net",
        "phone": "+1-972-555-0160",
        "job_title": "Business Development Manager",
        "industry": "Telecom",
        "company_size": "201-500",
        "budget": "$10k",
        "requirement": "Improve outbound sequencing for ISP wholesale deals.",
        "lead_source": "Outbound",
        "website": "https://packetwave.net",
        "linkedin_url": "https://linkedin.com/in/emilyfoster",
        "notes": "Responded to cold call; curious.",
        "status": "New",
    },
    {
        "full_name": "Andre Silva",
        "company": "Finora Capital",
        "email": "andre@finora.capital",
        "phone": "+1-212-555-0108",
        "job_title": "Managing Partner",
        "industry": "FinTech",
        "company_size": "11-50",
        "budget": "$100k+",
        "requirement": "Build internal AI SDR stack for portfolio founders immediately.",
        "lead_source": "Referral",
        "website": "https://finora.capital",
        "linkedin_url": "https://linkedin.com/in/andresilva",
        "notes": "Can expand across portfolio companies.",
        "status": "Won",
    },
    {
        "full_name": "Maya Thompson",
        "company": "Greenline Construction",
        "email": "maya@greenline.build",
        "phone": "+1-602-555-0147",
        "job_title": "Business Development",
        "industry": "Construction",
        "company_size": "51-200",
        "budget": "$7,000",
        "requirement": "Track GC bid invitations and reminder emails.",
        "lead_source": "Website Form",
        "website": "https://greenline.build",
        "linkedin_url": "https://linkedin.com/in/mayathompson",
        "notes": "Moderate fit.",
        "status": "New",
    },
    {
        "full_name": "Jonas Berg",
        "company": "Nordic Robotics AB",
        "email": "jonas@nordicrobotics.se",
        "phone": "+46-8-555-0191",
        "job_title": "Head of Sales",
        "industry": "Manufacturing",
        "company_size": "201-500",
        "budget": "$55,000",
        "requirement": "Qualify OEM channel leads with multilingual follow-up drafts.",
        "lead_source": "Webinar",
        "website": "https://nordicrobotics.se",
        "linkedin_url": "https://linkedin.com/in/jonasberg",
        "notes": "EU expansion priority.",
        "status": "Qualified",
    },
    {
        "full_name": "Rachel Adams",
        "company": "PeerTutor Marketplace",
        "email": "rachel@peertutor.com",
        "phone": "+1-734-555-0123",
        "job_title": "Marketing Specialist",
        "industry": "EdTech",
        "company_size": "1-10",
        "budget": "Low / N/A",
        "requirement": "Looking for free tools someday.",
        "lead_source": "Cold Email",
        "website": "https://peertutor.com",
        "linkedin_url": None,
        "notes": "Cold / low urgency.",
        "status": "Lost",
    },
    {
        "full_name": "Kevin Ortiz",
        "company": "Atlas PropTech",
        "email": "kevin@atlasproptech.com",
        "phone": "+1-305-555-0193",
        "job_title": "Founder",
        "industry": "PropTech",
        "company_size": "11-50",
        "budget": "$22,000",
        "requirement": "Score landlord leads from property portal forms this month.",
        "lead_source": "Inbound Demo",
        "website": "https://atlasproptech.com",
        "linkedin_url": "https://linkedin.com/in/kevinortiz",
        "notes": "Requested proposal outline.",
        "status": "Proposal Sent",
    },
    {
        "full_name": "Sarah Mitchell",
        "company": "QuantumOps Monitoring",
        "email": "sarah@quantumops.io",
        "phone": "+1-778-555-0150",
        "job_title": "Chief Operating Officer",
        "industry": "SaaS",
        "company_size": "51-200",
        "budget": "$48,000",
        "requirement": "Unify sales pipeline analytics and AI next-best-action for SDRs urgently.",
        "lead_source": "Referral",
        "website": "https://quantumops.io",
        "linkedin_url": "https://linkedin.com/in/sarahmitchell",
        "notes": "Executive sponsor engaged.",
        "status": "Contacted",
    },
]


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Delete DB / drop tables to re-seed.")
            print("Tip: delete backend/leads.db or run with --force")
            return

        user = User(
            email="demo@qualifyai.dev",
            full_name="Alex Morgan",
            hashed_password=pwd_context.hash("demo1234"),
        )
        db.add(user)
        db.flush()

        settings = AppSettings(
            business_name="QualifyAI",
            target_industry="SaaS, FinTech, B2B Services, HR Tech, LegalTech",
            ideal_customer_profile=(
                "B2B companies with 11-500 employees, clear budget ($10k+), "
                "and leadership buyers seeking AI lead qualification and pipeline automation."
            ),
            minimum_budget_preference="$10,000+",
            default_follow_up_interval_days=3,
            ai_provider="OpenAI Compatible",
            api_key_placeholder="",
            email_signature="Best regards,\nAlex Morgan\nSales Lead, QualifyAI\nhttps://qualifyai.dev",
        )
        db.add(settings)

        today = date.today()
        leads_created = []
        for idx, item in enumerate(SEED_LEADS):
            created = datetime.utcnow() - timedelta(days=(25 - idx))
            lead = Lead(
                owner_id=user.id,
                **item,
                created_at=created,
                updated_at=created,
                last_contacted_at=created + timedelta(days=1) if item["status"] != "New" else None,
            )
            result = score_lead(item, {
                "target_industry": settings.target_industry,
                "ideal_customer_profile": settings.ideal_customer_profile,
            })
            lead.ai_score = result["score"]
            lead.ai_classification = result["classification"]
            lead.priority = result["priority"]
            lead.next_action = result["suggested_next_action"]
            if item["status"] in ("Contacted", "Qualified", "Proposal Sent"):
                lead.next_follow_up_date = today + timedelta(days=(idx % 5) - 2)
            db.add(lead)
            db.flush()
            leads_created.append((lead, result))

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
            db.add(
                PipelineActivity(
                    lead_id=lead.id,
                    from_status=None,
                    to_status="New",
                    note="Lead created (seed)",
                    created_at=created,
                )
            )
            if item["status"] != "New":
                db.add(
                    PipelineActivity(
                        lead_id=lead.id,
                        from_status="New",
                        to_status=item["status"],
                        note="Stage progressed (seed)",
                        created_at=created + timedelta(days=2),
                    )
                )

        # 10 email drafts (match runtime AI email quality)
        from services.ai_service import generate_mock_email

        email_specs = [
            (0, "First Outreach", "Draft"),
            (1, "Proposal Follow-up", "Sent"),
            (2, "Follow-up", "Draft"),
            (7, "Meeting Request", "Draft"),
            (8, "Proposal Follow-up", "Sent"),
            (10, "First Outreach", "Draft"),
            (14, "First Outreach", "Sent"),
            (16, "Meeting Request", "Draft"),
            (19, "Follow-up", "Sent"),
            (24, "Re-engagement", "Draft"),
        ]
        settings_dict = {
            "business_name": settings.business_name,
            "email_signature": settings.email_signature,
            "target_industry": settings.target_industry,
        }
        for lead_idx, email_type, status in email_specs:
            lead, _ = leads_created[lead_idx]
            lead_payload = {
                "full_name": lead.full_name,
                "company": lead.company,
                "job_title": lead.job_title,
                "industry": lead.industry,
                "budget": lead.budget,
                "requirement": lead.requirement,
                "lead_source": lead.lead_source,
                "ai_score": lead.ai_score,
                "ai_classification": lead.ai_classification,
            }
            generated = generate_mock_email(lead_payload, email_type, settings_dict)
            draft = EmailDraft(
                lead_id=lead.id,
                email_type=email_type,
                subject=generated["subject"],
                body=generated["body"],
                status=status,
                sent_at=datetime.utcnow() - timedelta(days=1) if status == "Sent" else None,
            )
            db.add(draft)

        # 8 follow-ups
        follow_specs = [
            (0, -1, "Pending"),
            (1, 0, "Pending"),
            (2, 1, "Pending"),
            (4, -3, "Overdue"),
            (7, 2, "Pending"),
            (8, -2, "Overdue"),
            (14, 3, "Pending"),
            (17, 4, "Completed"),
        ]
        for lead_idx, day_offset, status in follow_specs:
            lead, _ = leads_created[lead_idx]
            due = today + timedelta(days=day_offset)
            fu = FollowUp(
                lead_id=lead.id,
                due_date=due,
                notes=f"Check in on {lead.company} — {lead.next_action}",
                status=status if status != "Pending" else ("Overdue" if due < today else "Pending"),
                completed_at=datetime.utcnow() if status == "Completed" else None,
            )
            db.add(fu)
            lead.next_follow_up_date = due

        # 6 recommendations
        recs = [
            ("Contact Hot leads first", "Priority Outreach", "High",
             "Prioritize Northstar Analytics, CloudMeter, Harbor Legal, Orbit HR, and Finora Capital for same-day outreach."),
            ("Clear overdue follow-ups", "Follow-up", "High",
             "Two+ follow-ups are overdue. Resolve ShopNest and Harbor Legal reminders before net-new outbound."),
            ("SaaS & FinTech outperform", "Industry Insight", "Medium",
             "SaaS and FinTech leads show the strongest average scores — double down on those ICP channels this week."),
            ("Close open proposals", "Conversion", "High",
             "BrightLedger, Harbor Legal, Orbit HR, and Atlas PropTech have proposals out — book decision meetings."),
            ("Two-track sales motion", "Strategy", "Medium",
             "Hot leads: meeting CTA within 24h. Warm leads: case study + audit offer. Protect calendar for Hot only."),
            ("Tighten pipeline hygiene", "Pipeline", "Low",
             "Require next follow-up dates before stage moves and batch-nurture Cold leads quarterly."),
        ]
        for title, category, priority, content in recs:
            db.add(
                Recommendation(
                    title=title,
                    category=category,
                    content=content,
                    priority=priority,
                    is_active=True,
                )
            )

        db.commit()
        print("Seed complete:")
        print(f"  User: demo@qualifyai.dev / demo1234")
        print(f"  Leads: {len(leads_created)}")
        print(f"  Emails: {len(email_specs)}")
        print(f"  Follow-ups: {len(follow_specs)}")
        print(f"  Recommendations: {len(recs)}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if "--force" in sys.argv:
        print("Forcing database reset...")
        reset_db()
    seed()

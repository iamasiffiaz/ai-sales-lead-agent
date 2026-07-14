import csv
import io
from typing import Any


CSV_LEAD_FIELDS = [
    "name",
    "company",
    "email",
    "phone",
    "job_title",
    "industry",
    "company_size",
    "budget",
    "requirement",
    "lead_source",
    "website",
    "linkedin_url",
    "notes",
]

EXPORT_FIELDS = [
    "id",
    "full_name",
    "company",
    "email",
    "phone",
    "job_title",
    "industry",
    "company_size",
    "budget",
    "requirement",
    "lead_source",
    "website",
    "linkedin_url",
    "notes",
    "status",
    "ai_score",
    "ai_classification",
    "priority",
    "next_action",
    "next_follow_up_date",
    "created_at",
]


def parse_csv_bytes(content: bytes) -> list[dict[str, Any]]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower().replace(" ", "_"): (v or "").strip() for k, v in row.items() if k}
        cleaned["_row_number"] = idx
        rows.append(cleaned)
    return rows


def leads_to_csv(leads: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for lead in leads:
        row = {}
        for field in EXPORT_FIELDS:
            value = lead.get(field)
            if value is None:
                row[field] = ""
            else:
                row[field] = str(value)
        writer.writerow(row)
    return buffer.getvalue()


def normalize_csv_lead(row: dict[str, Any]) -> dict[str, Any]:
    name = row.get("name") or row.get("full_name") or ""
    return {
        "full_name": name,
        "company": row.get("company", ""),
        "email": row.get("email", "").lower(),
        "phone": row.get("phone") or None,
        "job_title": row.get("job_title") or None,
        "industry": row.get("industry") or None,
        "company_size": row.get("company_size") or None,
        "budget": row.get("budget") or None,
        "requirement": row.get("requirement") or None,
        "lead_source": row.get("lead_source") or None,
        "website": row.get("website") or None,
        "linkedin_url": row.get("linkedin_url") or None,
        "notes": row.get("notes") or None,
    }

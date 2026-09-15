"""
Support Ticket Triage & Insights Assistant
============================================

Reads a CSV of support tickets, uses the Claude API to classify each one
(category, priority, one-line summary, suggested first-response draft),
stores the enriched results in PostgreSQL, and writes a summary report
(Markdown + CSV) of ticket volumes and trends.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    export DATABASE_URL="postgresql://localhost:5432/support_ticket_triage_ai"  # optional, this is the default
    python3 triage.py

Requires: anthropic, psycopg2-binary  (see requirements.txt)
A local PostgreSQL database must exist first — see README.md.
"""

import csv
import json
import os
import sys
from pathlib import Path

DATA_PATH = Path("data/sample_tickets.csv")
REPORT_MD_PATH = Path("report.md")
REPORT_CSV_PATH = Path("report_export.csv")

DEFAULT_DATABASE_URL = "postgresql://localhost:5432/support_ticket_triage_ai"
MODEL = "claude-sonnet-5"

TRIAGE_PROMPT_TEMPLATE = """You are triaging an internal IT support ticket. Read it and respond with ONLY a JSON object (no prose, no markdown fences) with these exact keys:

- "category": one of ["hardware", "software", "network", "account_access", "security", "other"]
- "priority": one of ["low", "medium", "high"]
- "summary": a single sentence (max 20 words) summarizing the issue
- "suggested_response": a short, professional draft first-response to the requester (2-4 sentences), acknowledging the issue and stating a plausible next step. Do not invent specific ticket numbers, names, or timelines you don't have.

Ticket subject: {subject}
Ticket description: {description}
"""


def load_tickets(path: Path):
    if not path.exists():
        sys.exit(f"Expected input data at {path} — run generate_data.py first.")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify_ticket(client, subject: str, description: str) -> dict:
    prompt = TRIAGE_PROMPT_TEMPLATE.format(subject=subject, description=description)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    # Be forgiving of accidental markdown fences
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "category": "other",
            "priority": "medium",
            "summary": "(could not parse model output)",
            "suggested_response": text[:300],
        }


def connect_db():
    try:
        import psycopg2
    except ImportError:
        sys.exit("Missing dependency. Run: pip install -r requirements.txt")

    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    try:
        return psycopg2.connect(database_url)
    except psycopg2.OperationalError as e:
        sys.exit(
            f"Could not connect to PostgreSQL at {database_url}\n\n{e}\n"
            "Create the database first, e.g.:\n"
            "  createdb support_ticket_triage_ai\n"
            "or open pgAdmin4/DBeaver and create a database named 'support_ticket_triage_ai',\n"
            "then re-run this script. You can also point DATABASE_URL at a different DB."
        )


def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                submitted_at TEXT,
                requester TEXT,
                subject TEXT,
                description TEXT,
                category TEXT,
                priority TEXT,
                summary TEXT,
                suggested_response TEXT
            )
        """)
    conn.commit()


def upsert_ticket(conn, ticket: dict, triage: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tickets
                (ticket_id, submitted_at, requester, subject, description, category, priority, summary, suggested_response)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticket_id) DO UPDATE SET
                submitted_at = EXCLUDED.submitted_at,
                requester = EXCLUDED.requester,
                subject = EXCLUDED.subject,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                priority = EXCLUDED.priority,
                summary = EXCLUDED.summary,
                suggested_response = EXCLUDED.suggested_response
            """,
            (
                ticket["ticket_id"], ticket["submitted_at"], ticket["requester"],
                ticket["subject"], ticket["description"],
                triage.get("category", "other"), triage.get("priority", "medium"),
                triage.get("summary", ""), triage.get("suggested_response", ""),
            ),
        )


def build_report(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT category, COUNT(*) as n FROM tickets GROUP BY category ORDER BY n DESC")
        by_category = cur.fetchall()

        cur.execute("SELECT priority, COUNT(*) as n FROM tickets GROUP BY priority ORDER BY n DESC")
        by_priority = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM tickets")
        total = cur.fetchone()[0]

        cur.execute("SELECT ticket_id, subject, summary FROM tickets WHERE priority = 'high'")
        high_priority = cur.fetchall()

        cur.execute("SELECT ticket_id, submitted_at, category, priority, summary FROM tickets ORDER BY submitted_at")
        export_rows = cur.fetchall()

    lines = ["# Ticket Triage Report", "", f"**Total tickets processed:** {total}", ""]

    lines += ["## Volume by category", ""]
    for category, n in by_category:
        lines.append(f"- {category}: {n} ({n / total:.0%})")

    lines += ["", "## Volume by priority", ""]
    for priority, n in by_priority:
        lines.append(f"- {priority}: {n} ({n / total:.0%})")

    lines += ["", "## High-priority tickets needing attention first", ""]
    if high_priority:
        for ticket_id, subject, summary in high_priority:
            lines.append(f"- **{ticket_id}** — {subject}: {summary}")
    else:
        lines.append("- None flagged as high priority in this batch.")

    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    # Also export a flat CSV, ready to drop straight into Tableau / DBeaver
    with open(REPORT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ticket_id", "submitted_at", "category", "priority", "summary"])
        writer.writerows(export_rows)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "Get a key at https://console.anthropic.com/ and run:\n"
            '  export ANTHROPIC_API_KEY="sk-ant-..."\n'
            "then re-run this script."
        )

    try:
        import anthropic
    except ImportError:
        sys.exit("Missing dependency. Run: pip install -r requirements.txt")

    client = anthropic.Anthropic(api_key=api_key)

    tickets = load_tickets(DATA_PATH)
    print(f"Loaded {len(tickets)} tickets from {DATA_PATH}")

    conn = connect_db()
    init_db(conn)

    for i, ticket in enumerate(tickets, 1):
        print(f"[{i}/{len(tickets)}] Triaging {ticket['ticket_id']}...")
        try:
            triage = classify_ticket(client, ticket["subject"], ticket["description"])
        except anthropic.AuthenticationError:
            conn.close()
            sys.exit(
                "\nAnthropic API rejected the key (401 authentication_error).\n"
                "Double-check ANTHROPIC_API_KEY is the full key from "
                "https://console.anthropic.com/settings/keys (it starts with "
                "'sk-ant-api03-' and is a long string — make sure none of it got "
                "truncated when copying)."
            )
        except anthropic.APIError as e:
            conn.close()
            sys.exit(f"\nAnthropic API error on {ticket['ticket_id']}: {e}")
        upsert_ticket(conn, ticket, triage)
        conn.commit()

    build_report(conn)
    conn.close()

    print(f"\nDone. Data is in PostgreSQL (table 'tickets') — open it in pgAdmin4 or DBeaver to explore.")
    print(f"Also wrote {REPORT_MD_PATH} and {REPORT_CSV_PATH}")


if __name__ == "__main__":
    main()

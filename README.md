# Support Ticket Triage & Insights Assistant

A small end-to-end demo of AI automation applied to a common ICT operations
problem: turning a pile of raw support tickets into triaged, prioritized,
actionable data.

**Pipeline:** CSV of tickets → Claude API classifies each ticket (category,
priority, summary, draft response) → results stored in PostgreSQL → SQL
aggregation produces a Markdown report and a CSV ready to drop straight into
Tableau.

## Why this exists

Built as a practical example of applying AI automation to everyday IT/ICT
operations work — not a toy chatbot, but a small pipeline that takes a real
operational task (triaging support tickets) and speeds it up end to end.

## Tech stack

- **Python** — orchestration
- **Anthropic Claude API** (`claude-sonnet-5`) — per-ticket classification and draft-response generation
- **PostgreSQL** — structured storage and SQL-based aggregation (browsable in pgAdmin4 / DBeaver)
- **CSV** — data loading and export

## How it works

1. `generate_data.py` creates a synthetic dataset of ~50 sample IT support
   tickets (`data/sample_tickets.csv`). All data is fabricated for
   demonstration — no real company or customer information.
2. `triage.py`:
   - Loads the tickets.
   - Sends each one to Claude, asking for a structured JSON response:
     category, priority, one-line summary, and a suggested first-response draft.
   - Writes the enriched results into a `tickets` table in PostgreSQL.
   - Runs SQL aggregations over the results and writes `report.md` (a
     readable summary: volume by category/priority, high-priority tickets
     to handle first) plus `report_export.csv` for further analysis in a
     BI tool.

## Running it

```bash
# 1. Create the database (any of these work)
createdb support_ticket_triage_ai
# ...or create a database named "support_ticket_triage_ai" in pgAdmin4 / DBeaver

# 2. Set up Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Generate sample data and run the pipeline
python3 generate_data.py      # creates data/sample_tickets.csv
export ANTHROPIC_API_KEY="sk-ant-..."   # get a key at console.anthropic.com

# optional — defaults to postgresql://localhost:5432/support_ticket_triage_ai
export DATABASE_URL="postgresql://user:password@localhost:5432/support_ticket_triage_ai"

python3 triage.py             # populates PostgreSQL, produces report.md, report_export.csv
```

Once it's run, open the `tickets` table in **pgAdmin4** or **DBeaver** to
browse the AI-classified results directly, or explore `report_export.csv`
in Tableau.

## Example output

```markdown
# Ticket Triage Report

Total tickets processed: 50

## Volume by category
- software: 13 (26%)
- network: 12 (24%)
- account_access: 12 (24%)
- hardware: 10 (20%)
- security: 3 (6%)

## Volume by priority
- high: 28 (56%)
- medium: 18 (36%)
- low: 4 (8%)

## High-priority tickets needing attention first
- T-1001 — Cannot connect to company database: User can't connect to the reporting database remotely, likely a VPN/network issue.
- T-1010 — Laptop won't turn on: Laptop won't power on at all despite a charged battery, likely a hardware failure.
- T-1013 — Phishing email reported: User reported a suspicious email requesting password verification.
```

## Possible extensions

- Swap the synthetic CSV for a real ticketing system export (Zendesk,
  Freshdesk, Jira Service Management, etc.) via their export/API.
- Add a lightweight web front-end so non-technical staff can view the report.
- Track triage accuracy over time by comparing AI-assigned priority to
  actual resolution time.

---

Built by [Filip Mamic](https://www.linkedin.com/in/filip-mamic-hr/) as a
practical example of applying AI automation to ICT operations.

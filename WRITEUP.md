# AI-assisted support ticket triage — case study

A short write-up of what this project demonstrates and why it's useful.

## The problem

IT/support teams spend real time each day just reading through incoming
tickets, figuring out what category each one falls into, how urgent it is,
and drafting a first reply — before any actual troubleshooting starts. That
sorting work is repetitive and takes staff time away from actually resolving
issues.

## What this does

A small pipeline that takes a batch of support tickets and automatically:

1. **Classifies** each one by category (hardware, software, network, account
   access, security) and priority (low/medium/high).
2. **Summarizes** the issue in one line, so someone scanning the queue
   doesn't have to read every ticket in full.
3. **Drafts a first response** for each ticket, so staff can review and send
   rather than write from scratch.
4. **Produces a report** showing ticket volume by category and priority, and
   flags the high-priority ones that need attention first.

## Why it matters

- **Faster first response** — a draft reply exists the moment a ticket comes
  in, instead of waiting for someone to have time to write one.
- **Consistent triage** — every ticket gets the same category/priority logic
  applied, instead of it depending on whoever happens to read it first.
- **Visibility** — the summary report gives a manager a quick read on what's
  coming in and what's urgent, without manually reading the whole queue.
- **Time saved** — sorting and drafting is the part that scales linearly with
  ticket volume; this is the part AI is well suited to take off someone's
  plate.

## How it's built

A small Python pipeline: tickets in a CSV → each one sent to Claude (Anthropic's
AI model) for classification and draft response → results stored in a
PostgreSQL database → SQL used to build the summary report. It runs against a
synthetic sample dataset (no real tickets or customer data), built purely to
demonstrate the approach end to end.

Full code: see the accompanying GitHub repository.

## Where this could go from here

This was deliberately kept small and generic so it's easy to follow end to
end. A natural next step for a real deployment would be connecting it to
whatever system is actually used for support tickets (Zendesk, Freshdesk,
Jira Service Management, an internal tool, etc.) and tailoring the
categories and report to match real day-to-day work — or applying the same
pattern to a different repetitive, data-heavy process entirely.

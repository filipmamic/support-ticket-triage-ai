"""
Generates a synthetic (fabricated) IT support ticket dataset for demo purposes.

No real company or customer data is used anywhere in this project. All names,
tickets, and details below are randomly generated for illustration only.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

SUBJECTS_AND_BODIES = [
    ("Can't log into email", "I've tried resetting my password twice but I still can't access my company email account. Getting an 'invalid credentials' error every time."),
    ("Laptop won't turn on", "My laptop was working fine yesterday, now it won't power on at all. No lights, no fan noise. Battery is charged."),
    ("VPN keeps disconnecting", "Every 10-15 minutes my VPN connection drops and I have to reconnect. Started happening this week, was fine before."),
    ("Need software license activated", "We just installed the new design software but it's asking for a license key I don't have. Can someone provision one?"),
    ("Printer not showing up on network", "The 3rd floor printer isn't showing up when I try to print from my machine. Others say it's working for them."),
    ("Request for new monitor", "My current monitor has a flickering issue. Could I get a replacement or a second monitor added to my desk?"),
    ("Shared drive access denied", "I lost access to the 'Finance' shared drive folder after the recent permissions update. I need it back for reporting."),
    ("Slow computer performance", "My machine has been extremely slow for the past few days, especially when opening Excel or the browser."),
    ("Email going to spam for external clients", "Clients are telling me my emails are landing in their spam folder. This started after the domain change."),
    ("New employee onboarding - account setup", "We have a new hire starting Monday and need their email, laptop, and system accounts set up in time."),
    ("Password reset for CRM system", "I'm locked out of the CRM after too many failed login attempts. Need a reset link sent to my work email."),
    ("Wi-Fi keeps dropping in conference room B", "During client calls in conference room B the Wi-Fi disconnects randomly. Very disruptive during meetings."),
    ("Software update broke reporting tool", "After the last update, the internal reporting dashboard shows a blank page instead of loading data."),
    ("Requesting admin rights to install software", "I need to install a data visualization tool for a project but don't have admin rights on my laptop."),
    ("Two-factor authentication not sending codes", "I'm not receiving the SMS code when logging in remotely. Tried resending three times."),
    ("Backup failed notification", "I got an automated email saying my nightly backup failed last night. Not sure what to do next."),
    ("Mobile device not syncing email", "My phone stopped syncing company email since this morning. Already tried removing and re-adding the account."),
    ("Access request for new project folder", "Could someone grant me access to the 'Q4-Rollout' project folder on the shared server?"),
    ("Screen sharing not working in meetings", "When I try to share my screen in video calls, participants just see a black screen."),
    ("Old laptop replacement request", "My laptop is almost 5 years old and struggles to run basic office software. Requesting an upgrade."),
    ("Cannot connect to company database", "Getting a timeout error whenever I try to connect to the reporting database from home."),
    ("Phishing email reported", "I received a suspicious email asking to verify my password. Flagging it in case others got it too."),
    ("Teams calls dropping mid-meeting", "My Teams calls have been dropping every 20 minutes or so for the last two days."),
    ("Need external hard drive encrypted", "Compliance asked me to get my external backup drive encrypted before using it for client data."),
    ("Invoice system access issue", "I can view invoices in the system but can't approve them anymore, even though my role hasn't changed."),
]

PRIORITY_HINT_WORDS = ["urgent", "asap", "can't work", "blocked", "client-facing", "important deadline"]

def generate_tickets(n=50):
    tickets = []
    start_date = datetime(2026, 8, 1)
    for i in range(1, n + 1):
        subject, body = random.choice(SUBJECTS_AND_BODIES)
        # Occasionally add urgency language to vary priority signal
        if random.random() < 0.25:
            body += f" This is {random.choice(PRIORITY_HINT_WORDS)}, please help soon."
        submitted = start_date + timedelta(days=random.randint(0, 40), hours=random.randint(8, 18))
        tickets.append({
            "ticket_id": f"T-{1000 + i}",
            "submitted_at": submitted.strftime("%Y-%m-%d %H:%M"),
            "requester": f"user{i:03d}@example-corp.test",
            "subject": subject,
            "description": body,
        })
    return tickets


def main():
    tickets = generate_tickets(50)
    out_path = "data/sample_tickets.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "submitted_at", "requester", "subject", "description"])
        writer.writeheader()
        writer.writerows(tickets)
    print(f"Wrote {len(tickets)} synthetic tickets to {out_path}")


if __name__ == "__main__":
    main()

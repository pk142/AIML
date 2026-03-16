"""
Multi-Agent Email Workflow Demo
================================
Step 1: Simulate inbound emails
Step 2: Route to client-specific agents (Client A = Law Firm, Client B = Marketing Agency)
Step 3: QA Agent checks the output
Step 4: Print final response

HOW TO RUN:
  1. pip install openai python-dotenv
  2. Paste your OpenAI key inside the .env file
  3. python email_agents.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Loads the OPENAI_API_KEY from your .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────────
# STEP 1 — Simulated inbound emails
# (In real life, these come from SendGrid / Gmail API)
# ─────────────────────────────────────────────

INBOUND_EMAILS = [
    {
        "client_id": "client_a",
        "from": "john@lawfirm.com",
        "subject": "Contract review deadline",
        "body": "Hi, can you remind me of our standard NDA review turnaround time and who the signing authority is?",
    },
    {
        "client_id": "client_b",
        "from": "sara@marketingagency.com",
        "subject": "Campaign brief question",
        "body": "Hey, what is our standard deliverable list for a social media campaign and what is our usual timeline?",
    },
]


# ─────────────────────────────────────────────
# STEP 2A — Client Knowledge Bases
# (In real life, this is a vector DB like Pinecone.
#  For the demo, we use plain text — same concept.)
# ─────────────────────────────────────────────

CLIENT_KNOWLEDGE = {
    "client_a": """
    CLIENT: Hartwell & Associates Law Firm
    
    NDA Review Turnaround: Standard NDA review takes 3 business days.
    Expedited review (surcharge applies): 24 hours.
    
    Signing Authority:
    - Contracts under $10,000: Senior Associate can sign.
    - Contracts $10,000–$100,000: Partner approval required.
    - Contracts above $100,000: Managing Partner (Robert Hartwell) must sign.
    
    Standard NDA Template: Version 4.2 (updated Jan 2024).
    All NDAs must be reviewed by compliance before sending to client.
    """,

    "client_b": """
    CLIENT: BrightSpark Marketing Agency
    
    Standard Social Media Campaign Deliverables:
    - 12 x static post designs (Instagram + LinkedIn)
    - 4 x short-form video scripts (15–30 sec)
    - 1 x content calendar (monthly)
    - 2 x performance reports (mid-campaign + final)
    
    Standard Timeline: 6 weeks from brief approval to final delivery.
    Week 1–2: Strategy & content planning.
    Week 3–4: Design & production.
    Week 5: Client review & revisions (max 2 rounds).
    Week 6: Final delivery & handoff.
    
    Primary contact for campaign approvals: Creative Director.
    """,
}


# ─────────────────────────────────────────────
# STEP 2B — Client Agent
# Takes an email + the client's knowledge base,
# returns a draft reply.
# ─────────────────────────────────────────────

def run_client_agent(email: dict) -> str:
    client_id = email["client_id"]
    knowledge = CLIENT_KNOWLEDGE[client_id]

    print(f"\n{'='*55}")
    print(f"  CLIENT AGENT firing for: {client_id.upper()}")
    print(f"  Email from: {email['from']}")
    print(f"  Subject: {email['subject']}")
    print(f"{'='*55}")

    system_prompt = f"""
You are a helpful AI assistant for a specific client.
You ONLY use the knowledge provided below to answer questions.
Do NOT make up any information not found in the knowledge base.
Always be professional and concise.

--- CLIENT KNOWLEDGE BASE ---
{knowledge}
--- END OF KNOWLEDGE BASE ---
"""

    user_message = f"""
The client sent this email:

Subject: {email['subject']}
Message: {email['body']}

Write a professional email reply that answers their question
using ONLY the information in your knowledge base.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )

    draft_reply = response.choices[0].message.content
    print(f"\n[Client Agent Draft Reply]\n{draft_reply}")
    return draft_reply


# ─────────────────────────────────────────────
# STEP 3 — QA Agent (shared for all clients)
# Checks the draft reply for:
#   - Hallucinations / made-up facts
#   - Proper formatting
#   - Placeholder names still present (e.g. [NAME])
# ─────────────────────────────────────────────

def run_qa_agent(draft_reply: str, original_email: dict) -> str:
    print(f"\n{'─'*55}")
    print(f"  QA AGENT checking output...")
    print(f"{'─'*55}")

    qa_system_prompt = """
You are a strict QA agent for an email automation system.
Your job is to review a draft email reply and improve it.

Check for:
1. Unreplaced placeholders like [NAME], [DATE], [COMPANY] — fix or remove them.
2. Formatting: ensure the email has a greeting, clear body, and sign-off.
3. Tone: professional and clear.
4. No hallucinated facts (do not add information not in the draft).

Return ONLY the final corrected email. No commentary.
"""

    qa_user_message = f"""
Original client email:
\"\"\"{original_email['body']}\"\"\"

Draft reply to review:
\"\"\"{draft_reply}\"\"\"

Return the final polished version.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": qa_system_prompt},
            {"role": "user", "content": qa_user_message},
        ],
        temperature=0.1,
    )

    final_reply = response.choices[0].message.content
    print(f"\n[QA Agent Final Reply]\n{final_reply}")
    return final_reply


# ─────────────────────────────────────────────
# STEP 4 — Main workflow: wire everything together
# ─────────────────────────────────────────────

def process_email(email: dict):
    print(f"\n{'#'*55}")
    print(f"  PROCESSING EMAIL from {email['from']}")
    print(f"{'#'*55}")

    # Step 2: Client agent generates draft
    draft = run_client_agent(email)

    # Step 3: QA agent reviews and polishes
    final = run_qa_agent(draft, email)

    print(f"\n{'*'*55}")
    print(f"  FINAL OUTPUT (ready to send to {email['from']})")
    print(f"{'*'*55}")
    print(final)

    return final


# ─────────────────────────────────────────────
# RUN IT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    for email in INBOUND_EMAILS:
        process_email(email)
        print("\n\n")

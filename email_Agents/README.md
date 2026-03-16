# Multi-Agent Email Workflow Demo

An AI-powered email automation system using multiple agents.
Each client gets a dedicated AI agent with their own knowledge base.
All responses pass through a shared QA agent before being sent.

## How it works

```
Inbound Email
     ↓
  Router (reads client ID)
     ↓              ↓
Client A Agent   Client B Agent
(Law Firm KB)    (Marketing KB)
     ↓              ↓
     └──→ QA Agent ←──┘
              ↓
      Final Email Reply
```

## Setup

1. Clone the repo
   ```bash
   git clone https://github.com/your-username/email-agents.git
   cd email-agents
   ```

2. Install dependencies
   ```bash
   pip install openai python-dotenv
   ```

3. Create your `.env` file
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and paste your OpenAI API key.

4. Run the demo
   ```bash
   python email_agents.py
   ```

## Project structure

```
📁 email-agents/
    ├── email_agents.py   ← main workflow
    ├── .env.example      ← key template (safe to share)
    ├── .env              ← your real key (never uploaded)
    ├── .gitignore        ← protects your .env
    └── README.md
```

## Tech stack

- Python 3.x
- OpenAI API (gpt-4o-mini)
- python-dotenv

## What this demonstrates

- Multi-agent orchestration with client-specific knowledge bases
- Data separation between clients (each agent only sees its own KB)
- Shared QA agent that checks all outputs before delivery
- Foundation for RAG-based email automation systems

## Next steps (planned)

- [ ] Connect to real email via Gmail API or SendGrid
- [ ] Replace hardcoded knowledge base with Pinecone vector DB
- [ ] Add human-in-the-loop approval before sending
- [ ] Web dashboard to manage clients

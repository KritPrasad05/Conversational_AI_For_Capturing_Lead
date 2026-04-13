# ServiceHive Agent

This project implements the assignment as a small conversational sales assistant with:

- RAG over a JSON knowledge base for pricing, features, and policies
- rule-based intent detection with exactly three intents
- multi-turn state tracking for lead capture
- a LangGraph workflow that routes between greeting, product Q&A, and high-intent lead capture
- a mock lead-capture tool that runs only after all required fields are collected

## Project structure

```text
servicehive_agent/
|-- app.py
|-- config.py
|-- data/
|   `-- knowledge_base.json
|-- rag/
|   |-- loader.py
|   |-- embedder.py
|   `-- retriever.py
|-- agent/
|   |-- state.py
|   |-- intent.py
|   |-- planner.py
|   `-- graph.py
|-- tools/
|   `-- lead_capture.py
`-- utils/
    `-- helpers.py
```

## Setup

1. Install dependencies:

```powershell
Scripts\pip.exe install -r requirements.txt
```

2. Add your Gemini key:

```powershell
Copy-Item .env.example .env
```

Then set `GEMINI_API_KEY` inside `.env`.

3. Run the agent:

```powershell
Scripts\python.exe -m servicehive_agent.app
```

## Notes

- The app uses Gemini for embeddings and answer synthesis when `GEMINI_API_KEY` is present.
- If the key or SDK is missing, it falls back to deterministic local embeddings and grounded template answers so the workflow still runs.
- The original assignment mentioned `google-generativeai`, but Google's current official SDK is `google-genai`; the former was deprecated in late 2025, so this implementation uses the supported client.

## Example flow

```text
User: hi
Assistant: Hi, I can help with ServiceHive pricing, features, policies, or getting you set up.

User: what does the growth plan include?
Assistant: ... grounded answer from the knowledge base ...

User: i'm interested in a demo
Assistant: Happy to help with that. Before I log this as a lead, what name should I use?

User: my name is Riya
Assistant: Thanks Riya. What is the best email address for follow-up?

User: riya@example.com
Assistant: Which platform are you using or planning to use, such as Shopify, WhatsApp, Instagram, or your website?

User: Shopify
Assistant: Perfect, Riya. I've captured your interest for the Shopify setup and the team can follow up at riya@example.com.
```

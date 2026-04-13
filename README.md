# 🎬 AutoStream AI Agent
### AI-Powered Lead Generation System | Built for ServiceHive Inflx Platform

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=flat&logo=langchain)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F54E27?style=flat)](https://groq.com)

---

## 📺 Demo Video

> 🎥 **[Watch the Demo](YOUR_VIDEO_LINK_HERE)**
>
> *Replace the link above with your screen recording URL (YouTube, Loom, Google Drive, etc.)*

---

## 📌 What Is This?

AutoStream AI Agent is a **conversational AI lead generation system** built for **ServiceHive's Inflx platform**. It simulates a real-world SaaS sales agent for a fictional company called **AutoStream** — an AI-powered video editing tool for content creators.

The agent can:
- 💬 Answer product and pricing questions using a **RAG-powered knowledge base**
- 🎯 Detect when a user has **high intent to purchase**
- 📋 Collect user details (name, email, platform) through a **natural onboarding flow**
- 💾 Store leads in a database and support **multiple plans per user across platforms**
- 🖥️ Be used via a **Streamlit web UI** backed by a **FastAPI REST API**

---

## 🏗️ Architecture Overview

```
User (Streamlit UI)
        ↓  HTTP POST /chat
FastAPI Backend (api/main.py)
        ↓  session state management
LangGraph Agent (servicehive_agent/)
        ├── Intent Detection  → LLM classifies: greeting / product_query / high_intent
        ├── RAG Pipeline      → FAISS + Google Embeddings → knowledge_base.json
        ├── Onboarding FSM    → explicit state machine: name → email → platform → save
        ├── Info Extractor    → LLM extracts name/plan/platform with conversation history
        └── Lead Database     → in-memory dict keyed by email+platform
```

### Why LangGraph?

LangGraph was chosen over AutoGen because:
- It gives **full control over the agent's state** at every step via `AgentState`
- The **explicit graph structure** (nodes + edges) makes the flow auditable and debuggable
- It integrates cleanly with LangChain's RAG and LLM abstractions
- State is retained across turns naturally — no workarounds needed

### State Management

Each conversation session maintains an `AgentState` TypedDict that tracks:
- `history` — full conversation (last 8 turns sent to LLM for context)
- `user_name`, `email`, `platform`, `selected_plan` — lead data
- `stage` — current onboarding step (`None` → `collecting_name` → `collecting_email` → `collecting_platform` → `done`)
- `lead_ready` — whether the lead has been captured

---

## 📁 Project Structure

```
ServiceHive/                          ← Root folder
│
├── servicehive_agent/                ← Core agent (LangGraph + RAG)
│   │
│   ├── agent/
│   │   ├── state.py                  ← AgentState TypedDict
│   │   ├── llm.py                    ← Groq LLM setup
│   │   ├── intent.py                 ← LLM-based intent classifier
│   │   ├── extractor.py              ← LLM info extractor + email regex
│   │   ├── planner.py                ← Main agent brain + onboarding FSM
│   │   └── graph.py                  ← LangGraph StateGraph definition
│   │
│   ├── rag/
│   │   ├── loader.py                 ← Loads knowledge_base.json into Documents
│   │   ├── embedder.py               ← Google Generative AI Embeddings
│   │   ├── vector_store.py           ← FAISS index (load or build)
│   │   └── retriever.py              ← Similarity search retriever
│   │
│   ├── tools/
│   │   └── lead_capture.py           ← mock_lead_capture() function
│   │
│   ├── utils/
│   │   └── db.py                     ← In-memory lead database
│   │
│   ├── data/
│   │   ├── knowledge_base.json       ← Plans, policies, general info
│   │   └── vector_store/             ← Saved FAISS index (auto-generated)
│   │
│   └── app.py                        ← CLI runner (for testing without UI)
│
├── backend/
│   ├── __init__.py
│   └── main.py                       ← FastAPI app (sessions, /chat, /leads)
│
├── frontend/
│   └── streamlit_app.py              ← Streamlit chat UI
│
├── .env                              ← API keys (never commit this)
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

- Python **3.9 or higher**
- A **Groq API key** (free) — for the LLaMA 3.1 language model
- A **Google API key** — for the embedding model (Gemini Embeddings)

---

## 🔑 Getting API Keys

### Groq API Key (Free)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to **API Keys** → **Create API Key**
4. Copy your key

### Google API Key (for Embeddings)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API Key** → **Create API Key**
4. Copy your key

---

## 🚀 Getting Started

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd ServiceHive
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

Create a `.env` file in the **root `ServiceHive/` folder**:

```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

### Step 5 — Build the vector store (first run only)

The first time you run the backend, it will automatically build the FAISS vector store from `knowledge_base.json` and save it to `servicehive_agent/data/vector_store/`. This takes ~10 seconds. Every subsequent run loads it from disk instantly.

---

## ▶️ Running the Application

You need **two terminals** open simultaneously.

### Terminal 1 — Start the FastAPI Backend

```bash
# From the ServiceHive/ root folder
uvicorn backend.main:app --reload --port 8000
```

Expected output:
```
[RAG] Loading existing vector store...
[RAG] Vector store loaded successfully.
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2 — Start the Streamlit Frontend

```bash
# From the ServiceHive/ root folder
streamlit run frontend/streamlit_app.py
```

Streamlit will open your browser automatically at **http://localhost:8501**

---

## 🖥️ Using the Web Interface

### Chat Panel (main area)
- Type your message in the input box and click **Send →**
- The agent will respond based on intent:
  - **Greetings** → friendly welcome
  - **Plan / pricing questions** → answers from knowledge base
  - **High intent** (e.g. "sign me up", "how do I get this plan") → starts onboarding

### Session Status (sidebar)
Live tracker showing the current onboarding stage, name, email, platform, and plan as they are collected. Shows a green **"Lead Captured"** badge when registration completes.

### Lead Database (sidebar)
- Shows all captured leads in a table
- Filter by **Basic Plan** or **Pro Plan**
- Click **Refresh Leads** to update manually

### New Conversation
Click **🔄 New Conversation** to start fresh (resets both frontend and backend session).

---

## 🧪 Testing via CLI (without UI)

```bash
cd servicehive_agent
python app.py
```

---

## 📡 API Reference

The FastAPI backend exposes these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message, receive agent reply |
| `POST` | `/reset/{session_id}` | Reset a session to initial state |
| `GET` | `/leads` | Get all captured leads |
| `GET` | `/leads?plan=Basic Plan` | Filter leads by plan name |
| `GET` | `/health` | Health check |

Interactive API docs available at: **http://localhost:8000/docs**

### Example `/chat` request

```json
POST /chat
{
  "session_id": "abc-123",
  "message": "I want to sign up for the Pro plan"
}
```

### Example `/chat` response

```json
{
  "session_id": "abc-123",
  "reply": "Great for the Pro Plan! Let's get you signed up. What's your name?",
  "stage": "collecting_name",
  "user_name": null,
  "email": null,
  "platform": null,
  "selected_plan": "Pro Plan",
  "lead_ready": false
}
```

---

## 💬 WhatsApp Integration (Webhook Approach)

To deploy this agent on WhatsApp:

1. **Create a Meta Developer App** at [developers.facebook.com](https://developers.facebook.com) and enable the WhatsApp Business API.

2. **Set up a webhook** that Meta will call every time a user sends a message. Your FastAPI backend is already ready for this — just add a new route:

```python
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict):
    phone = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    text  = payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

    # Use phone number as session_id
    result = process_chat(session_id=phone, message=text)

    # Send reply back via WhatsApp Cloud API
    send_whatsapp_message(to=phone, text=result["reply"])
    return {"status": "ok"}
```

3. **Expose your local server** using [ngrok](https://ngrok.com):
```bash
ngrok http 8000
```

4. **Register the ngrok URL** as your webhook in the Meta Developer Console under WhatsApp → Configuration → Webhook.

5. **Verify the webhook** with a verify token — Meta sends a `GET` request with a `hub.challenge` that your server must echo back.

---

## 📦 requirements.txt

```
langchain
langchain-groq
langchain-google-genai
langchain-community
langgraph
faiss-cpu
fastapi
uvicorn
streamlit
requests
python-dotenv
pydantic
```

---

## 🧠 Knowledge Base

The agent answers questions from `servicehive_agent/data/knowledge_base.json`:

| Category | Contents |
|----------|----------|
| Plans | Basic Plan ($29/mo), Pro Plan ($79/mo) with full feature lists |
| Policies | Refund policy (7-day window), 24/7 support (Pro only) |
| General | What AutoStream is, supported platforms |

To add more information, edit `knowledge_base.json` and **delete the `data/vector_store/` folder** so it rebuilds on next startup.

---

## 🔮 Evaluation Criteria Coverage

| Criterion | Implementation |
|-----------|---------------|
| Agent reasoning & intent detection | LLM classifier with 8-turn conversation history |
| Correct use of RAG | FAISS + Google Embeddings + LangChain retriever |
| Clean state management | LangGraph `AgentState` TypedDict, explicit FSM |
| Proper tool calling logic | `mock_lead_capture()` fires only after all 3 fields collected |
| Code clarity & structure | Modular: `agent/`, `rag/`, `tools/`, `utils/`, `api/`, `frontend/` |
| Real-world deployability | FastAPI backend + Streamlit UI + WhatsApp webhook guide |

---

## 👤 Author

Built by **Krit Prasad** as part of the ServiceHive Machine Learning Internship Assignment.

---

## 📄 License

This project is submitted as an internship assignment for **ServiceHive / Inflx**. All rights reserved.

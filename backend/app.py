"""
FastAPI backend for the CRA Tax Support Agent.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Ensure .env is loaded from project root
load_dotenv(Path(__file__).parent.parent / ".env")

from .database import (
    create_session,
    list_sessions,
    get_session,
    delete_session,
    add_message,
    update_session_state,
    get_session_state,
    update_session_title,
    create_reminder,
    list_reminders,
)
from .orchestrator import process_message, call_action

app = FastAPI(title="CRA Tax Support Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (npm run build → frontend/dist)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SessionCreate(BaseModel):
    title: str = "New Chat"


class ActionRequest(BaseModel):
    action: str
    params: dict


class ReminderRequest(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    frequency: str = "one-time"
    delivery: str = "email"
    next_date: str = ""


# --- Sessions ---

@app.get("/api/sessions")
def api_list_sessions():
    return list_sessions()


@app.post("/api/sessions")
def api_create_session(body: SessionCreate):
    return create_session(body.title)


@app.get("/api/sessions/{session_id}")
def api_get_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.delete("/api/sessions/{session_id}")
def api_delete_session(session_id: str):
    if not delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


# --- Chat ---

@app.post("/api/chat")
def api_chat(body: ChatRequest):
    session = get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    add_message(body.session_id, "user", body.message)

    # Load conversation state
    state = get_session_state(body.session_id)
    if not state.get("action"):
        state = {"action": None, "params": {}, "awaiting": None}

    # Build conversation history from previous messages (for multi-turn context)
    conversation_history = []
    for msg in session.get("messages", []):
        if msg["role"] in ("user", "assistant"):
            conversation_history.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    # Process through orchestrator
    try:
        response_text, sources = process_message(body.message, state, conversation_history=conversation_history)
    except Exception as e:
        response_text = "Sorry, I encountered an error processing your request. Please try again."
        sources = None

    # Guard against None response
    if not response_text:
        response_text = "Sorry, I couldn't generate a response. Please try again."

    # Save assistant message
    add_message(body.session_id, "assistant", response_text, sources)

    # Persist conversation state
    update_session_state(body.session_id, state)

    # Auto-title on first message
    if len(session.get("messages", [])) == 0:
        title = body.message[:50] + ("..." if len(body.message) > 50 else "")
        update_session_title(body.session_id, title)

    return {
        "response": response_text,
        "sources": sources,
        "state": {
            "action": state.get("action"),
            "awaiting": state.get("awaiting"),
        },
    }


@app.post("/api/action")
def api_action(body: ActionRequest):
    """Call an action directly, bypassing intent classification."""
    try:
        result = call_action(body.action, body.params)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reminders")
def api_create_reminder(body: ReminderRequest):
    reminder = create_reminder(
        name=body.name,
        email=body.email,
        phone=body.phone,
        frequency=body.frequency,
        delivery=body.delivery,
        next_date=body.next_date,
    )
    return reminder


@app.get("/api/reminders")
def api_list_reminders():
    return list_reminders()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# --- Serve Frontend ---
# Mount static assets (JS, CSS, images) if frontend is built
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        """Catch-all: serve index.html for client-side routing."""
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")

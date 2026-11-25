
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from llm_service import API_KEYS

from time import perf_counter

from schemas import ChatRequest
from crud import save_conversation
from llm_service import generate_response
from dotenv import load_dotenv

from database import Base, engine, get_db
from crud import (
    get_session_messages,
    format_session_messages
)

from fastapi import Header

import models

import litellm

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LYFTR AI Chatbot API",
    lifespan=lifespan
)

load_dotenv()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173, http://localhost:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Simulate-Failure"]
)



@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        keys_configured = len(API_KEYS)
        cache_enabled = litellm.cache is not None

        if keys_configured < 2 or not cache_enabled:
            raise HTTPException(
                status_code=503,
                detail="service not ready"
            )

        return {
            "status": "ok",
            "keys_configured": keys_configured,
            "cache_enabled": cache_enabled
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="service not ready"
        )

@app.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    messages = get_session_messages(
        db,
        session_id
    )

    if not messages:
        raise HTTPException(
            status_code=404,
            detail="session not found"
        )

    return {
        "session_id": session_id,
        "messages": format_session_messages(messages)
    }

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    x_simulate_failure: str | None = Header(default=None)
):
    start_time = perf_counter()

    # Retrieve previous messages from SQLite
    history = get_session_messages(
        db,
        request.session_id
    )

    # Construct the complete LLM conversation
    messages = [
        {
            "role": "system",
            "content": (
                request.system_prompt
                or "You are a helpful AI assistant."
            )
        }
    ]

    # Add previous conversation history
    for previous in history:
        messages.append({
            "role": previous.role,
            "content": previous.content
        })

    # Add the latest user message
    messages.append({
        "role": "user",
        "content": request.message
    })

    try:
        # Generate a real AI response
        result = generate_response(messages, simulate_failure=x_simulate_failure)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="all providers unavailable"
        )

    # Measure response latency
    latency_ms = int(
        (perf_counter() - start_time) * 1000
    )

    # Construct response metadata
    
    metadata = {
        "resolution_source": result["resolution_source"],
        "model": result["model"],
        "latency_ms": latency_ms,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "key_id": result["key_id"],
        "fallback_attempts": result["fallback_attempts"]
    }


    # Store the successful conversation
    save_conversation(
        db=db,
        session_id=request.session_id,
        user_message=request.message,
        assistant_reply=result["reply"],
        metadata=metadata
    )

    return {
        "session_id": request.session_id,
        "reply": result["reply"],
        "metadata": metadata
    }

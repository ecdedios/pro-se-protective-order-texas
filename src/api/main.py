"""
FastAPI app — intake endpoints. Session-based state, minimal retention
per architecture doc §4.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from src.agent.orchestrator import IntakeOrchestrator

app = FastAPI(title="TX Pro Se Protective Order Agent")
orchestrator = IntakeOrchestrator()


class ConversationState(BaseModel):
    session_id: str
    answers: dict = {}


class ProceduralQuestion(BaseModel):
    session_id: str
    question: str
    county: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/intake/next-question")
def next_question(state: ConversationState) -> dict:
    return orchestrator.next_question(state.model_dump())


@app.post("/intake/ask")
def ask_procedural_question(payload: ProceduralQuestion) -> dict:
    return orchestrator.answer_procedural_question(payload.question, payload.county)

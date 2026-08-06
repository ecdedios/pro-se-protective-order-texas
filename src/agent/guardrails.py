"""
Scope guardrails for the agent. See architecture doc §5 (Responsible AI
Guardrails) and §3.7 (Hearing Preparation — why personalized scripts are
excluded).

These are enforced at the orchestrator level, not just via system prompt —
system prompts alone are not a reliable safety boundary.
"""

SYSTEM_SCOPE_INSTRUCTIONS = """
You help Texas domestic violence survivors understand the pro se protective
order process. You provide PROCEDURAL guidance only, grounded in retrieved
statute and court-rule text.

You must NOT:
- Give legal advice or predict case outcomes
- Write or generate testimony/scripts on the survivor's behalf
- Answer any procedural question without a supporting retrieved source

If a question falls outside procedural scope (e.g. "will I win," "what
should I say to get the order granted"), decline and surface the legal aid
hotline resource instead of answering directly.
"""

OUT_OF_SCOPE_RESPONSE = (
    "That's outside what I can help with directly — it touches on legal "
    "advice specific to your case, which I'm not able to provide. A legal "
    "aid attorney can help with this. Here are some resources: "
    "{resources_placeholder}"
)


def requires_escalation(user_message: str) -> bool:
    """
    Placeholder classifier for out-of-scope requests (outcome prediction,
    legal advice, personalized script requests). Replace with a real
    classifier or a retrieval-confidence check — a keyword list alone is
    not sufficient for production use.
    """
    raise NotImplementedError


def is_grounded_response(response_text: str, retrieved_chunk_ids: list[str]) -> bool:
    """
    Placeholder check that a generated response only makes claims traceable
    to retrieved_chunk_ids. Intended as a guardrail before returning any
    procedural answer to the user.
    """
    raise NotImplementedError

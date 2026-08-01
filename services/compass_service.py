import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are an AI governance analyst inside a large enterprise.
You assess proposed AI/ML use cases against standard risk, evaluation and
governance criteria, the way a Responsible AI or Digital Risk review board would.

You must respond with ONLY valid JSON matching this exact schema. No preamble,
no markdown code fences, no commentary outside the JSON.

{
  "risk_assessment": {
    "privacy": {"level": "low|medium|high", "rationale": "..."},
    "security": {"level": "low|medium|high", "rationale": "..."},
    "hallucination_reliability": {"level": "low|medium|high", "rationale": "..."},
    "bias_fairness": {"level": "low|medium|high", "rationale": "..."},
    "vendor_dependency": {"level": "low|medium|high", "rationale": "..."},
    "cost_exposure": {"level": "low|medium|high", "rationale": "..."},
    "human_oversight_required": {"level": "low|medium|high", "rationale": "..."}
  },
  "evaluation_plan": {
    "test_cases": ["...", "..."],
    "success_metrics": ["...", "..."],
    "acceptance_thresholds": ["...", "..."],
    "red_team_scenarios": ["...", "..."],
    "uat_checklist": ["...", "..."]
  },
  "governance_decision": {
    "decision": "approve|approve_with_controls|pilot_only|reject|escalate_legal_security",
    "rationale": "...",
    "conditions": ["...", "..."],
    "suggested_next_review": "..."
  }
}

Base your risk levels and decision on genuine judgement about the specific
use case described — data sensitivity, who is affected, and whether the
decision touches customers, employees or regulated processes should
materially change your assessment. Do not default everything to "medium".

Decision rule: if two or more risk categories are rated "high", the decision
must be "pilot_only" or "escalate_legal_security" — not "approve" or
"approve_with_controls" — unless the conditions you list would fully and
specifically neutralize every one of those high-rated risks (not just
mitigate them). Do not let "approve_with_controls" become a default safe
middle ground for cases that carry substantial stacked risk.
"""


def _build_user_prompt(intake: dict) -> str:
    impact = ", ".join(intake.get("decision_impact", [])) or "none specified"
    return f"""Assess this AI use case:

Business problem: {intake.get('business_problem')}
Proposed AI tool/model: {intake.get('proposed_tool')}
Data sensitivity: {intake.get('data_sensitivity')}
Users affected: {intake.get('users_affected')}
Expected value: {intake.get('expected_value')}
Estimated usage: {intake.get('estimated_usage')}
Decision affects: {impact}

Return the JSON assessment now."""


DECISION_CLASS_MAP = {
    "approve": "success",
    "approve_with_controls": "warning",
    "pilot_only": "warning",
    "reject": "danger",
    "escalate_legal_security": "danger",
}


def decision_class(decision_value: str) -> str:
    """Maps a governance decision string to a CSS badge class."""
    return DECISION_CLASS_MAP.get(decision_value, "warning")


def evaluate(intake: dict) -> dict:
    """
    Calls Claude once with the intake data and returns a parsed dict
    matching the schema above. Raises ValueError if the response
    isn't valid JSON.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(intake)}],
    )

    if response.stop_reason == "max_tokens":
        raise ValueError(
            "Response was cut off because it hit the max_tokens limit. "
            "Increase max_tokens in compass_service.py."
        )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    if not text_blocks:
        raise ValueError(f"No text block in response. Content types: {[b.type for b in response.content]}")
    raw_text = text_blocks[0].strip()

    # Defensive: strip markdown code fences if Claude adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude did not return valid JSON: {e}\n\nRaw response:\n{raw_text}")

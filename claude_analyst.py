"""
claude_analyst.py — Claude-powered analysis for RAI Compliance Assistant.

Two jobs:
  1. characterize_system()       — RAI risk profile (autonomy level, highest-risk principle)
  2. generate_rai_narrative()    — draft compliance narrative for one RAI criterion
"""

from __future__ import annotations

import json
import re

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MAX_TOKENS, CLAUDE_MODEL


class AnalystError(Exception):
    pass


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def characterize_system(
    name: str,
    description: str,
    intended_users: str,
    data_sources: str,
    deployment_context: str,
) -> dict:
    """
    Analyze an AI system and determine its RAI risk profile.

    Returns:
      {
        "autonomy_level": "Low" | "Medium" | "High" | "Critical",
        "highest_risk_principle": "Responsible" | "Equitable" | "Traceable" | "Reliable" | "Governable",
        "priority_criteria": ["RE-1", "TR-1", ...],   # up to 4 highest-priority criteria IDs
        "rationale": str
      }
    Raises AnalystError on failure.
    """
    prompt = f"""You are a DoD AI governance expert specializing in the DoD AI Ethical Principles (2020) and CDAO Responsible AI guidance.

Analyze the following AI system and determine its Responsible AI (RAI) risk profile.

SYSTEM NAME: {name}
DESCRIPTION: {description}
INTENDED USERS: {intended_users}
DATA SOURCES: {data_sources}
DEPLOYMENT CONTEXT: {deployment_context}

The DoD's five RAI principles are:
- Responsible (RE): Human accountability for AI decisions and harms
- Equitable (EQ): Minimizing unintended bias in data, models, and outcomes
- Traceable (TR): Auditable, explainable, documented AI behavior
- Reliable (RL): Consistent, tested, monitored performance
- Governable (GO): Human override, controlled updates, scope constraints

The 20 RAI criteria IDs are: RE-1, RE-2, RE-3, RE-4, EQ-1, EQ-2, EQ-3, EQ-4, TR-1, TR-2, TR-3, TR-4, RL-1, RL-2, RL-3, RL-4, GO-1, GO-2, GO-3, GO-4.

Autonomy levels:
- Low: Human makes all decisions; AI provides information or analysis only
- Medium: AI recommends actions; human reviews and approves each
- High: AI acts autonomously within defined scope; human oversight periodic
- Critical: AI acts autonomously in high-stakes domain; errors can cause serious harm

Return ONLY valid JSON (no markdown):
{{
  "autonomy_level": "Medium",
  "highest_risk_principle": "Traceable",
  "priority_criteria": ["TR-1", "TR-2", "GO-1", "RE-3"],
  "rationale": "2-3 sentences explaining the autonomy level and why the identified principle poses the highest risk for this specific system."
}}"""

    try:
        response = _get_client().messages.create(
            model=CLAUDE_MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        result = json.loads(_strip_fences(raw))
    except json.JSONDecodeError as exc:
        raise AnalystError(f"Claude returned invalid JSON: {exc}") from exc
    except Exception as exc:
        raise AnalystError(f"Claude API error: {exc}") from exc

    for field in ("autonomy_level", "highest_risk_principle", "priority_criteria", "rationale"):
        if field not in result:
            raise AnalystError(f"Claude response missing field: {field}")

    return result


def generate_rai_narrative(
    system_name: str,
    system_description: str,
    criterion_id: str,
    criterion_title: str,
    criterion_description: str,
    criterion_guidance: str,
    implementation_notes: str = "",
) -> str:
    """
    Generate a draft RAI compliance narrative for one criterion.

    Returns plain text (2-4 paragraphs). Raises AnalystError on failure.
    """
    notes_section = (
        f"\nAdditional context from the system owner: {implementation_notes}"
        if implementation_notes else ""
    )

    prompt = f"""You are a DoD AI governance analyst writing a Responsible AI compliance narrative for a formal AI system assessment.

Write a compliance narrative for the RAI criterion below. The narrative describes HOW this specific AI system addresses this criterion — be specific to the system, not generic.

SYSTEM: {system_name}
SYSTEM DESCRIPTION: {system_description}{notes_section}

CRITERION: {criterion_id} — {criterion_title}
CRITERION REQUIREMENT: {criterion_description}
IMPLEMENTATION GUIDANCE: {criterion_guidance}

Write 2-4 paragraphs in formal government technical writing style. Include:
1. How this specific system addresses this criterion (specific mechanisms, policies, design decisions)
2. Who is responsible for maintaining compliance with this criterion
3. Evidence or artifacts that would demonstrate compliance to an assessor
4. Any known gaps or areas requiring improvement

Do NOT use markdown formatting. Write in plain prose. Be specific to this system — do not write generic boilerplate.
Do NOT claim the system is fully compliant if the implementation notes suggest otherwise.
The narrative is a factual description of the current state, not a marketing document."""

    try:
        response = _get_client().messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as exc:
        raise AnalystError(f"Claude API error: {exc}") from exc

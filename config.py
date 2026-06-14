"""config.py — Responsible AI Compliance Assistant configuration."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_MAX_TOKENS = 4000

# --- App ---
APP_TITLE = "RAI Compliance Assistant"
APP_SUBTITLE = "DoD Responsible AI Principles Assessment Tool"
DEMO_MODE = True
DEMO_BANNER = "DEMONSTRATION ONLY — SYNTHETIC DATA — NOT FOR OPERATIONAL USE"
DATABASE_URL = "sqlite:///./rai_compliance.db"

# --- Autonomy levels (used for risk characterization) ---
AUTONOMY_LEVELS = ["Low", "Medium", "High", "Critical"]

AUTONOMY_DESCRIPTIONS = {
    "Low":      "Human makes all decisions; AI provides information or analysis only",
    "Medium":   "AI recommends actions; human reviews and approves each recommendation",
    "High":     "AI acts autonomously within defined scope; human oversight is periodic",
    "Critical": "AI acts autonomously in high-stakes domain; errors can cause serious harm",
}

# --- Criterion assessment statuses ---
CRITERION_STATUSES = {
    "met":           "Met",
    "partial":       "Partial",
    "not_addressed": "Not Addressed",
    "not_applicable":"Not Applicable",
}

# --- RAI principles ---
RAI_PRINCIPLES = {
    "RE": "Responsible",
    "EQ": "Equitable",
    "TR": "Traceable",
    "RL": "Reliable",
    "GO": "Governable",
}

# RAI Compliance Assistant

**DoD Responsible AI Principles Assessment Tool**

Helps AI vendors and defense contractors assess whether an AI system meets the DoD's five Responsible AI principles and generates supporting compliance documentation.

**Live demo:** [rai-compliance.onrender.com](https://rai-compliance.onrender.com)

---

## What It Does

Register an AI system → Claude characterizes its autonomy level and highest-risk principle → Work through 20 criteria across five principles → Generate Claude-drafted compliance narratives for each criterion → Export an RAI Assessment Report.

## The Five DoD AI Ethical Principles (2020)

| Code | Principle | Focus |
|------|-----------|-------|
| RE | **Responsible** | Human accountability for AI decisions and harms |
| EQ | **Equitable** | Minimizing unintended bias in data, models, and outcomes |
| TR | **Traceable** | Auditable, explainable, documented AI behavior |
| RL | **Reliable** | Consistent, tested, monitored performance |
| GO | **Governable** | Human override, controlled updates, scope constraints |

Twenty sub-criteria (four per principle) derived from the DoD AI Ethical Principles (Feb 2020) and CDAO Responsible AI guidance.

## How Claude Is Used — and How It Isn't

**Claude does:**
- Analyze the system description to identify autonomy level and highest-risk principle
- Draft compliance narratives for individual criteria (the "why this system addresses this criterion" text)

**Claude does not:**
- Make the compliance determination (Met / Partial / Not Addressed) — that's a human decision
- Determine whether a system is RAI-compliant overall — the engine computes the score from human-entered statuses

This is the same pattern used across all seven projects in this portfolio: the rules engine determines, Claude writes prose, human confirms.

## The Meta-Story

This tool makes explicit a design pattern already implicit across all seven portfolio projects:

| Pattern | Example |
|---------|---------|
| Rules engine determines, Claude drafts prose | ATO Accelerator: FIPS 199 + SSP narratives |
| Human confirmation before any consequential action | CFIUS Screener: parse → confirm → screen |
| Every output labeled AI-generated | All Claude-calling projects |
| Honest limitations sections | CFIUS memo, GhostTrace reports |
| Pinned model versions, no silent updates | `claude-haiku-4-5-20251001` in every config.py |
| Bounded agentic loops | GhostTrace Deep Trace: max 5 tool calls |

The RAI criteria in this tool (especially TR-4, GO-2) describe what this portfolio already does.

## Demo Systems

**SENTINEL Influence Operations Detection Engine** (Medium autonomy, highest risk: Equitable)
Based on Project 5. The interesting RAI tension: the DISARM TTP taxonomy that defines "influence operation" is itself a classification that encodes editorial judgment about adversary behavior — an EQ-1 bias question.

**GhostTrace Deep Trace Agentic Loop** (High autonomy, highest risk: Governable)
Based on Project 6's agentic loop. The `max_tool_calls=5` ceiling in the code is GO-1 (human override) implemented as a constraint rather than a policy. The pre-seeded GO-1 narrative walks through exactly why this is partially but not fully compliant.

## User Flow

1. **Register** an AI system (name, description, users, data sources, deployment context)
2. **Characterize** — Claude determines autonomy level and flags highest-risk principle
3. **Assess** — Work through 20 criteria; set each to Met / Partial / Not Addressed / Not Applicable
4. **Generate** — For any criterion, Claude drafts a compliance narrative based on your notes
5. **Report** — RAI Assessment Report shows score by principle, open gaps, and a POA&M

## Tech Stack

- **Backend:** Python + FastAPI + SQLAlchemy 2.0 + SQLite
- **AI:** Claude Haiku (`claude-haiku-4-5-20251001`) — characterization + narrative drafting only
- **Frontend:** Jinja2 templates + vanilla CSS (no CDN — air-gap safe)
- **Deployment:** Render free tier
- **Tests:** 29 passing (pytest)

## Honest Limitations

- Criteria are derived from public DoD guidance; verify against current CDAO publications before formal use
- Claude's compliance narratives are drafts — review and edit before including in formal documentation
- RAI score is a percentage of criteria marked Met or N/A; it is not a legal determination of compliance
- No authentication — add SSO before any organizational deployment
- SQLite on Render is ephemeral — database resets on every cold start (demo data reloads automatically)
- Part of a demonstration portfolio; not a commercial product

## Running Locally

```bash
git clone https://github.com/JakPot42/rai-compliance
cd rai-compliance
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Optional: set ANTHROPIC_API_KEY for live Claude calls
uvicorn main:app --reload
```

Open http://localhost:8000 — demo data loads automatically on first start.

## Project Context

Project 9 of the JakPot42 defense AI portfolio. Companion projects:

- [SEAD 3 Auditor](https://github.com/JakPot42/sead3-auditor) — Personnel security compliance
- [SAM.gov Agent](https://github.com/JakPot42/sam-acquisition-agent) — Acquisition intelligence
- [FriendShore](https://github.com/JakPot42/friendshore-supply-chain) — Supply chain risk
- [ATO Accelerator](https://github.com/JakPot42/ato-accelerator) — NIST 800-53 / RMF compliance
- [SENTINEL](https://github.com/JakPot42/sentinel-io-engine) — Influence operations detection
- [GhostTrace](https://github.com/JakPot42/ghosttrace) — Hidden ownership & shell company tracing
- [CFIUS Screener](https://github.com/JakPot42/cfius-screener) — Foreign investment screening

---

*DEMONSTRATION ONLY — not for operational use — verify against official DoD and CDAO guidance*

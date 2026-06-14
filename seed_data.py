"""
seed_data.py — Two demo AI systems for RAI Compliance Assistant.

These are fictionalized versions of systems from the JakPot42 portfolio,
used as case studies to demonstrate the RAI assessment pattern.

System A: SENTINEL Influence Operations Detection Engine (medium autonomy)
System B: GhostTrace Deep Trace Agentic Loop (high autonomy)
"""

from __future__ import annotations

DEMO_SYSTEMS = [
    {
        "name": "SENTINEL Influence Operations Detection Engine",
        "description": (
            "Monitors adversary media outlets (RT, Sputnik, TASS, Global Times) and "
            "Reddit for coordinated influence operations. Clusters articles by narrative "
            "similarity, classifies DISARM framework Tactics, Techniques, and Procedures "
            "(TTPs), and generates structured intelligence assessments for analyst review. "
            "All assessments are reviewed by a human intelligence analyst before dissemination."
        ),
        "system_owner": "Capt. Marcus Webb, J2 Intelligence Section",
        "intended_users": "Intelligence analysts, J2 staff, SOC operators",
        "data_sources": "RSS feeds from public adversary media; Reddit public API; DISARM TTP taxonomy",
        "deployment_context": (
            "Web application deployed on Render. Analysts access via browser. "
            "No autonomous dissemination — all intelligence reports require analyst approval before release."
        ),
        "autonomy_level": "Medium",
        "highest_risk_principle": "Equitable",
        "priority_criteria": ["EQ-1", "TR-2", "RL-2", "GO-1"],
        "characterization_rationale": (
            "SENTINEL operates at Medium autonomy: it identifies and classifies potential "
            "influence operations automatically, but a human analyst reviews every "
            "assessment before it is disseminated. The highest RAI risk is Equitable — "
            "the definition of what constitutes an 'adversary' narrative is baked into "
            "the system's DISARM training signal, creating a potential source of political "
            "or geographic bias that could skew threat detection toward certain regions "
            "or narrative types."
        ),
        "criterion_statuses": {
            "RE-1": "met",
            "RE-2": "met",
            "RE-3": "partial",
            "RE-4": "partial",
            "EQ-1": "not_addressed",
            "EQ-2": "not_addressed",
            "EQ-3": "partial",
            "EQ-4": "not_addressed",
            "TR-1": "partial",
            "TR-2": "partial",
            "TR-3": "met",
            "TR-4": "met",
            "RL-1": "met",
            "RL-2": "partial",
            "RL-3": "partial",
            "RL-4": "met",
            "GO-1": "met",
            "GO-2": "met",
            "GO-3": "partial",
            "GO-4": "partial",
        },
        "sample_narrative": {
            "criterion_id": "TR-3",
            "narrative": (
                "SENTINEL's data provenance is grounded in publicly accessible sources with "
                "stable, documented origins. All monitored RSS feeds are sourced from official "
                "publications of the tracked media outlets (RT, Sputnik, TASS, Global Times, "
                "and Reddit's public API). Feed URLs are hardcoded in the source configuration "
                "and versioned in the GitHub repository, ensuring that any change to a data "
                "source is captured in the commit history. The DISARM TTP taxonomy used for "
                "classification is maintained by the public DISARM Foundation and referenced "
                "by version tag.\n\n"
                "At inference time, each ingested article is stored in the SQLite database "
                "with its source URL, publication timestamp, and the feed it was retrieved "
                "from. This metadata persists alongside the classification result, allowing "
                "an analyst or auditor to retrieve the original article text for any "
                "classification the system produced. Article text is not modified before "
                "classification — the system operates on raw feed content.\n\n"
                "Current gap: SENTINEL uses Claude Haiku to generate the final intelligence "
                "assessment narrative. The model version (claude-haiku-4-5-20251001) is "
                "pinned in config.py, satisfying TR-4's minimum version tracking requirement. "
                "However, the prompt used to generate narratives is not versioned independently "
                "of the code — a future improvement would version prompts as configuration "
                "artifacts so that prompt changes are as traceable as model version changes."
            ),
        },
    },
    {
        "name": "GhostTrace Deep Trace Agentic Loop",
        "description": (
            "Bounded agentic system that autonomously investigates corporate entities "
            "for hidden ownership, shell company indicators, and OFAC SDN sanctions exposure. "
            "Given a target entity, the system makes up to 5 sequential tool calls "
            "(investigate_entity, search_cached_filings) against SEC EDGAR data, builds "
            "an ownership graph, computes a risk score, and generates a findings report. "
            "The system operates within a strict 5-call ceiling and cannot exceed its "
            "defined tool inventory."
        ),
        "system_owner": "Dr. Priya Nair, Financial Intelligence Unit",
        "intended_users": (
            "Financial crime analysts, due diligence officers, CFIUS practitioners, "
            "compliance teams at financial institutions"
        ),
        "data_sources": (
            "SEC EDGAR filings (SC 13D/13G, 10-K Exhibit 21, DEF 14A); "
            "OFAC SDN list (sdn.csv, alt.csv); cached filing database"
        ),
        "deployment_context": (
            "Web application deployed on Render. Analyst initiates a deep trace via "
            "POST /trace/{id}/deep-trace. System runs autonomously for up to 5 tool calls "
            "then returns a report. Analyst reviews report before any action is taken. "
            "DEMO_MODE=True — all outputs watermarked for demonstration use only."
        ),
        "autonomy_level": "High",
        "highest_risk_principle": "Governable",
        "priority_criteria": ["GO-1", "TR-1", "RL-2", "RE-3"],
        "characterization_rationale": (
            "GhostTrace Deep Trace operates at High autonomy: it takes a sequence of "
            "investigative actions — tool calls against live data sources — without human "
            "approval at each step. The highest RAI risk is Governable, because the "
            "system's autonomous multi-step action loop is precisely where loss of human "
            "control would have the most significant consequences. The 5-call ceiling "
            "partially addresses this, but the system currently lacks a mid-run pause "
            "or human confirmation mechanism."
        ),
        "criterion_statuses": {
            "RE-1": "met",
            "RE-2": "met",
            "RE-3": "partial",
            "RE-4": "partial",
            "EQ-1": "not_applicable",
            "EQ-2": "not_applicable",
            "EQ-3": "partial",
            "EQ-4": "not_addressed",
            "TR-1": "partial",
            "TR-2": "partial",
            "TR-3": "met",
            "TR-4": "met",
            "RL-1": "met",
            "RL-2": "met",
            "RL-3": "partial",
            "RL-4": "met",
            "GO-1": "met",
            "GO-2": "met",
            "GO-3": "met",
            "GO-4": "partial",
        },
        "sample_narrative": {
            "criterion_id": "GO-1",
            "narrative": (
                "GhostTrace implements human override of the agentic loop through a combination "
                "of hard-coded ceiling constraints and architectural design. The Deep Trace "
                "function enforces a maximum of 5 tool calls per invocation (max_tool_calls=5 "
                "in deep_trace.py). Once this ceiling is reached, the loop exits regardless "
                "of the model's assessment of whether further investigation is warranted. "
                "This ceiling is not a configuration parameter — it is a code constant that "
                "requires a code change and redeployment to modify, ensuring it cannot be "
                "overridden by a prompt or user input.\n\n"
                "At the system level, the human analyst retains override authority over the "
                "investigation as a whole. The analyst initiates the Deep Trace via an explicit "
                "POST request; the system does not initiate autonomous investigation "
                "unprompted. The resulting report is presented to the analyst for review "
                "before any downstream action (e.g., OFAC screening, regulatory notification) "
                "is taken. The analyst can discard the report, dispute its findings, or "
                "initiate a new trace with different parameters at any point.\n\n"
                "Current gap: the 5-call ceiling provides a post-hoc bound but does not "
                "provide mid-run visibility or intervention capability. If the system is "
                "consuming unexpected data sources or producing intermediate results that "
                "appear erroneous, the analyst cannot pause the loop at step 3 without "
                "terminating it entirely. A future enhancement would surface intermediate "
                "tool call results to the analyst with an option to continue or halt, "
                "which would fully satisfy GO-1's requirement for accessible override "
                "in operational conditions."
            ),
        },
    },
]

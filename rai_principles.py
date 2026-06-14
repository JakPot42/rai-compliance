"""
rai_principles.py — DoD Responsible AI criteria catalog.

Twenty criteria across the five DoD AI Ethical Principles (2020):
  RE — Responsible
  EQ — Equitable
  TR — Traceable
  RL — Reliable
  GO — Governable

Source: DoD AI Ethical Principles (Feb 2020) + CDAO RAI guidance.
All 20 criteria apply to every AI system; autonomy level determines priority.
"""

from __future__ import annotations

CRITERIA: list[dict] = [
    # =========================================================================
    # RE — Responsible
    # =========================================================================
    {
        "id": "RE-1",
        "principle": "RE",
        "title": "Accountability Designation",
        "description": (
            "Named individual(s) with documented authority and responsibility for the AI "
            "system's behavior, outputs, and lifecycle decisions. Accountability chain is "
            "traceable from system to senior official."
        ),
        "guidance": (
            "Document who is responsible for the AI system in writing. This includes the "
            "AI system owner, the operator(s), and the senior official who authorizes "
            "deployment. Responsibility must be clear — 'the team' is not accountable, "
            "a named person is."
        ),
        "portfolio_example": (
            "ATO Accelerator: The ISSO and Authorizing Official (AO) are named in the "
            "System Security Plan before any system operates. Same principle here."
        ),
    },
    {
        "id": "RE-2",
        "principle": "RE",
        "title": "Consent and Notice",
        "description": (
            "Individuals or operators affected by AI-assisted decisions are informed that "
            "an AI system is involved, what it does, and how to seek human review of "
            "AI outputs that affect them."
        ),
        "guidance": (
            "At minimum: label AI-generated outputs as AI-generated. Where AI affects "
            "individuals (e.g., screening, scoring, classification), provide a mechanism "
            "for those individuals to know and to contest outcomes."
        ),
        "portfolio_example": (
            "All 7 portfolio projects display a DEMO banner and label Claude-generated "
            "content explicitly. SEAD 3 and CFIUS Screener show human-confirmation "
            "screens before acting on AI-parsed data."
        ),
    },
    {
        "id": "RE-3",
        "principle": "RE",
        "title": "Harm Reporting and Remediation",
        "description": (
            "Documented process for identifying, reporting, escalating, and remediating "
            "AI-caused harms, unexpected behaviors, or significant errors. Includes "
            "timelines and responsible parties."
        ),
        "guidance": (
            "Define: what counts as a reportable AI harm or failure? Who receives the "
            "report? What is the expected response time? How is the system corrected or "
            "suspended while investigation is underway?"
        ),
        "portfolio_example": (
            "GhostTrace and CFIUS Screener both display explicit 'Honest Limitations' "
            "sections — a lightweight version of this: telling users what can go wrong "
            "before it does."
        ),
    },
    {
        "id": "RE-4",
        "principle": "RE",
        "title": "Legal and Policy Review",
        "description": (
            "AI system reviewed by legal counsel and policy officials for compliance with "
            "applicable law, DoD Directive 3000.09, export control, privacy law, and "
            "use-case restrictions before operational deployment."
        ),
        "guidance": (
            "This is not a checkbox — it requires documented review by someone with "
            "legal authority to clear the system for its specific use case. Autonomous "
            "systems or systems touching lethal force require DAF/DAG-level review."
        ),
        "portfolio_example": (
            "CFIUS Screener: the deterministic jurisdiction engine cites 31 CFR Part 800 "
            "verbatim, and the tool explicitly states it is for screening assistance only "
            "— not legal advice. That disclaimer is RE-4 in action."
        ),
    },

    # =========================================================================
    # EQ — Equitable
    # =========================================================================
    {
        "id": "EQ-1",
        "principle": "EQ",
        "title": "Training Data Bias Assessment",
        "description": (
            "Training data and fine-tuning datasets assessed for demographic, geographic, "
            "linguistic, or population bias prior to model training or deployment. "
            "Assessment methodology and findings documented."
        ),
        "guidance": (
            "For systems using foundation models (e.g., Claude, GPT): document known "
            "bias properties of the underlying model and how they interact with your "
            "use case. You cannot ignore foundation model bias by saying 'we didn't train it.'"
        ),
        "portfolio_example": (
            "SENTINEL Influence Operations: if adversary media is the training signal, "
            "the definition of 'adversary' is itself a bias question. Who decided what "
            "counts as an influence operation?"
        ),
    },
    {
        "id": "EQ-2",
        "principle": "EQ",
        "title": "Fairness Metrics",
        "description": (
            "Quantitative fairness metrics defined and monitored in deployment. Metrics "
            "are specific to the use case (e.g., equal false positive rates across "
            "demographic groups, parity in classification outcomes)."
        ),
        "guidance": (
            "Fairness metrics must be defined BEFORE deployment, not discovered after a "
            "complaint. What does 'fair' mean for this system? Equal accuracy? Equal "
            "error rates? Equal representation in outcomes? Document the choice and why."
        ),
        "portfolio_example": (
            "SAM.gov Agent: if it ranks solicitations, does it systematically miss "
            "opportunities relevant to small or minority-owned businesses? That's EQ-2."
        ),
    },
    {
        "id": "EQ-3",
        "principle": "EQ",
        "title": "Diverse Evaluation Sets",
        "description": (
            "System evaluated against diverse, representative populations including edge "
            "cases and underrepresented groups relevant to the deployment context. "
            "Evaluation results documented and used to inform deployment decisions."
        ),
        "guidance": (
            "Your test set is a claim about the world. If you test on a narrow "
            "population, you're claiming the system works on that population. DoD systems "
            "often operate across diverse contexts — your eval should reflect that."
        ),
        "portfolio_example": (
            "FriendShore: does the supply chain risk engine perform equally well for "
            "suppliers in Latin America vs. Southeast Asia vs. Eastern Europe? That's EQ-3."
        ),
    },
    {
        "id": "EQ-4",
        "principle": "EQ",
        "title": "Disparate Impact Monitoring",
        "description": (
            "Ongoing monitoring in deployment for disproportionate error rates, harms, "
            "or adverse outcomes affecting specific populations. Thresholds for "
            "remediation action defined in advance."
        ),
        "guidance": (
            "Deployment changes distribution. Even a system that passed EQ-3 at "
            "launch may develop disparate impact over time as the population of users "
            "or inputs shifts. EQ-4 requires that someone is watching after launch."
        ),
        "portfolio_example": (
            "SEAD 3: if the disclosure parser systematically misclassifies reportable "
            "events for employees in certain job codes, that's disparate impact. "
            "EQ-4 requires catching it before it becomes a compliance failure."
        ),
    },

    # =========================================================================
    # TR — Traceable
    # =========================================================================
    {
        "id": "TR-1",
        "principle": "TR",
        "title": "Decision Audit Logs",
        "description": (
            "System produces persistent, tamper-evident logs of AI inputs, outputs, and "
            "key decision factors for every consequential AI decision. Logs retained "
            "for a defined period and accessible to authorized reviewers."
        ),
        "guidance": (
            "Log what went in, what came out, and when. For agentic systems, log each "
            "tool call. Logs must be persistent — not stored only in memory — and "
            "accessible to oversight personnel independently of the AI system itself."
        ),
        "portfolio_example": (
            "GhostTrace Deep Trace: each tool call in the bounded agentic loop "
            "(investigate_entity, search_cached_filings) should be logged with inputs "
            "and outputs. The 5-call limit is itself a traceability constraint."
        ),
    },
    {
        "id": "TR-2",
        "principle": "TR",
        "title": "Explainability",
        "description": (
            "AI outputs can be explained in human-understandable terms to operators, "
            "affected individuals, and oversight personnel. Explanation depth is "
            "proportionate to decision stakes."
        ),
        "guidance": (
            "Explainability does not require interpretable ML — it requires that a human "
            "can understand WHY the system produced an output. Citing sources, showing "
            "confidence, or providing a reasoning chain are all valid approaches."
        ),
        "portfolio_example": (
            "CFIUS Screener: every finding in the screening report cites the specific "
            "31 CFR Part 800 provision it derives from. That's explainability — the "
            "deterministic engine exposes its reasoning chain."
        ),
    },
    {
        "id": "TR-3",
        "principle": "TR",
        "title": "Data Provenance",
        "description": (
            "Training data, fine-tuning data, and inference-time data sources are "
            "documented, versioned, and traceable to authoritative sources. Data "
            "lineage is accessible to authorized reviewers."
        ),
        "guidance": (
            "If you cannot answer 'where did this data come from and has it changed?', "
            "you cannot investigate a failure. This applies to RAG context, tool call "
            "results, and real-time feeds — not just training data."
        ),
        "portfolio_example": (
            "GhostTrace: every extracted entity cites the specific SEC EDGAR filing "
            "(accession number, filing type) it came from. That's TR-3 applied to "
            "inference-time data."
        ),
    },
    {
        "id": "TR-4",
        "principle": "TR",
        "title": "Model Documentation",
        "description": (
            "Model architecture, training methodology, known limitations, version history, "
            "and evaluation results are documented and maintained. For third-party models, "
            "provider documentation is referenced and gaps noted."
        ),
        "guidance": (
            "For systems using Claude or other foundation models: document which model "
            "version, what context window constraints apply, and what the known failure "
            "modes are. Model cards and system cards are common documentation formats."
        ),
        "portfolio_example": (
            "Every portfolio project specifies 'claude-haiku-4-5-20251001' explicitly in "
            "config.py — not a generic 'latest' pointer. That's the minimum version "
            "tracking required by TR-4."
        ),
    },

    # =========================================================================
    # RL — Reliable
    # =========================================================================
    {
        "id": "RL-1",
        "principle": "RL",
        "title": "Baseline Performance Testing",
        "description": (
            "System tested across expected operational conditions with documented "
            "performance metrics before deployment. Acceptance criteria defined in "
            "advance; system not deployed until criteria are met."
        ),
        "guidance": (
            "Performance testing is not the same as unit testing. It requires realistic "
            "inputs, realistic volumes, and metrics that matter for the use case — "
            "not just 'the code runs.' Define what 'good enough' means before you test."
        ),
        "portfolio_example": (
            "ATO Accelerator: 17 passing tests covering control catalog, categorization "
            "logic, and Claude narrative generation. CFIUS Screener: 85 tests including "
            "all jurisdiction engine edge cases. That's RL-1 in practice."
        ),
    },
    {
        "id": "RL-2",
        "principle": "RL",
        "title": "Adversarial and Edge-Case Testing",
        "description": (
            "System tested against adversarial inputs, distribution shift, out-of-scope "
            "requests, and known edge cases. Failure modes documented and mitigated "
            "before deployment."
        ),
        "guidance": (
            "An adversary will find the edge cases you didn't test. For text-based AI "
            "systems: test with ambiguous inputs, conflicting information, and off-topic "
            "requests. Document what the system does in each case — and whether that's "
            "the intended behavior."
        ),
        "portfolio_example": (
            "CFIUS Screener: _normalize() strips ALL trailing corporate suffixes "
            "iteratively — tested to prevent 'Apex Holdings LLC' from being treated "
            "differently than 'Apex Holdings.' That's adversarial edge-case hardening."
        ),
    },
    {
        "id": "RL-3",
        "principle": "RL",
        "title": "Operational Monitoring",
        "description": (
            "System performance monitored continuously in deployment. Automated alerts "
            "or human review triggered when performance degrades, error rates spike, "
            "or system behavior deviates from baseline."
        ),
        "guidance": (
            "Monitoring means someone is watching after launch — not just at launch. "
            "Define: what metric triggers a review? Who reviews it? What action is taken? "
            "For AI systems, performance can degrade as the world changes even without "
            "any code changes."
        ),
        "portfolio_example": (
            "SENTINEL: the /api/stats health endpoint returns system state in JSON. "
            "That's the seed of operational monitoring — a machine-readable endpoint "
            "that an external monitor could poll."
        ),
    },
    {
        "id": "RL-4",
        "principle": "RL",
        "title": "Uncertainty Communication",
        "description": (
            "System communicates confidence levels, uncertainty, or limitations to "
            "operators and users where AI predictions may be unreliable. Users are "
            "not presented AI outputs as certain when they are not."
        ),
        "guidance": (
            "If the system doesn't know, it should say so. This includes: confidence "
            "scores on classifications, 'I don't have enough information' responses "
            "for agentic systems, and explicit 'not applicable' or 'insufficient data' "
            "outputs rather than silence or hallucinated guesses."
        ),
        "portfolio_example": (
            "Every Claude-calling project includes an 'Honest Limitations' section in "
            "the README, and all outputs include DEMO banners. CFIUS Screener memo: "
            "'This assessment does not constitute legal advice.' That's RL-4."
        ),
    },

    # =========================================================================
    # GO — Governable
    # =========================================================================
    {
        "id": "GO-1",
        "principle": "GO",
        "title": "Human Override Mechanism",
        "description": (
            "Operator or designated human can override, pause, or halt AI outputs at "
            "any time without requiring system redesign. Override capability is "
            "documented, tested, and accessible in operational conditions."
        ),
        "guidance": (
            "Override must work when it matters — including in degraded or high-tempo "
            "operational conditions. For systems where override could be life-critical, "
            "test the override under simulated stress. Document response time from "
            "override command to system halt."
        ),
        "portfolio_example": (
            "GhostTrace Deep Trace: max_tool_calls=5 is a hard-coded upper bound — "
            "the loop cannot run indefinitely regardless of what the model decides. "
            "That's GO-1 implemented as a code constraint."
        ),
    },
    {
        "id": "GO-2",
        "principle": "GO",
        "title": "Update and Retraining Process",
        "description": (
            "Documented, change-controlled process for updating, retraining, or "
            "fine-tuning the AI system. No undocumented silent updates to model "
            "weights, prompts, or system behavior. Version changes are logged."
        ),
        "guidance": (
            "Silent model updates are a governance failure. If your system calls a "
            "third-party API that can update the underlying model without notice, "
            "document that risk and specify a mitigation (e.g., pin model version, "
            "require re-evaluation on model version change)."
        ),
        "portfolio_example": (
            "All portfolio projects pin the model ID ('claude-haiku-4-5-20251001') in "
            "config.py rather than using 'claude-haiku-latest'. That prevents silent "
            "behavior changes from model updates — the baseline version of GO-2."
        ),
    },
    {
        "id": "GO-3",
        "principle": "GO",
        "title": "Scope Constraint Enforcement",
        "description": (
            "System refuses or flags inputs and requests outside its defined operational "
            "parameters. Out-of-scope requests produce an explicit 'outside scope' "
            "response rather than a hallucinated or unreliable answer."
        ),
        "guidance": (
            "Define scope explicitly. A CFIUS screener should not opine on patent law. "
            "A supply chain risk engine should not assess geopolitical intent. Scope "
            "constraints must be enforced in the system, not just documented in the "
            "user guide — users will always try things outside scope."
        ),
        "portfolio_example": (
            "CFIUS Screener: Part 800 only, no Part 802 real estate. The tool explicitly "
            "documents this and the jurisdiction engine only evaluates Part 800 triggers. "
            "Inputs outside scope don't get a guess — they get a scope disclaimer."
        ),
    },
    {
        "id": "GO-4",
        "principle": "GO",
        "title": "Decommission Plan",
        "description": (
            "Documented plan for safely retiring the AI system, including: data handling "
            "and deletion, model weight disposition, user notification, and transition "
            "procedures for any functions the system supports."
        ),
        "guidance": (
            "AI systems are decommissioned — eventually. The plan should exist before "
            "deployment, not be drafted in crisis when a system fails or is replaced. "
            "Data handling is especially critical: what happens to user inputs that "
            "were sent to the model?"
        ),
        "portfolio_example": (
            "All portfolio projects use SQLite with ephemeral Render storage. On "
            "decommission, the database is wiped automatically. That's the minimal "
            "version of GO-4 — data doesn't persist after the service ends."
        ),
    },
]

# Lookup by criterion ID
CRITERIA_LOOKUP: dict[str, dict] = {c["id"]: c for c in CRITERIA}

# Group by principle
CRITERIA_BY_PRINCIPLE: dict[str, list[dict]] = {}
for _c in CRITERIA:
    CRITERIA_BY_PRINCIPLE.setdefault(_c["principle"], []).append(_c)


def get_criterion(criterion_id: str) -> dict | None:
    return CRITERIA_LOOKUP.get(criterion_id)


def principle_summary(assessments: list) -> dict[str, dict]:
    """Return per-principle counts: {principle_code: {met, partial, not_addressed, not_applicable, total}}."""
    result: dict[str, dict] = {}
    for a in assessments:
        p = a.principle_code
        if p not in result:
            result[p] = {"met": 0, "partial": 0, "not_addressed": 0, "not_applicable": 0, "total": 0}
        result[p][a.status] = result[p].get(a.status, 0) + 1
        result[p]["total"] += 1
    return result

"""main.py — RAI Compliance Assistant FastAPI application."""

from __future__ import annotations

import datetime as _dt
import json
import os

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from claude_analyst import AnalystError, characterize_system, generate_rai_narrative
from config import (
    APP_SUBTITLE, APP_TITLE, AUTONOMY_DESCRIPTIONS, CRITERION_STATUSES,
    DEMO_BANNER, DEMO_MODE, RAI_PRINCIPLES,
)
from database import SessionLocal, get_db, init_db
from models import AISystem, CriterionAssessment
from rai_principles import CRITERIA, CRITERIA_BY_PRINCIPLE, CRITERIA_LOOKUP, get_criterion, principle_summary

app = FastAPI(title=APP_TITLE)

os.makedirs("static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.filters["fromjson"] = json.loads


def _load_seed_data(db: Session) -> None:
    from seed_data import DEMO_SYSTEMS
    for demo in DEMO_SYSTEMS:
        if db.query(AISystem).filter_by(name=demo["name"]).first():
            continue
        system = AISystem(
            name=demo["name"],
            description=demo["description"],
            system_owner=demo["system_owner"],
            intended_users=demo["intended_users"],
            data_sources=demo["data_sources"],
            deployment_context=demo["deployment_context"],
            autonomy_level=demo["autonomy_level"],
            highest_risk_principle=demo["highest_risk_principle"],
            priority_criteria=json.dumps(demo["priority_criteria"]),
            characterization_rationale=demo["characterization_rationale"],
        )
        db.add(system)
        db.flush()

        statuses = demo["criterion_statuses"]
        sample = demo["sample_narrative"]
        for crit in CRITERIA:
            status = statuses.get(crit["id"], "not_addressed")
            narrative = sample["narrative"] if crit["id"] == sample["criterion_id"] else None
            db.add(CriterionAssessment(
                system_id=system.id,
                criterion_id=crit["id"],
                principle_code=crit["principle"],
                status=status,
                generated_narrative=narrative,
            ))
    db.commit()


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        _load_seed_data(db)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(extra: dict | None = None) -> dict:
    base = {
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "demo_mode": DEMO_MODE,
        "demo_banner": DEMO_BANNER,
        "rai_principles": RAI_PRINCIPLES,
        "criterion_statuses": CRITERION_STATUSES,
        "autonomy_descriptions": AUTONOMY_DESCRIPTIONS,
    }
    if extra:
        base.update(extra)
    return base


def _build_assessments(db: Session, system: AISystem) -> None:
    """Create CriterionAssessment rows for all 20 RAI criteria."""
    existing = {a.criterion_id for a in system.assessments}
    for crit in CRITERIA:
        if crit["id"] not in existing:
            db.add(CriterionAssessment(
                system_id=system.id,
                criterion_id=crit["id"],
                principle_code=crit["principle"],
                status="not_addressed",
            ))


def _priority_set(system: AISystem) -> set[str]:
    if system.priority_criteria:
        try:
            return set(json.loads(system.priority_criteria))
        except (json.JSONDecodeError, TypeError):
            pass
    return set()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    systems = db.query(AISystem).order_by(AISystem.created_at.desc()).all()
    return templates.TemplateResponse(request, "index.html", _ctx({"systems": systems}))


@app.get("/systems/new", response_class=HTMLResponse)
def new_system_form(request: Request):
    return templates.TemplateResponse(request, "new_system.html", _ctx())


@app.post("/systems/new")
def create_system(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(default=""),
    system_owner: str = Form(default=""),
    intended_users: str = Form(default=""),
    data_sources: str = Form(default=""),
    deployment_context: str = Form(default=""),
):
    system = AISystem(
        name=name,
        description=description,
        system_owner=system_owner,
        intended_users=intended_users,
        data_sources=data_sources,
        deployment_context=deployment_context,
    )
    db.add(system)
    db.commit()
    db.refresh(system)
    return RedirectResponse(f"/systems/{system.id}/characterize", status_code=303)


@app.get("/systems/{system_id}/characterize", response_class=HTMLResponse)
def characterize_form(request: Request, system_id: int, db: Session = Depends(get_db)):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return templates.TemplateResponse(request, "characterize.html", _ctx({"system": system}))


@app.post("/systems/{system_id}/characterize")
def run_characterize(
    request: Request,
    system_id: int,
    db: Session = Depends(get_db),
):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    try:
        result = characterize_system(
            name=system.name,
            description=system.description or "",
            intended_users=system.intended_users or "",
            data_sources=system.data_sources or "",
            deployment_context=system.deployment_context or "",
        )
    except AnalystError as exc:
        return templates.TemplateResponse(
            request, "characterize.html",
            _ctx({"system": system, "error": str(exc)}),
            status_code=500,
        )

    system.autonomy_level = result["autonomy_level"]
    system.highest_risk_principle = result["highest_risk_principle"]
    system.priority_criteria = json.dumps(result["priority_criteria"])
    system.characterization_rationale = result["rationale"]
    db.commit()

    _build_assessments(db, system)
    db.commit()

    return RedirectResponse(f"/systems/{system_id}", status_code=303)


@app.get("/systems/{system_id}", response_class=HTMLResponse)
def system_detail(request: Request, system_id: int, db: Session = Depends(get_db)):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    # Group assessments by principle
    principle_groups: dict[str, list] = {}
    for a in sorted(system.assessments, key=lambda x: x.criterion_id):
        principle_groups.setdefault(a.principle_code, []).append(a)

    # Attach criterion metadata
    assessments_with_meta = []
    priority = _priority_set(system)
    for a in sorted(system.assessments, key=lambda x: x.criterion_id):
        crit = get_criterion(a.criterion_id)
        assessments_with_meta.append((a, crit, a.criterion_id in priority))

    p_summary = principle_summary(system.assessments)

    return templates.TemplateResponse(request, "system_detail.html", _ctx({
        "system": system,
        "principle_groups": principle_groups,
        "assessments_with_meta": assessments_with_meta,
        "criteria_lookup": CRITERIA_LOOKUP,
        "criteria_by_principle": CRITERIA_BY_PRINCIPLE,
        "principle_summary": p_summary,
        "priority_set": priority,
    }))


@app.get("/systems/{system_id}/criteria/{criterion_id}", response_class=HTMLResponse)
def criterion_detail(
    request: Request,
    system_id: int,
    criterion_id: str,
    db: Session = Depends(get_db),
):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    assessment = db.query(CriterionAssessment).filter_by(
        system_id=system_id, criterion_id=criterion_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Criterion not found for this system")

    crit = get_criterion(criterion_id)
    priority = _priority_set(system)

    return templates.TemplateResponse(request, "criterion_detail.html", _ctx({
        "system": system,
        "assessment": assessment,
        "crit": crit,
        "is_priority": criterion_id in priority,
    }))


@app.post("/systems/{system_id}/criteria/{criterion_id}/status")
def update_status(
    system_id: int,
    criterion_id: str,
    db: Session = Depends(get_db),
    status: str = Form(...),
    implementation_notes: str = Form(default=""),
):
    assessment = db.query(CriterionAssessment).filter_by(
        system_id=system_id, criterion_id=criterion_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment.status = status
    assessment.implementation_notes = implementation_notes
    assessment.updated_at = _dt.datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/systems/{system_id}/criteria/{criterion_id}", status_code=303)


@app.post("/systems/{system_id}/criteria/{criterion_id}/generate")
def generate_narrative(
    request: Request,
    system_id: int,
    criterion_id: str,
    db: Session = Depends(get_db),
    implementation_notes: str = Form(default=""),
):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    assessment = db.query(CriterionAssessment).filter_by(
        system_id=system_id, criterion_id=criterion_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    crit = get_criterion(criterion_id)
    if not crit:
        raise HTTPException(status_code=404, detail="Criterion definition not found")

    try:
        narrative = generate_rai_narrative(
            system_name=system.name,
            system_description=system.description or "",
            criterion_id=criterion_id,
            criterion_title=crit["title"],
            criterion_description=crit["description"],
            criterion_guidance=crit["guidance"],
            implementation_notes=implementation_notes,
        )
    except AnalystError as exc:
        priority = _priority_set(system)
        return templates.TemplateResponse(
            request, "criterion_detail.html",
            _ctx({"system": system, "assessment": assessment,
                  "crit": crit, "is_priority": criterion_id in priority,
                  "error": str(exc)}),
            status_code=500,
        )

    assessment.generated_narrative = narrative
    if implementation_notes:
        assessment.implementation_notes = implementation_notes
    assessment.updated_at = _dt.datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/systems/{system_id}/criteria/{criterion_id}", status_code=303)


@app.get("/systems/{system_id}/report", response_class=HTMLResponse)
def rai_report(request: Request, system_id: int, db: Session = Depends(get_db)):
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    met = [a for a in system.assessments if a.status == "met"]
    partial = [a for a in system.assessments if a.status == "partial"]
    not_addressed = sorted(
        [a for a in system.assessments if a.status == "not_addressed"],
        key=lambda x: x.criterion_id,
    )
    na = [a for a in system.assessments if a.status == "not_applicable"]
    priority = _priority_set(system)
    p_summary = principle_summary(system.assessments)

    return templates.TemplateResponse(request, "report.html", _ctx({
        "system": system,
        "met": met,
        "partial": partial,
        "not_addressed": not_addressed,
        "na": na,
        "priority_set": priority,
        "criteria_lookup": CRITERIA_LOOKUP,
        "principle_summary": p_summary,
    }))


@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    from seed_data import DEMO_SYSTEMS
    _load_seed_data(db)
    first = db.query(AISystem).filter_by(name=DEMO_SYSTEMS[0]["name"]).first()
    if first:
        return RedirectResponse(f"/systems/{first.id}", status_code=303)
    return RedirectResponse("/", status_code=303)

"""models.py — ORM models for RAI Compliance Assistant."""

from __future__ import annotations

import datetime as _dt

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class AISystem(Base):
    """An AI system being assessed against DoD Responsible AI principles."""
    __tablename__ = "ai_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_owner: Mapped[str | None] = mapped_column(Text, nullable=True)
    intended_users: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    deployment_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Risk characterization results (set after Claude analysis)
    autonomy_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    highest_risk_principle: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    characterization_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())

    assessments: Mapped[list[CriterionAssessment]] = relationship(
        "CriterionAssessment", back_populates="system", cascade="all, delete-orphan"
    )

    @property
    def met_count(self) -> int:
        return sum(1 for a in self.assessments if a.status == "met")

    @property
    def partial_count(self) -> int:
        return sum(1 for a in self.assessments if a.status == "partial")

    @property
    def not_addressed_count(self) -> int:
        return sum(1 for a in self.assessments if a.status == "not_addressed")

    @property
    def not_applicable_count(self) -> int:
        return sum(1 for a in self.assessments if a.status == "not_applicable")

    @property
    def total_criteria(self) -> int:
        return len(self.assessments)

    @property
    def rai_score(self) -> int:
        if not self.total_criteria:
            return 0
        done = self.met_count + self.not_applicable_count
        return int(done / self.total_criteria * 100)

    @property
    def rai_status(self) -> str:
        score = self.rai_score
        if score >= 85:
            return "Compliant"
        if score >= 50:
            return "Partially Compliant"
        return "At Risk"


class CriterionAssessment(Base):
    """Tracks the status of one RAI criterion for a given AI system."""
    __tablename__ = "criterion_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_systems.id"))
    criterion_id: Mapped[str] = mapped_column(Text)     # e.g. "RE-1"
    principle_code: Mapped[str] = mapped_column(Text)   # e.g. "RE"
    status: Mapped[str] = mapped_column(Text, default="not_addressed")
    implementation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)

    system: Mapped[AISystem] = relationship("AISystem", back_populates="assessments")

    @property
    def status_label(self) -> str:
        from config import CRITERION_STATUSES
        return CRITERION_STATUSES.get(self.status, self.status.replace("_", " ").title())

    @property
    def status_css(self) -> str:
        return {
            "met":           "status-met",
            "partial":       "status-partial",
            "not_addressed": "status-not-addressed",
            "not_applicable":"status-na",
        }.get(self.status, "status-not-addressed")

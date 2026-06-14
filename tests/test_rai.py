"""Tests for rai_principles.py and claude_analyst.py — no real API calls."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from rai_principles import (
    CRITERIA,
    CRITERIA_BY_PRINCIPLE,
    CRITERIA_LOOKUP,
    get_criterion,
    principle_summary,
)
from claude_analyst import characterize_system, generate_rai_narrative, AnalystError


# ---------------------------------------------------------------------------
# rai_principles
# ---------------------------------------------------------------------------

class TestRaiPrinciples:
    def test_criteria_count(self):
        assert len(CRITERIA) == 20

    def test_all_criteria_have_required_fields(self):
        for c in CRITERIA:
            assert "id" in c, f"Missing id in {c}"
            assert "principle" in c
            assert "title" in c
            assert "description" in c
            assert "guidance" in c
            assert "portfolio_example" in c

    def test_five_principles_represented(self):
        principles = {c["principle"] for c in CRITERIA}
        assert principles == {"RE", "EQ", "TR", "RL", "GO"}

    def test_four_criteria_per_principle(self):
        for code, group in CRITERIA_BY_PRINCIPLE.items():
            assert len(group) == 4, f"{code} has {len(group)} criteria, expected 4"

    def test_criteria_ids_are_unique(self):
        ids = [c["id"] for c in CRITERIA]
        assert len(ids) == len(set(ids))

    def test_criteria_ids_follow_pattern(self):
        valid_prefixes = {"RE", "EQ", "TR", "RL", "GO"}
        for c in CRITERIA:
            prefix = c["id"].split("-")[0]
            assert prefix in valid_prefixes, f"Bad prefix in {c['id']}"
            num = c["id"].split("-")[1]
            assert num in {"1", "2", "3", "4"}, f"Bad number in {c['id']}"

    def test_get_criterion_returns_correct_entry(self):
        c = get_criterion("GO-1")
        assert c is not None
        assert c["title"] == "Human Override Mechanism"
        assert c["principle"] == "GO"

    def test_get_criterion_returns_none_for_unknown(self):
        assert get_criterion("ZZ-99") is None

    def test_criteria_lookup_covers_all(self):
        assert len(CRITERIA_LOOKUP) == 20
        for c in CRITERIA:
            assert c["id"] in CRITERIA_LOOKUP

    def test_principle_summary_empty(self):
        summary = principle_summary([])
        assert summary == {}

    def test_principle_summary_counts(self):
        class FakeAssessment:
            def __init__(self, principle, status):
                self.principle_code = principle
                self.status = status

        assessments = [
            FakeAssessment("RE", "met"),
            FakeAssessment("RE", "partial"),
            FakeAssessment("RE", "not_addressed"),
            FakeAssessment("RE", "not_applicable"),
            FakeAssessment("GO", "met"),
            FakeAssessment("GO", "met"),
        ]
        summary = principle_summary(assessments)
        assert summary["RE"]["met"] == 1
        assert summary["RE"]["partial"] == 1
        assert summary["RE"]["not_addressed"] == 1
        assert summary["RE"]["not_applicable"] == 1
        assert summary["RE"]["total"] == 4
        assert summary["GO"]["met"] == 2
        assert summary["GO"]["total"] == 2

    def test_portfolio_examples_not_empty(self):
        for c in CRITERIA:
            assert c["portfolio_example"].strip(), f"{c['id']} has empty portfolio_example"

    def test_re1_exists_and_is_responsible(self):
        c = get_criterion("RE-1")
        assert c["principle"] == "RE"
        assert "Accountability" in c["title"]

    def test_go1_is_human_override(self):
        c = get_criterion("GO-1")
        assert "Override" in c["title"] or "override" in c["description"].lower()


# ---------------------------------------------------------------------------
# claude_analyst — characterize_system
# ---------------------------------------------------------------------------

class TestCharacterizeSystem:
    def _mock_response(self, payload: dict) -> MagicMock:
        msg = MagicMock()
        msg.content = [MagicMock(text=json.dumps(payload))]
        return msg

    @patch("claude_analyst._get_client")
    def test_returns_correct_keys(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response({
            "autonomy_level": "High",
            "highest_risk_principle": "Governable",
            "priority_criteria": ["GO-1", "TR-1"],
            "rationale": "This system operates autonomously.",
        })
        result = characterize_system(
            "TestAI", "An autonomous AI agent", "Analysts", "Public data", "Web app"
        )
        assert result["autonomy_level"] == "High"
        assert result["highest_risk_principle"] == "Governable"
        assert "rationale" in result
        assert isinstance(result["priority_criteria"], list)

    @patch("claude_analyst._get_client")
    def test_raises_on_invalid_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="not json at all")]
        )
        with pytest.raises(AnalystError, match="invalid JSON"):
            characterize_system("s", "d", "u", "ds", "ctx")

    @patch("claude_analyst._get_client")
    def test_raises_on_missing_field(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response({
            "autonomy_level": "Low",
            # missing highest_risk_principle, priority_criteria, rationale
        })
        with pytest.raises(AnalystError, match="missing field"):
            characterize_system("s", "d", "u", "ds", "ctx")

    @patch("claude_analyst._get_client")
    def test_strips_markdown_fences(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        payload = {
            "autonomy_level": "Medium",
            "highest_risk_principle": "Equitable",
            "priority_criteria": ["EQ-1"],
            "rationale": "r",
        }
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text=f"```json\n{json.dumps(payload)}\n```")]
        )
        result = characterize_system("s", "d", "u", "ds", "ctx")
        assert result["autonomy_level"] == "Medium"

    @patch("claude_analyst._get_client")
    def test_raises_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Connection error")
        with pytest.raises(AnalystError, match="Claude API error"):
            characterize_system("s", "d", "u", "ds", "ctx")


# ---------------------------------------------------------------------------
# claude_analyst — generate_rai_narrative
# ---------------------------------------------------------------------------

class TestGenerateRaiNarrative:
    @patch("claude_analyst._get_client")
    def test_returns_string(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="The system addresses GO-1 by...")]
        )
        result = generate_rai_narrative(
            "TestAI", "An AI system", "GO-1",
            "Human Override Mechanism",
            "Operator can override at any time.",
            "Define override procedures.",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("claude_analyst._get_client")
    def test_returns_stripped_string(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="  The narrative text.  ")]
        )
        result = generate_rai_narrative("s", "d", "RE-1", "t", "desc", "guidance")
        assert result == "The narrative text."

    @patch("claude_analyst._get_client")
    def test_raises_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("timeout")
        with pytest.raises(AnalystError, match="Claude API error"):
            generate_rai_narrative("s", "d", "RE-1", "t", "desc", "guidance")

    @patch("claude_analyst._get_client")
    def test_includes_implementation_notes_when_provided(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="narrative")]
        )
        generate_rai_narrative(
            "s", "d", "RE-1", "t", "desc", "guidance",
            implementation_notes="We use a JIRA ticket for reporting."
        )
        call_args = mock_client.messages.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        assert "JIRA" in prompt_content


# ---------------------------------------------------------------------------
# seed_data integrity
# ---------------------------------------------------------------------------

class TestSeedData:
    def test_seed_has_two_systems(self):
        from seed_data import DEMO_SYSTEMS
        assert len(DEMO_SYSTEMS) == 2

    def test_each_seed_system_covers_all_20_criteria(self):
        from seed_data import DEMO_SYSTEMS
        all_ids = {c["id"] for c in CRITERIA}
        for demo in DEMO_SYSTEMS:
            covered = set(demo["criterion_statuses"].keys())
            missing = all_ids - covered
            assert not missing, f"{demo['name']} missing criteria: {missing}"

    def test_seed_status_values_are_valid(self):
        from seed_data import DEMO_SYSTEMS
        valid = {"met", "partial", "not_addressed", "not_applicable"}
        for demo in DEMO_SYSTEMS:
            for cid, status in demo["criterion_statuses"].items():
                assert status in valid, f"{demo['name']} {cid}: invalid status '{status}'"

    def test_seed_autonomy_levels_are_valid(self):
        from seed_data import DEMO_SYSTEMS
        valid = {"Low", "Medium", "High", "Critical"}
        for demo in DEMO_SYSTEMS:
            assert demo["autonomy_level"] in valid

    def test_seed_priority_criteria_are_real_ids(self):
        from seed_data import DEMO_SYSTEMS
        all_ids = {c["id"] for c in CRITERIA}
        for demo in DEMO_SYSTEMS:
            for cid in demo.get("priority_criteria", []):
                assert cid in all_ids, f"Priority criterion {cid} not in catalog"

    def test_seed_sample_narrative_criterion_exists(self):
        from seed_data import DEMO_SYSTEMS
        for demo in DEMO_SYSTEMS:
            sample_id = demo["sample_narrative"]["criterion_id"]
            assert get_criterion(sample_id) is not None, f"Sample criterion {sample_id} not in catalog"

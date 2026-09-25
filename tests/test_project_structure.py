"""Phase 1 tests for configuration and scope safeguards."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(name: str) -> dict:
    """Load a project YAML configuration."""
    with (ROOT / "configs" / name).open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    assert isinstance(value, dict)
    return value


def test_data_scope_is_english_and_sinhala_only() -> None:
    config = load_yaml("data_config.yaml")
    assert config["languages"]["included"] == ["en", "si"]
    assert "ta" in config["languages"]["excluded"]
    assert config["sources"]["modify_sources"] is False


def test_entity_schema_remains_the_approved_five_classes() -> None:
    config = load_yaml("ner_config.yaml")
    assert config["annotation"]["labels"] == [
        "FUNDAMENTAL_RIGHT",
        "OFFENSE",
        "PENALTY",
        "CONSTITUTIONAL_BODY",
        "TEMPORAL_ENTITY",
    ]
    assert config["annotation"]["legal_reference_label_status"] == (
        "pending_researcher_confirmation"
    )


def test_no_cross_document_amendment_inference() -> None:
    config = load_yaml("amendment_config.yaml")
    assert config["method"]["infer_cross_document_relationships"] is False

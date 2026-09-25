"""Tests for leakage-safe Phase 5 feasibility safeguards."""

from __future__ import annotations

from sri_lankan_legal_nlp.data.splitting import exact_agreement_corpus, feasibility_report


def _row(task_id: str, language: str, spans: list[list[object]]) -> dict:
    return {
        "id": task_id,
        "text": "Supreme Court",
        "label": spans,
        "meta": {"language": language, "parent_record_id": f"page-{task_id}"},
    }


def test_consensus_keeps_only_exact_shared_spans() -> None:
    first = {"one": _row("one", "en", [[0, 13, "CONSTITUTIONAL_BODY"]])}
    second = {
        "one": _row(
            "one",
            "en",
            [[0, 13, "CONSTITUTIONAL_BODY"], [0, 7, "FUNDAMENTAL_RIGHT"]],
        )
    }
    corpus = exact_agreement_corpus(first, second)
    assert corpus[0]["label"] == [[0, 13, "CONSTITUTIONAL_BODY"]]


def test_five_folds_are_rejected_when_group_support_is_missing() -> None:
    corpus = [
        {
            **_row("one", "en", [[0, 13, "CONSTITUTIONAL_BODY"]]),
            "consensus_status": "exact_agreement_only_pending_adjudication",
        }
    ]
    report = feasibility_report(corpus, ["CONSTITUTIONAL_BODY", "OFFENSE"], 5)
    assert report["five_fold_feasible"] is False
    assert report["final_split_created"] is False

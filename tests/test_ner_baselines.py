"""Tests for Phase 6 NER baseline utilities."""

from __future__ import annotations

from sri_lankan_legal_nlp.ner.baselines import bio_tags, tags_to_spans, tokenize
from sri_lankan_legal_nlp.ner.evaluation import exact_span_metrics


def test_sinhala_combining_marks_remain_in_one_token() -> None:
    text = "ශ්‍රේෂ්ඨාධිකරණය"
    tokens = tokenize(text)
    assert tokens == [(text, 0, len(text))]


def test_bio_round_trip_preserves_exact_span() -> None:
    text = "The Supreme Court decides."
    start, end = text.index("Supreme"), text.index("Court") + len("Court")
    row = {"text": text, "label": [[start, end, "CONSTITUTIONAL_BODY"]]}
    tokens = tokenize(text)
    assert tags_to_spans(tokens, bio_tags(row, tokens)) == [(start, end, "CONSTITUTIONAL_BODY")]


def test_exact_span_metric_counts_false_positives_and_negatives() -> None:
    rows = [{"id": "one", "label": [[0, 5, "OFFENSE"]]}]
    report = exact_span_metrics(rows, {"one": [(0, 4, "OFFENSE")]}, ["OFFENSE"])
    assert report["micro"]["tp"] == 0
    assert report["micro"]["fp"] == 1
    assert report["micro"]["fn"] == 1

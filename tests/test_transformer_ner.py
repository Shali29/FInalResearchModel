"""Unit tests for transformer character-to-subword label alignment."""

from __future__ import annotations

from sri_lankan_legal_nlp.ner.transformer_alignment import align_labels


def test_special_tokens_are_masked_and_subwords_use_bio() -> None:
    labels = {"O": 0, "B-OFFENSE": 1, "I-OFFENSE": 2}
    offsets = [(0, 0), (0, 4), (4, 7), (8, 12), (0, 0)]
    assert align_labels(offsets, [[0, 7, "OFFENSE"]], labels) == [-100, 1, 2, 0, -100]


def test_padding_and_unlabelled_tokens_are_handled() -> None:
    labels = {"O": 0, "B-PENALTY": 1, "I-PENALTY": 2}
    assert align_labels([(0, 3), (4, 8), (0, 0)], [], labels) == [0, 0, -100]

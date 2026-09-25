"""Transparent dictionary and CRF baselines for bilingual legal NER."""

from __future__ import annotations

import unicodedata
from collections import Counter, defaultdict
from typing import Any

Span = tuple[int, int, str]


def tokenize(text: str) -> list[tuple[str, int, int]]:
    """Return tokens while keeping Sinhala combining marks attached to their base letters."""
    tokens: list[tuple[str, int, int]] = []
    start: int | None = None
    for index, character in enumerate(text):
        is_word = unicodedata.category(character)[0] in {"L", "M", "N"} or character in {
            "_",
            "\u200c",
            "\u200d",
        }
        if is_word and start is None:
            start = index
        elif not is_word:
            if start is not None:
                tokens.append((text[start:index], start, index))
                start = None
            if not character.isspace():
                tokens.append((character, index, index + 1))
    if start is not None:
        tokens.append((text[start:], start, len(text)))
    return tokens


def build_dictionary(rows: list[dict[str, Any]]) -> dict[str, list[tuple[str, str]]]:
    """Build language-specific entity phrase dictionaries from training annotations only."""
    phrases: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    for row in rows:
        language = str(row["meta"]["language"])
        text = str(row["text"])
        for start, end, label in row.get("label", []):
            phrase = text[int(start) : int(end)].strip()
            if phrase:
                phrases[language][(phrase, str(label))] += 1
    return {
        language: sorted(values, key=lambda item: (-len(item[0]), item[0], item[1]))
        for language, values in phrases.items()
    }


def dictionary_predict(
    row: dict[str, Any], dictionary: dict[str, list[tuple[str, str]]]
) -> list[Span]:
    """Apply longest-first, non-overlapping exact phrase matching."""
    text = str(row["text"])
    folded = text.casefold()
    candidates: list[Span] = []
    for phrase, label in dictionary.get(str(row["meta"]["language"]), []):
        needle = phrase.casefold()
        start = 0
        while (position := folded.find(needle, start)) >= 0:
            end = position + len(needle)
            left_ok = position == 0 or not (
                text[position - 1].isalnum() and text[position].isalnum()
            )
            right_ok = end == len(text) or not (text[end - 1].isalnum() and text[end].isalnum())
            if left_ok and right_ok:
                candidates.append((position, end, label))
            start = position + max(len(needle), 1)
    accepted: list[Span] = []
    for candidate in sorted(candidates, key=lambda span: (-(span[1] - span[0]), span[0], span[2])):
        if not any(candidate[0] < span[1] and span[0] < candidate[1] for span in accepted):
            accepted.append(candidate)
    return sorted(accepted)


def bio_tags(row: dict[str, Any], tokens: list[tuple[str, int, int]]) -> list[str]:
    """Convert exact annotations into BIO token labels."""
    tags = ["O"] * len(tokens)
    for start, end, label in sorted(row.get("label", [])):
        indices = [i for i, (_, left, right) in enumerate(tokens) if left >= start and right <= end]
        for offset, index in enumerate(indices):
            tags[index] = f"{'B' if offset == 0 else 'I'}-{label}"
    return tags


def token_features(tokens: list[tuple[str, int, int]], index: int) -> dict[str, object]:
    """Create explainable language-independent lexical and contextual CRF features."""
    word = tokens[index][0]
    features: dict[str, object] = {
        "bias": 1.0,
        "word.lower": word.casefold(),
        "word[-3:]": word[-3:].casefold(),
        "word[-2:]": word[-2:].casefold(),
        "word[:2]": word[:2].casefold(),
        "word.isupper": word.isupper(),
        "word.istitle": word.istitle(),
        "word.isdigit": word.isdigit(),
        "word.has_digit": any(char.isdigit() for char in word),
        "word.length": len(word),
    }
    if index > 0:
        previous = tokens[index - 1][0]
        features.update(
            {"-1:word.lower": previous.casefold(), "-1:word.istitle": previous.istitle()}
        )
    else:
        features["BOS"] = True
    if index + 1 < len(tokens):
        following = tokens[index + 1][0]
        features.update(
            {"+1:word.lower": following.casefold(), "+1:word.istitle": following.istitle()}
        )
    else:
        features["EOS"] = True
    return features


def tags_to_spans(tokens: list[tuple[str, int, int]], tags: list[str]) -> list[Span]:
    """Convert predicted BIO tags back into character spans, repairing invalid I tags."""
    spans: list[Span] = []
    current: tuple[int, int, str] | None = None
    for (_, start, end), tag in zip(tokens, tags, strict=True):
        prefix, _, label = tag.partition("-")
        if tag == "O" or not label:
            if current:
                spans.append(current)
                current = None
        elif prefix == "B" or current is None or current[2] != label:
            if current:
                spans.append(current)
            current = (start, end, label)
        else:
            current = (current[0], end, label)
    if current:
        spans.append(current)
    return spans

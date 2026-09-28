"""FastAPI application for the integrated legal-information prototype."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from sri_lankan_legal_nlp.api.service import (
    DISCLAIMER,
    find_amendments,
    find_source_records,
    predict_entities,
    simplification_template,
)

app = FastAPI(
    title="Sri Lankan Legal NLP Research API",
    version="0.1.0",
    description=DISCLAIMER,
)


class TextRequest(BaseModel):
    """Bilingual user text accepted by NER and simplification preparation."""

    text: str = Field(min_length=1, max_length=20_000)
    language: Literal["en", "si"]


@app.get("/")
def root() -> dict[str, str]:
    return {"name": app.title, "status": "research_prototype", "disclaimer": DISCLAIMER}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ner")
def ner(request: TextRequest) -> dict:
    return predict_entities(request.text, request.language)


@app.get("/sources/search")
def source_search(
    query: str = Query(min_length=1),
    language: Literal["en", "si"] | None = None,
    limit: int = Query(default=10, ge=1, le=50),
) -> dict:
    return {
        "results": find_source_records(query, language, limit),
        "disclaimer": DISCLAIMER,
    }


@app.post("/simplification/prepare")
def prepare_simplification(request: TextRequest) -> dict:
    return simplification_template(request.text, request.language)


@app.get("/amendments")
def amendments(
    provision: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    return {
        "results": find_amendments(provision, limit),
        "status": "candidates_pending_manual_review",
        "disclaimer": DISCLAIMER,
    }

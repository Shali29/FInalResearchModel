"""Configuration loading and validation for data pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from sri_lankan_legal_nlp.data.models import DocumentSpec


class ExtractionSettings(BaseModel):
    """Validated thresholds controlling text extraction and OCR fallback."""

    model_config = ConfigDict(extra="forbid")

    embedded_text_first: bool = True
    preserve_page_boundaries: bool = True
    unicode_normalization: str = "NFC"
    ocr_fallback: bool = True
    ocr_languages: dict[str, str]
    minimum_non_whitespace_characters_per_page: int = Field(ge=1)
    maximum_replacement_character_ratio: float = Field(ge=0, le=1)
    verification_default: str
    repeated_boundary_line_minimum_fraction: float = Field(gt=0, le=1)
    repeated_boundary_line_minimum_pages: int = Field(ge=2)
    ocr_dpi: int = Field(ge=150, le=600)
    tesseract_executable: str
    tessdata_directory: str


class DataConfig(BaseModel):
    """Subset of data configuration used by Phase 2."""

    model_config = ConfigDict(extra="allow")

    sources: dict[str, Any]
    paths: dict[str, str]
    extraction: ExtractionSettings

    @property
    def legal_pdf_root(self) -> Path:
        return Path(self.sources["legal_pdf_root"])

    @property
    def documents(self) -> dict[str, DocumentSpec]:
        return {
            filename: DocumentSpec.model_validate(value)
            for filename, value in self.sources["documents"].items()
        }


def load_data_config(path: Path) -> DataConfig:
    """Read a UTF-8 YAML file and validate the Phase 2 settings."""
    with path.open(encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    return DataConfig.model_validate(raw)

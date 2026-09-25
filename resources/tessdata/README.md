# Portable Tesseract language data

Phase 2 uses this directory through `TESSDATA_PREFIX` so administrator access is unnecessary.
The binary `*.traineddata` files are intentionally ignored by Git and must be downloaded/copied
when rebuilding the environment.

- `eng.traineddata`: copied from the Winget-installed UB Mannheim Tesseract 5.4 package
- `sin.traineddata`: downloaded from the official `tesseract-ocr/tessdata` repository

Verified SHA-256 checksums for this environment:

```text
7D4322BD2A7749724879683FC3912CB542F19906C83BCC1A52132556427170B2  eng.traineddata
C4241607AFE257B9CFDAFA5A171287B7D0441FF541E3B214C0FA03558916ED24  sin.traineddata
```

The presence of a language model does not establish OCR accuracy. All OCR output remains
`pending_review` and must be sampled against the page image.

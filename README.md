# Test Case Generation Platform

A dual-interface problem preparation platform that produces Codebase Online Judge–ready problem bundles. The system orchestrates scraping, AI-assisted enhancement, deterministic/randomized test generation, canonical solution execution, validation, and export workflows for both CLI automation and a lightweight web UI.

## Features (MVP)
- Deterministic problem generation with optional random variation for practice sets.
- Shared Python core powering both a CLI (Typer) and FastAPI web service.
- AI enhancement layer (OpenAI first, pluggable local fallback) for statements, constraints, and validation.
- Codebase-compliant exports: `problem_code/` directories with `.in/.out`, `metadata.json`, and `problem.md`.
- Local-first storage under `/output`, with hooks for future Git/S3 synchronization.
- Minimal role-based access (admin, setter, reviewer) for the web UI.

## Architecture Overview
```
Client (React UI) ──► FastAPI API ──► Core Engine
                         │
                         ├── Spec Ingestion
                         ├── Scraper + Cache
                         ├── AI Enhancer / Validator
                         ├── Deterministic Test Generator
                         ├── Reference Runner (vetted solutions only)
                         └── Exporter (metadata, markdown, zip)
```

## Getting Started
1. **Environment:** Ensure Python 3.11+ is available. Create and activate a virtual environment.
2. **Install:** `pip install -e .[dev]`
3. **CLI usage:** `tcg generate --problem-code ABC123 --seed 42`
4. **API server:** `uvicorn tcg.api.main:app --reload`
5. **Output:** Generated bundles appear under `output/`.

## Roadmap Snapshot
- Sprint 1: Repository scaffold, metadata spec, CLI skeleton, FastAPI base, local writer.
- Sprint 2: AI enhancer integration, deterministic RNG generator, ZIP exporter.
- Sprint 3: Scraper pipeline and reviewer flow.
- Sprint 4: Reference runner with resource limits, reproducibility tests.
- Sprint 5: Web UI, approvals, CI hardening.

## Contributing
- Run `ruff` and `pytest` before pushing.
- Document feature toggles in `docs/` (planned).

## Licensing & Provenance
- Scraped content retained for provenance only.
- All published statements are AI-regenerated to avoid copyright leakage.

---
Status: Sprint 1 in progress.

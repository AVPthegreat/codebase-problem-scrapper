# Coding Problem Scraper (Web)

A simple FastAPI web app that scrapes coding problems from popular platforms based on your prompt, generates `.in`/`.out` testcases, and packages everything into a downloadable ZIP. Includes a fast “placeholder mode” for instant results when testing the flow.

## Features
- Single-page web UI: enter prompt, pick platforms and difficulty, see live logs and progress.
- Curate results: accept/reject problems, then download a filtered ZIP.
- Live sources: Codeforces implemented; LeetCode, CodeChef, GeeksforGeeks, and AtCoder supported to varying degrees.
- Placeholder mode: instant synthetic problems for quick validation.

## Quick start
1. Ensure Python 3.11+ is installed.
2. Create and activate a virtualenv.
3. Install deps:
   - Editable install with dev extras: `pip install -e '.[dev]'`
4. Run the web app locally:
   - `python scripts/run_web.py`
5. Open http://127.0.0.1:8000 and submit a prompt.

## Project layout
- `src/app/services/` – Core orchestration and scrapers
- `src/webapp/` – FastAPI app and Jinja templates (index, job, recent)
- `scripts/run_web.py` – Local runner (uvicorn)
- `tests/` – Smoke tests and a few live scraper checks

## Notes
- Be mindful of platform ToS when scraping. Use placeholder mode for demos.
- If you expose this beyond localhost, consider adding auth and persistent storage.

## Contributing
- Run `pytest` before pushing. Keep changes minimal and focused.

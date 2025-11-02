# Coding Problem Scraper (Web)

A simple FastAPI web app that scrapes coding problems from popular platforms based on your prompt, generates `.in`/`.out` testcases, and packages everything into a downloadable ZIP. Includes a fast “placeholder mode” for instant results when testing the flow.

## Features
- Single-page web UI: enter prompt, pick platforms and difficulty, see live logs and progress.
- Curate results: accept/reject problems, then download a filtered ZIP.
- Live sources: Codeforces implemented; LeetCode, CodeChef, GeeksforGeeks, and AtCoder supported to varying degrees.
- Placeholder mode: instant synthetic problems for quick validation.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AVPthegreat/codebase-problem-scrapper.git
   cd codebase-problem-scrapper
   ```

2. **Create and activate a virtual environment**
   
   On macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   On Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e '.[dev]'
   ```

4. **Run the web application**
   ```bash
   python scripts/run_web.py
   ```

5. **Open your browser**
   - Navigate to http://127.0.0.1:8000
   - Enter a prompt like "Give me 3 easy sorting problems"
   - Select platforms and difficulty
   - Click "Generate Problems"

### Usage Tips
- **Placeholder Mode**: Check the "Use placeholder mode" box for instant synthetic problems (great for testing the UI)
- **Platform Selection**: Select specific platforms (Codeforces, LeetCode, etc.) or leave all unchecked for all available scrapers
- **Problem Curation**: After generation, you can accept/reject individual problems and download only selected ones

## Project layout
- `src/app/services/` – Core orchestration and scrapers
- `src/webapp/` – FastAPI app and Jinja templates (index, job, recent)
- `scripts/run_web.py` – Local runner (uvicorn)
- `tests/` – Smoke tests and a few live scraper checks

## Notes
- **Respect platform ToS**: Be mindful when scraping live platforms. Use placeholder mode for demos and testing.
- **Local use only**: This is designed for localhost. If exposing beyond localhost, add authentication and consider persistent storage.
- **Large files**: Never commit virtual environments (`.venv*`) or output folders to git. The `.gitignore` file handles this automatically.

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill -9
```

**Missing dependencies?**
```bash
pip install -e '.[dev]'
```

**Tests failing?**
```bash
pytest tests/
```

## Contributing
- Run `pytest` before pushing. Keep changes minimal and focused.

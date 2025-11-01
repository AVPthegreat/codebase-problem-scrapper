# Coding Problem Scraper Desktop App

A lightweight desktop utility that scrapes coding problems from competitive programming sites using a user prompt, generates deterministic `.in`/`.out` testcases, and packages them into ZIP archives for download.

## Features (MVP)
- Desktop GUI (PySide6) accepting prompts such as “10 medium sorting problems with I/O specs.”
- Scrapes competitive programming platforms (Codeforces implemented; LeetCode, CodeChef, GeeksforGeeks, and AtCoder stubs awaiting full support).
- Generates structured folders with problem statements and `.in`/`.out` testcase files.
- Exports all generated problems as a ZIP archive ready for online judge upload.

## Architecture Overview
```
PySide6 Desktop UI
    ├── Prompt input + status log
    ├── Generation worker (async scraping + parsing)
    └── ZIP exporter & file chooser

Scraper Engine
    ├── Site adapters (LeetCode, Codeforces, CodeChef, GFG, AtCoder, ...)
    ├── Rate limiting + retry (tenacity)
    ├── HTML parsing (selectolax / BeautifulSoup)
    └── Testcase formatter and ZIP packager
```

## Getting Started
1. **Environment:** Ensure Python 3.11+ is available. Create and activate a virtual environment.
2. **Install:** `pip install -e '.[dev]'`
3. **Run desktop app:** `tcg-desktop`
4. **Prompt:** Describe the problems you need; wait for scraping and ZIP creation.
5. **Download:** Save the generated ZIP to your desired location.

## Roadmap Snapshot
- Sprint 0: Desktop scaffold, scraper interfaces, ZIP exporter.
- Sprint 1: Implement site adapters (LeetCode, Codeforces, CodeChef).
- Current progress: Codeforces adapter implemented with sample test extraction; LeetCode, CodeChef, GeeksforGeeks, and AtCoder stubs in place pending auth/TOS work.
- UI now streams per-scraper progress logs during generation.
- Sprint 2: Add remaining high-priority sources (GeeksforGeeks, AtCoder, etc.).
- Sprint 3: Integrate AI rewriting/validation layer.
- Sprint 4: Add scheduling, caching, and advanced filtering.

## Contributing
- Run `ruff` and `pytest` before pushing changes.
- Document new site adapters and scraping considerations in future `docs/`.

## Licensing & Provenance
- Scraped content is for personal preparation only; respect each platform’s terms of service.
- Keep provenance logs per problem for future review.

---
Status: Desktop MVP under development.

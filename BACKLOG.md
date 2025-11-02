# Project Backlog

This backlog mirrors the issues we plan to open on GitHub. Use it for quick scanning and prioritization.

Legend: [Type] [Area] [Priority] [Difficulty]

## Quick Wins
1. README: add screenshots and a short demo GIF — [documentation] [frontend] [P1] [good first issue]
2. Recent jobs page: add "Clear history" button — [enhancement] [frontend] [ux] [P2] [good first issue]
3. Index: "Select/Deselect all platforms" toggle — [enhancement] [frontend] [ux] [P2] [good first issue]
4. Improve error messages in UI — [enhancement] [frontend] [ux] [P2] [good first issue]
5. CONTRIBUTING: add "How to run tests quickly" — [documentation] [P2] [good first issue]
6. Ruff: ignore temporary build directories — [chore] [ci] [P2] [good first issue]
7. Job page: "Copy Job ID" button — [enhancement] [frontend] [ux] [P2] [good first issue]
8. Footer: add "Report an issue" link — [documentation] [frontend] [P2] [good first issue]

## Core Enhancements
9. Cancel job endpoint and UI button — [enhancement] [backend] [ux] [P0] [help wanted]
10. In-memory job TTL cleanup — [enhancement] [backend] [P0]
11. Optional persistent job store (SQLite) — [enhancement] [backend] [infra] [P1] [help wanted]
12. Configurable MAX_CONCURRENT via env — [enhancement] [backend] [P1]
13. Retry policy for HTTP errors — [enhancement] [backend] [scraper] [P1]
14. Basic auth when non-localhost — [enhancement] [backend] [security] [P1]
15. Health endpoint and metrics stub — [enhancement] [backend] [infra] [P2]

## Scraper Improvements
16. Codeforces: better discovery (tags + pagination) — [enhancement] [scraper] [P1] [help wanted]
17. LeetCode: stabilize metadata retrieval — [enhancement] [scraper] [P1]
18. CodeChef: update selectors and encoding — [enhancement] [scraper] [P1]
19. GFG: clean sample input/output parsing — [enhancement] [scraper] [P2]
20. AtCoder: locale-safe parsing — [enhancement] [scraper] [P2]
21. New scraper template + docs — [enhancement] [scraper] [documentation] [P1]

## UX & Polish
22. Job progress: ETA and remaining steps — [enhancement] [frontend] [ux] [P2]
23. Problem preview panel — [enhancement] [frontend] [ux] [P2]
24. Dark mode toggle — [enhancement] [frontend] [ux] [P3]

## Testing & CI
25. Scraper unit tests with recorded fixtures — [test] [scraper] [backend] [P1] [help wanted]
26. End-to-end API test with TestClient — [test] [backend] [P1]
27. Codecov badge in README — [ci] [documentation] [P2]

## Infra
28. Dockerfile for one-click run — [enhancement] [infra] [P1] [help wanted]
29. Devcontainer (VS Code) — [enhancement] [infra] [P2]
30. Async scraping prototype (flagged) — [performance] [enhancement] [backend] [P3]

## Docs & Community
31. Architecture overview diagram — [documentation] [P2]
32. Roadmap: v0.2.0 and v0.3.0 — [documentation] [P2]
33. Repository labels: set colors and descriptions — [chore] [documentation] [P2]

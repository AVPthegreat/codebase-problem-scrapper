#!/usr/bin/env bash
set -euo pipefail

REPO="AVPthegreat/codebase-problem-scrapper"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is not installed." >&2
  echo "Install: https://cli.github.com/ (macOS: brew install gh)" >&2
  echo "Then authenticate: gh auth login" >&2
  exit 127
fi

echo "Using repository: $REPO"

create_label() {
  local name="$1"; shift
  local color="$1"; shift
  local desc="$1"; shift
  if gh label list --repo "$REPO" | awk 'tolower($0)' | grep -q "^$(echo "$name" | tr '[:upper:]' '[:lower:]')\b"; then
    echo "Label exists: $name"
  else
    echo "Creating label: $name"
    gh label create "$name" --color "$color" --description "$desc" --repo "$REPO" || true
  fi
}

# Create standard labels (idempotent)
create_label "enhancement" a2eeef "New feature or request"
create_label "bug" d73a4a "Something isn't working"
create_label "documentation" 0075ca "Improvements or additions to documentation"
create_label "test" 5319e7 "Testing related work"
create_label "performance" c2e0c6 "Performance improvements"
create_label "refactor" d4c5f9 "Code refactoring"
create_label "chore" cfd3d7 "Build, deps, meta"

create_label "backend" 1d76db "Server, API, orchestrator"
create_label "frontend" 0e8a16 "UI templates and JS"
create_label "scraper" fbca04 "Platform scrapers"
create_label "ci" bfdadc "CI/CD workflows"
create_label "infra" 0052cc "Dev environment and tooling"
create_label "docs" 0366d6 "Documentation area"
create_label "ux" f9d0c4 "User experience and interactions"

create_label "good first issue" 7057ff "Good for newcomers"
create_label "help wanted" 008672 "Extra attention is needed"

create_label "P0" b60205 "Critical priority"
create_label "P1" d93f0b "High priority"
create_label "P2" fef2c0 "Medium priority"
create_label "P3" c5def5 "Low priority"

new_issue() {
  local title="$1"; shift
  local labels_csv="$1"; shift
  local body="$1"; shift
  echo "\nCreating issue: $title"
  gh issue create \
    --repo "$REPO" \
    --title "$title" \
    $(printf %s "$labels_csv" | awk -F, '{for(i=1;i<=NF;i++) printf " --label \"%s\"", $i}') \
    --body "$body" || true
}

# ========== QUICK WINS ==========
new_issue \
  "README: add screenshots and a short demo GIF" \
  "documentation,frontend,good first issue,P1" \
  "Add 3–4 screenshots (main UI, progress/logs, curation, ZIP structure) and a 10–20s demo GIF to README.\n\nAcceptance Criteria:\n- Images committed under repo assets (e.g., docs/assets)\n- README updated with working links that render on GitHub\n- Demo GIF under ~10MB"

new_issue \
  "Recent jobs page: add 'Clear history' button (local only)" \
  "enhancement,frontend,ux,good first issue,P2" \
  "Add a button to clear in-memory recent jobs list. Local-only; affects current process, not persisted.\n\nAcceptance Criteria:\n- Button visible on /recent\n- Clicking clears the list without errors\n- UI refreshes to show empty state"

new_issue \
  "Index: add 'Select/Deselect all platforms' toggle" \
  "enhancement,frontend,ux,good first issue,P2" \
  "Add a single checkbox to toggle all platform checkboxes.\n\nAcceptance Criteria:\n- Toggling selects/deselects all platform options\n- Works with any combination of existing selections"

new_issue \
  "Improve error messages in UI for network/API failures" \
  "enhancement,frontend,ux,good first issue,P2" \
  "Show a friendly toast/alert when submit or polling fails.\n\nAcceptance Criteria:\n- Visible error message on fetch failures\n- No silent failures in console only\n- Retry action suggested"

new_issue \
  "CONTRIBUTING: add 'How to run tests quickly' section" \
  "documentation,good first issue,P2" \
  "Document running pytest, common pitfalls, and how to run a single test.\n\nAcceptance Criteria:\n- CONTRIBUTING.md updated\n- Includes pytest commands and troubleshooting"

new_issue \
  "Ruff: ignore temporary build directories" \
  "chore,ci,good first issue,P2" \
  "Update ruff configuration to ignore dist/ and build/ if present.\n\nAcceptance Criteria:\n- Ruff passes locally and in CI without scanning build artifacts"

new_issue \
  "Job page: add 'Copy Job ID' button" \
  "enhancement,frontend,ux,good first issue,P2" \
  "Add a copy-to-clipboard icon/button next to Job ID.\n\nAcceptance Criteria:\n- Clicking copies job ID reliably across browsers\n- Shows small confirmation"

new_issue \
  "Footer: add 'Report an issue' link" \
  "documentation,frontend,good first issue,P2" \
  "Add a footer link pointing to GitHub new issue page using templates.\n\nAcceptance Criteria:\n- Link goes to prefilled issue template URL"

# ========== CORE ENHANCEMENTS ==========
new_issue \
  "Cancel job endpoint and UI button" \
  "enhancement,backend,ux,P0,help wanted" \
  "Add POST /jobs/{id}/cancel to gracefully stop a running job and a UI button to trigger it.\n\nAcceptance Criteria:\n- Running job transitions to 'cancelled'\n- Background thread and timers cleaned up\n- UI reflects cancelled state"

new_issue \
  "In-memory job TTL cleanup" \
  "enhancement,backend,P0" \
  "Evict completed/failed jobs after a configurable TTL to prevent memory growth.\n\nAcceptance Criteria:\n- TTL env/config supported\n- Jobs cleaned on schedule or access\n- Recent page handles evicted jobs gracefully"

new_issue \
  "Optional persistent job store (SQLite) behind feature flag" \
  "enhancement,backend,infra,P1,help wanted" \
  "Persist jobs/logs to SQLite when enabled via env. Default remains in-memory.\n\nAcceptance Criteria:\n- Feature flag toggles persistence\n- Local default unchanged\n- Backwards compatible data model"

new_issue \
  "Make MAX_CONCURRENT configurable via environment" \
  "enhancement,backend,P1" \
  "Read concurrency limit from env with a safe default.\n\nAcceptance Criteria:\n- Changing env updates supervisor behavior\n- Documented in README"

new_issue \
  "Retry policy for transient HTTP errors (tenacity)" \
  "enhancement,backend,scraper,P1" \
  "Use tenacity/backoff for transient network errors in scrapers.\n\nAcceptance Criteria:\n- Retries applied to HTTP requests\n- Permanent errors logged once per URL\n- Timeouts respected"

new_issue \
  "Basic auth when binding beyond localhost" \
  "enhancement,backend,security,P1" \
  "Enable simple Basic Auth when host != 127.0.0.1 (off by default).\n\nAcceptance Criteria:\n- Disabled by default\n- When enabled, all routes require auth\n- Documented risks"

new_issue \
  "Health endpoint and metrics stub" \
  "enhancement,backend,infra,P2" \
  "Add /healthz and a stub for Prometheus metrics (optional).\n\nAcceptance Criteria:\n- /healthz returns 200 OK with basic info\n- Metrics endpoint is behind a flag"

# ========== SCRAPER IMPROVEMENTS ==========
new_issue \
  "Codeforces: better discovery (tags + pagination)" \
  "enhancement,scraper,P1,help wanted" \
  "Improve Codeforces scraper to support tag/topic discovery with pagination.\n\nAcceptance Criteria:\n- Given common tags, collects multiple problems reliably\n- Handles pagination without rate limit issues"

new_issue \
  "LeetCode: stabilize metadata retrieval (GraphQL)" \
  "enhancement,scraper,P1" \
  "Use stable endpoints for LeetCode metadata where allowed to reduce breakage.\n\nAcceptance Criteria:\n- Existing tests pass (e.g., Two Sum)\n- 2–3 canonical problems resolvable reliably"

new_issue \
  "CodeChef: update selectors and encoding handling" \
  "enhancement,scraper,P1" \
  "Adjust selectors and encoding normalization to reduce parse errors.\n\nAcceptance Criteria:\n- Live test passes consistently\n- Fewer empty/None fields in results"

new_issue \
  "GFG: clean sample input/output parsing" \
  "enhancement,scraper,P2" \
  "Strip prompts/headings so .in/.out contain only raw samples.\n\nAcceptance Criteria:\n- Clean .in/.out files with only inputs/outputs\n- Tests updated accordingly"

new_issue \
  "AtCoder: locale-safe parsing and alt layouts" \
  "enhancement,scraper,P2" \
  "Handle alternate layouts/locales for AtCoder problem pages.\n\nAcceptance Criteria:\n- Tests pass for additional sample problems\n- Robust handling across typical variants"

new_issue \
  "Add new scraper template + docs" \
  "enhancement,scraper,documentation,P1" \
  "Provide a base scraper template and a guide: 'How to add a new scraper'.\n\nAcceptance Criteria:\n- Template file in scrapers/\n- Docs with checklist and gotchas"

# ========== UX POLISH ==========
new_issue \
  "Job progress: show ETA and remaining steps" \
  "enhancement,frontend,ux,P2" \
  "Estimate remaining time based on steps completed.\n\nAcceptance Criteria:\n- ETA displays when calculable\n- Graceful fallback when unknown"

new_issue \
  "Problem preview panel in curation view" \
  "enhancement,frontend,ux,P2" \
  "Click a problem to preview title, snippet, and IO samples inline.\n\nAcceptance Criteria:\n- No full page reload\n- Accessible keyboard navigation"

new_issue \
  "Dark mode toggle" \
  "enhancement,frontend,ux,P3" \
  "Add a simple CSS dark theme toggle with persisted preference.\n\nAcceptance Criteria:\n- Toggle persists per session\n- Meets contrast accessibility"

# ========== TESTING & CI ==========
new_issue \
  "Scraper unit tests with recorded fixtures" \
  "test,scraper,backend,P1,help wanted" \
  "Record httpx/respx fixtures for 1–2 problems per platform to make tests stable offline.\n\nAcceptance Criteria:\n- Tests pass offline\n- CI no longer flaky on network"

new_issue \
  "End-to-end API test with TestClient" \
  "test,backend,P1" \
  "Submit job → poll → retrieve problems → create filtered ZIP in a single E2E test.\n\nAcceptance Criteria:\n- Stable E2E test green in CI"

new_issue \
  "Codecov badge in README" \
  "ci,documentation,P2" \
  "Add Codecov badge after configuring token in repository secrets.\n\nAcceptance Criteria:\n- Badge renders in README\n- CI uploads coverage on main"

# ========== INFRA ==========
new_issue \
  "Dockerfile for one-click run" \
  "enhancement,infra,P1,help wanted" \
  "Create a Dockerfile (and optional compose) to run the app easily.\n\nAcceptance Criteria:\n- docker run exposes :8000 and app works\n- README includes usage"

new_issue \
  "Devcontainer (VS Code) for contributors" \
  "enhancement,infra,P2" \
  "Add .devcontainer with Python, ruff, pytest preinstalled.\n\nAcceptance Criteria:\n- 'Open in Dev Container' runs tests out of the box"

new_issue \
  "Async scraping prototype behind a flag" \
  "performance,enhancement,backend,P3" \
  "Prototype httpx.AsyncClient with rate limits; compare throughput.\n\nAcceptance Criteria:\n- Behind a feature flag\n- Equal or better throughput\n- No regressions in tests"

# ========== DOCS & COMMUNITY ==========
new_issue \
  "Architecture overview diagram" \
  "documentation,P2" \
  "Add a simple diagram of the job queue, workers, and endpoints.\n\nAcceptance Criteria:\n- Diagram checked into docs/ and linked from README"

new_issue \
  "Roadmap: v0.2.0 and v0.3.0 milestones" \
  "documentation,P2" \
  "Create ROADMAP.md with upcoming milestones and priorities.\n\nAcceptance Criteria:\n- Document exists and is linked in README"

new_issue \
  "Repository labels: set colors and descriptions" \
  "chore,documentation,P2" \
  "Standardize label colors/descriptions for triage.\n\nAcceptance Criteria:\n- Labels reflect the palette in open_issues.sh\n- Documented briefly in CONTRIBUTING.md"

echo "\nAll done. If any issues failed due to permissions or duplicates, review the output above."

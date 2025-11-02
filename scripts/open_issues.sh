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

create_milestone() {
  local title="$1"; shift
  local desc="$1"; shift
  if gh api repos/$REPO/milestones --paginate | jq -r '.[].title' | grep -qx "$title"; then
    echo "Milestone exists: $title"
  else
    echo "Creating milestone: $title"
    gh api repos/$REPO/milestones -f title="$title" -f description="$desc" >/dev/null || true
  fi
}

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
create_label "security" e99695 "Security-related changes"

create_label "good first issue" 7057ff "Good for newcomers"
create_label "help wanted" 008672 "Extra attention is needed"

create_label "P0" b60205 "Critical priority"
create_label "P1" d93f0b "High priority"
create_label "P2" fef2c0 "Medium priority"
create_label "P3" c5def5 "Low priority"

# Create standard milestones (idempotent)
create_milestone "v0.2.0" "High-priority and core improvements"
create_milestone "v0.3.0" "Polish, UX and extended enhancements"

new_issue() {
  local title="$1"; shift
  local labels_csv="$1"; shift
  local milestone="$1"; shift
  local body="$1"; shift
  echo "\nCreating issue: $title"
  if [ -n "$milestone" ]; then
    M_FLAG=(--milestone "$milestone")
  else
    M_FLAG=()
  fi
  # Build label args safely (handles spaces in label names)
  IFS=',' read -r -a _labels <<< "$labels_csv"
  LABEL_ARGS=()
  for l in "${_labels[@]}"; do
    LABEL_ARGS+=(--label "$l")
  done

  # Skip if issue with the same title already exists
  if gh issue list --repo "$REPO" --search "in:title $title" --limit 1 --json title | jq -e '. | length > 0' >/dev/null; then
    echo "Issue already exists, skipping: $title"
    return 0
  fi

  gh issue create \
    --repo "$REPO" \
    --title "$title" \
    "${LABEL_ARGS[@]}" \
    "${M_FLAG[@]}" \
    --body "$body" || true
}

# ========== CRITICAL BUG FIXES ==========
new_issue \
  "[CRITICAL] Fix metadata extraction inconsistencies in scraped problems" \
  "bug,scraper,P0" \
  "v0.2.0" \
  "**Problem:** Problem metadata (titles, descriptions, constraints, I/O samples) is inconsistent across scrapers. Some problems have complete data while others are missing critical fields, leading to incomplete or unusable problem bundles.\n\n**Impact:** Users receive ZIP files with partial or missing problem data, making the tool unreliable for actual use.\n\n**Root Cause:**\n- Scraper selectors may be outdated or fragile\n- HTML structure variations not handled\n- Missing fallback logic for alternative layouts\n- No validation before including problems in output\n\n**Acceptance Criteria:**\n- ✅ Add metadata completeness validator before including problems in ZIP\n- ✅ Filter out problems missing title, statement, or I/O samples\n- ✅ Log which problems were skipped and why\n- ✅ Update scraper selectors for all platforms to handle common layout variants\n- ✅ Ensure at least 80% of scraped problems have complete metadata\n- ✅ Add unit tests validating metadata completeness for each scraper\n\n**Priority:** P0 - Blocks core functionality"

new_issue \
  "[CRITICAL] Progress stuck at 0% - supervisor thread not updating job state" \
  "bug,backend,P0" \
  "v0.2.0" \
  "**Problem:** Job submission succeeds but progress remains stuck at 0% indefinitely. Terminal/logs show activity but UI never updates. Job appears 'running' but never completes.\n\n**Impact:** Users cannot track job progress or know when scraping completes. Creates impression that app is frozen/broken.\n\n**Symptoms:**\n- POST /api/submit returns job ID successfully\n- GET /jobs/{id} shows status 'running' with 0% progress\n- Backend logs show scraping activity\n- Progress never increments; job never reaches 'completed' state\n- /jobs/{id}/log endpoint may or may not stream logs\n\n**Suspected Causes:**\n- Supervisor thread may not be starting or processing queue\n- Job state updates not persisting to shared JOBS dict\n- Race condition in threading/locking\n- Progress calculation logic broken\n\n**Acceptance Criteria:**\n- ✅ Job progresses from 0% → 100% as steps complete\n- ✅ Status transitions: pending → running → completed/failed\n- ✅ Add health check endpoint that verifies supervisor is alive\n- ✅ Add debug logging for job state transitions\n- ✅ E2E test: submit job → poll until completion → verify final state\n\n**Priority:** P0 - Core functionality broken"

new_issue \
  "[CRITICAL] Extreme slowdown when scraping multiple platforms with 'hard' difficulty" \
  "bug,performance,backend,scraper,P0" \
  "v0.2.0" \
  "**Problem:** When selecting all platforms + 'hard' difficulty, response time becomes unacceptably slow (multiple minutes or timeouts). App appears to hang.\n\n**Impact:** Users cannot scrape comprehensive problem sets. Forced to use limited queries or single platforms.\n\n**Symptoms:**\n- Selecting 1-2 platforms: completes in reasonable time (<30s)\n- Selecting all platforms + hard: takes 5+ minutes or times out\n- No incremental feedback during long operations\n- Browser may show 'page unresponsive' warnings\n\n**Root Causes:**\n- Sequential scraping (no concurrency between platforms)\n- No request rate limiting causes IP blocks/slowdowns\n- Large result sets processed in-memory without streaming\n- Blocking I/O in web thread\n\n**Acceptance Criteria:**\n- ✅ All platforms + hard difficulty completes in <2 minutes\n- ✅ Progress updates visible during scraping (not stuck at 0%)\n- ✅ Implement concurrent scraping with MAX_CONCURRENT workers\n- ✅ Add rate limiting per platform (avoid IP blocks)\n- ✅ Show estimated time remaining based on progress\n- ✅ Consider pagination/streaming for large result sets\n\n**Priority:** P0 - Severely impacts usability"

new_issue \
  "[CRITICAL] Interactive problem selection before download" \
  "enhancement,frontend,ux,P0" \
  "v0.2.0" \
  "**Feature Request:** After scraping completes, display all discovered problems in a filterable/selectable UI. Allow users to cherry-pick which problems to include in the final ZIP download instead of auto-downloading everything.\n\n**User Story:**\nAs a user, after scraping 50 hard problems from Codeforces, I want to:\n1. Preview the list of problems with metadata (title, difficulty, tags, acceptance rate)\n2. Select/deselect individual problems or use bulk filters\n3. Generate a custom ZIP with only my selected problems\n\n**Current Behavior:**\n- Scraping completes → ZIP auto-generated with ALL problems → no choice\n\n**Desired Behavior:**\n- Scraping completes → **Problem Curation Page** displays:\n  - Table/grid of all scraped problems\n  - Checkboxes for selection (select all / deselect all)\n  - Filters: difficulty, tags, platform, acceptance rate\n  - Search by title/ID\n  - Preview pane showing problem statement snippet\n- \"Generate ZIP with selected (X problems)\" button\n- Downloads filtered ZIP with only checked problems\n\n**Acceptance Criteria:**\n- ✅ New route: GET /jobs/{id}/problems → JSON list of scraped problems with metadata\n- ✅ Curation UI page with selectable problem table\n- ✅ Client-side filtering and search (or server-side if list is large)\n- ✅ POST /jobs/{id}/download with selected problem IDs in request body\n- ✅ Backend generates ZIP with only requested problems\n- ✅ UI shows count: \"X of Y problems selected\"\n- ✅ Keyboard shortcuts: Ctrl+A (select all), Escape (deselect)\n\n**Priority:** P0 - Highly requested feature; core to user workflow"

new_issue \
  "[CRITICAL] UI/UX improvements for better usability" \
  "enhancement,frontend,ux,P0" \
  "v0.2.0" \
  "**Problem:** Current UI is functional but lacks polish and usability features that would significantly improve user experience.\n\n**Pain Points:**\n1. **Visual Design:**\n   - Minimal styling; looks like a prototype\n   - Inconsistent spacing and typography\n   - No visual hierarchy or branding\n   - Forms lack validation feedback\n\n2. **Interaction Feedback:**\n   - No loading states or spinners\n   - Buttons don't show disabled/loading states\n   - No success/error toasts for actions\n   - Progress updates not prominent enough\n\n3. **Usability Issues:**\n   - Platform checkboxes hard to scan (no grouping/icons)\n   - Difficulty dropdown not obvious\n   - No help text or tooltips\n   - Recent jobs list cluttered\n   - Mobile responsiveness missing\n\n**Proposed Improvements:**\n\n**Phase 1 - Critical UX (v0.2.0):**\n- ✅ Add loading spinners for async operations\n- ✅ Toast notifications for success/error (e.g., \"Job submitted!\", \"Download ready\")\n- ✅ Improve form validation with inline error messages\n- ✅ Add disabled states to buttons during processing\n- ✅ Progress bar: make larger, show percentage, add color coding (blue=running, green=done, red=failed)\n- ✅ Platform selection: add icons/logos, group by category\n- ✅ Add \"What does this do?\" info tooltips\n- ✅ Responsive layout (mobile-friendly)\n\n**Phase 2 - Visual Polish (v0.3.0):**\n- Modern CSS framework or Tailwind integration\n- Consistent color scheme and typography\n- Dark mode support\n- Animations for state transitions\n- Professional landing page with hero section\n\n**Acceptance Criteria (Phase 1):**\n- No action leaves user wondering if it worked\n- All forms validate before submission\n- UI adapts to mobile screens\n- Progress is always visible and understandable\n- Passes basic accessibility audit (keyboard nav, ARIA labels)\n\n**Priority:** P0 - First impressions matter; current UI hurts adoption"

new_issue \
  "[CRITICAL] Fix typos and grammar errors across codebase and documentation" \
  "bug,documentation,good first issue,P0" \
  "v0.2.0" \
  "**Problem:** Typos and grammatical errors present in:\n- README.md\n- CONTRIBUTING.md\n- Code comments\n- UI text (button labels, error messages, form placeholders)\n- Log messages\n\n**Impact:**\n- Reduces professional perception of the project\n- May confuse contributors or users\n- Makes documentation harder to follow\n\n**Scope:**\nConduct a full audit of all user-facing text:\n1. Documentation files (README, CONTRIBUTING, SECURITY, etc.)\n2. UI templates (index.html, job.html, recent.html)\n3. Error messages and API responses\n4. Code comments (especially public functions)\n5. Log output\n\n**Tools:**\n- Run a spell checker (VS Code spell check extension)\n- Use Grammarly or LanguageTool for grammar\n- Manual review of technical terminology\n\n**Acceptance Criteria:**\n- ✅ All documentation files pass spell check\n- ✅ UI text is grammatically correct and professional\n- ✅ Error messages are clear and actionable\n- ✅ Code comments use consistent terminology\n- ✅ No embarrassing typos in public-facing pages\n- ✅ Add .vscode/settings.json with spell check enabled + custom dictionary for technical terms\n\n**Priority:** P0 - Easy fix with high ROI for professionalism\n\n**Good First Issue:** Perfect for new contributors; low complexity, high impact."

# ========== QUICK WINS ==========
new_issue \
  "README: add screenshots and a short demo GIF" \
  "documentation,frontend,good first issue,P1" \
  "v0.2.0" \
  "Add 3–4 screenshots (main UI, progress/logs, curation, ZIP structure) and a 10–20s demo GIF to README.\n\nAcceptance Criteria:\n- Images committed under repo assets (e.g., docs/assets)\n- README updated with working links that render on GitHub\n- Demo GIF under ~10MB"

new_issue \
  "Recent jobs page: add 'Clear history' button (local only)" \
  "enhancement,frontend,ux,good first issue,P2" \
  "v0.3.0" \
  "Add a button to clear in-memory recent jobs list. Local-only; affects current process, not persisted.\n\nAcceptance Criteria:\n- Button visible on /recent\n- Clicking clears the list without errors\n- UI refreshes to show empty state"

new_issue \
  "Index: add 'Select/Deselect all platforms' toggle" \
  "enhancement,frontend,ux,good first issue,P2" \
  "v0.3.0" \
  "Add a single checkbox to toggle all platform checkboxes.\n\nAcceptance Criteria:\n- Toggling selects/deselects all platform options\n- Works with any combination of existing selections"

new_issue \
  "Improve error messages in UI for network/API failures" \
  "enhancement,frontend,ux,good first issue,P2" \
  "v0.3.0" \
  "Show a friendly toast/alert when submit or polling fails.\n\nAcceptance Criteria:\n- Visible error message on fetch failures\n- No silent failures in console only\n- Retry action suggested"

new_issue \
  "CONTRIBUTING: add 'How to run tests quickly' section" \
  "documentation,good first issue,P2" \
  "v0.3.0" \
  "Document running pytest, common pitfalls, and how to run a single test.\n\nAcceptance Criteria:\n- CONTRIBUTING.md updated\n- Includes pytest commands and troubleshooting"

new_issue \
  "Ruff: ignore temporary build directories" \
  "chore,ci,good first issue,P2" \
  "v0.3.0" \
  "Update ruff configuration to ignore dist/ and build/ if present.\n\nAcceptance Criteria:\n- Ruff passes locally and in CI without scanning build artifacts"

new_issue \
  "Job page: add 'Copy Job ID' button" \
  "enhancement,frontend,ux,good first issue,P2" \
  "v0.3.0" \
  "Add a copy-to-clipboard icon/button next to Job ID.\n\nAcceptance Criteria:\n- Clicking copies job ID reliably across browsers\n- Shows small confirmation"

new_issue \
  "Footer: add 'Report an issue' link" \
  "documentation,frontend,good first issue,P2" \
  "v0.3.0" \
  "Add a footer link pointing to GitHub new issue page using templates.\n\nAcceptance Criteria:\n- Link goes to prefilled issue template URL"

# ========== CORE ENHANCEMENTS ==========
new_issue \
  "Cancel job endpoint and UI button" \
  "enhancement,backend,ux,P0,help wanted" \
  "v0.2.0" \
  "Add POST /jobs/{id}/cancel to gracefully stop a running job and a UI button to trigger it.\n\nAcceptance Criteria:\n- Running job transitions to 'cancelled'\n- Background thread and timers cleaned up\n- UI reflects cancelled state"

new_issue \
  "In-memory job TTL cleanup" \
  "enhancement,backend,P0" \
  "v0.2.0" \
  "Evict completed/failed jobs after a configurable TTL to prevent memory growth.\n\nAcceptance Criteria:\n- TTL env/config supported\n- Jobs cleaned on schedule or access\n- Recent page handles evicted jobs gracefully"

new_issue \
  "Optional persistent job store (SQLite) behind feature flag" \
  "enhancement,backend,infra,P1,help wanted" \
  "v0.2.0" \
  "Persist jobs/logs to SQLite when enabled via env. Default remains in-memory.\n\nAcceptance Criteria:\n- Feature flag toggles persistence\n- Local default unchanged\n- Backwards compatible data model"

new_issue \
  "Make MAX_CONCURRENT configurable via environment" \
  "enhancement,backend,P1" \
  "v0.2.0" \
  "Read concurrency limit from env with a safe default.\n\nAcceptance Criteria:\n- Changing env updates supervisor behavior\n- Documented in README"

new_issue \
  "Retry policy for transient HTTP errors (tenacity)" \
  "enhancement,backend,scraper,P1" \
  "v0.2.0" \
  "Use tenacity/backoff for transient network errors in scrapers.\n\nAcceptance Criteria:\n- Retries applied to HTTP requests\n- Permanent errors logged once per URL\n- Timeouts respected"

new_issue \
  "Basic auth when binding beyond localhost" \
  "enhancement,backend,security,P1" \
  "v0.2.0" \
  "Enable simple Basic Auth when host != 127.0.0.1 (off by default).\n\nAcceptance Criteria:\n- Disabled by default\n- When enabled, all routes require auth\n- Documented risks"

new_issue \
  "Health endpoint and metrics stub" \
  "enhancement,backend,infra,P2" \
  "v0.3.0" \
  "Add /healthz and a stub for Prometheus metrics (optional).\n\nAcceptance Criteria:\n- /healthz returns 200 OK with basic info\n- Metrics endpoint is behind a flag"

# ========== SCRAPER IMPROVEMENTS ==========
new_issue \
  "Codeforces: better discovery (tags + pagination)" \
  "enhancement,scraper,P1,help wanted" \
  "v0.2.0" \
  "Improve Codeforces scraper to support tag/topic discovery with pagination.\n\nAcceptance Criteria:\n- Given common tags, collects multiple problems reliably\n- Handles pagination without rate limit issues"

new_issue \
  "LeetCode: stabilize metadata retrieval (GraphQL)" \
  "enhancement,scraper,P1" \
  "v0.2.0" \
  "Use stable endpoints for LeetCode metadata where allowed to reduce breakage.\n\nAcceptance Criteria:\n- Existing tests pass (e.g., Two Sum)\n- 2–3 canonical problems resolvable reliably"

new_issue \
  "CodeChef: update selectors and encoding handling" \
  "enhancement,scraper,P1" \
  "v0.2.0" \
  "Adjust selectors and encoding normalization to reduce parse errors.\n\nAcceptance Criteria:\n- Live test passes consistently\n- Fewer empty/None fields in results"

new_issue \
  "GFG: clean sample input/output parsing" \
  "enhancement,scraper,P2" \
  "v0.3.0" \
  "Strip prompts/headings so .in/.out contain only raw samples.\n\nAcceptance Criteria:\n- Clean .in/.out files with only inputs/outputs\n- Tests updated accordingly"

new_issue \
  "AtCoder: locale-safe parsing and alt layouts" \
  "enhancement,scraper,P2" \
  "v0.3.0" \
  "Handle alternate layouts/locales for AtCoder problem pages.\n\nAcceptance Criteria:\n- Tests pass for additional sample problems\n- Robust handling across typical variants"

new_issue \
  "Add new scraper template + docs" \
  "enhancement,scraper,documentation,P1" \
  "v0.2.0" \
  "Provide a base scraper template and a guide: 'How to add a new scraper'.\n\nAcceptance Criteria:\n- Template file in scrapers/\n- Docs with checklist and gotchas"

# ========== UX POLISH ==========
new_issue \
  "Job progress: show ETA and remaining steps" \
  "enhancement,frontend,ux,P2" \
  "v0.3.0" \
  "Estimate remaining time based on steps completed.\n\nAcceptance Criteria:\n- ETA displays when calculable\n- Graceful fallback when unknown"

new_issue \
  "Problem preview panel in curation view" \
  "enhancement,frontend,ux,P2" \
  "v0.3.0" \
  "Click a problem to preview title, snippet, and IO samples inline.\n\nAcceptance Criteria:\n- No full page reload\n- Accessible keyboard navigation"

new_issue \
  "Dark mode toggle" \
  "enhancement,frontend,ux,P3" \
  "v0.3.0" \
  "Add a simple CSS dark theme toggle with persisted preference.\n\nAcceptance Criteria:\n- Toggle persists per session\n- Meets contrast accessibility"

# ========== TESTING & CI ==========
new_issue \
  "Scraper unit tests with recorded fixtures" \
  "test,scraper,backend,P1,help wanted" \
  "v0.2.0" \
  "Record httpx/respx fixtures for 1–2 problems per platform to make tests stable offline.\n\nAcceptance Criteria:\n- Tests pass offline\n- CI no longer flaky on network"

new_issue \
  "End-to-end API test with TestClient" \
  "test,backend,P1" \
  "v0.2.0" \
  "Submit job → poll → retrieve problems → create filtered ZIP in a single E2E test.\n\nAcceptance Criteria:\n- Stable E2E test green in CI"

new_issue \
  "Codecov badge in README" \
  "ci,documentation,P2" \
  "v0.3.0" \
  "Add Codecov badge after configuring token in repository secrets.\n\nAcceptance Criteria:\n- Badge renders in README\n- CI uploads coverage on main"

# ========== INFRA ==========
new_issue \
  "Dockerfile for one-click run" \
  "enhancement,infra,P1,help wanted" \
  "v0.2.0" \
  "Create a Dockerfile (and optional compose) to run the app easily.\n\nAcceptance Criteria:\n- docker run exposes :8000 and app works\n- README includes usage"

new_issue \
  "Devcontainer (VS Code) for contributors" \
  "enhancement,infra,P2" \
  "v0.3.0" \
  "Add .devcontainer with Python, ruff, pytest preinstalled.\n\nAcceptance Criteria:\n- 'Open in Dev Container' runs tests out of the box"

new_issue \
  "Async scraping prototype behind a flag" \
  "performance,enhancement,backend,P3" \
  "v0.3.0" \
  "Prototype httpx.AsyncClient with rate limits; compare throughput.\n\nAcceptance Criteria:\n- Behind a feature flag\n- Equal or better throughput\n- No regressions in tests"

# ========== DOCS & COMMUNITY ==========
new_issue \
  "Architecture overview diagram" \
  "documentation,P2" \
  "v0.3.0" \
  "Add a simple diagram of the job queue, workers, and endpoints.\n\nAcceptance Criteria:\n- Diagram checked into docs/ and linked from README"

new_issue \
  "Roadmap: v0.2.0 and v0.3.0 milestones" \
  "documentation,P2" \
  "v0.3.0" \
  "Create ROADMAP.md with upcoming milestones and priorities.\n\nAcceptance Criteria:\n- Document exists and is linked in README"

new_issue \
  "Repository labels: set colors and descriptions" \
  "chore,documentation,P2" \
  "v0.3.0" \
  "Standardize label colors/descriptions for triage.\n\nAcceptance Criteria:\n- Labels reflect the palette in open_issues.sh\n- Documented briefly in CONTRIBUTING.md"

echo "\nAll done. If any issues failed due to permissions or duplicates, review the output above."

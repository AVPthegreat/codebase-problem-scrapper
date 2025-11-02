from __future__ import annotations

from pathlib import Path
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List

from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import tempfile
import os
import zipfile
from pydantic import BaseModel

from app.services.orchestrator import ScrapeOrchestrator

app = FastAPI(title="Problem Scraper Web")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@dataclass
class Job:
    id: str
    prompt: str
    platform: str = "Any"
    difficulty: str = "Any"
    status: str = "queued"  # queued|running|done|error
    created_at: datetime = field(default_factory=datetime.utcnow)
    logs: List[str] = field(default_factory=list)
    zip_path: Optional[Path] = None
    error: Optional[str] = None


JOBS: Dict[str, Job] = {}
JOBS_LOCK = threading.Lock()
QUEUE: deque[str] = deque()
ACTIVE: set[str] = set()
ACTIVE_LOCK = threading.Lock()
RECENTS: deque[str] = deque(maxlen=20)
MAX_CONCURRENT = 2
SUPERVISOR_STARTED = False


def _append_log(job: Job, message: str) -> None:
    # List append is thread-safe in CPython, no lock needed
    job.logs.append(message)


def _compose_prompt(prompt: str, platform: str, difficulty: str) -> str:
    extra = []
    if platform and platform != "Any":
        # platform may be a comma-separated list of platforms
        label = "Platforms" if "," in platform else "Platform"
        extra.append(f"{label}: {platform}")
    if difficulty and difficulty != "Any":
        extra.append(f"Difficulty: {difficulty}")
    if extra:
        return prompt.strip() + "\n" + "\n".join(extra)
    return prompt.strip()


def _run_job(job_id: str) -> None:
    print(f"🏃 Job {job_id} thread started")
    with JOBS_LOCK:
        job = JOBS[job_id]
        job.status = "running"
        placeholder_mode = (job.error == "placeholder")
        job.error = None  # clear the flag
    
    timeout_triggered = False
    def mark_timeout():
        nonlocal timeout_triggered
        timeout_triggered = True
    
    timer = threading.Timer(120.0, mark_timeout)  # 2 minute timeout
    timer.daemon = True
    timer.start()
    
    try:
        print(f"📁 Creating temp directory for job {job_id}")
        out_dir = Path(tempfile.mkdtemp(prefix="tcg-web-"))
        orch = ScrapeOrchestrator(base_output=out_dir)

        final_prompt = _compose_prompt(job.prompt, job.platform, job.difficulty)
        _append_log(job, "Starting scraping workflow...")
        print(f"🔍 Job {job_id}: prompt='{job.prompt}', placeholder={placeholder_mode}")
        
        if placeholder_mode:
            _append_log(job, "Placeholder mode enabled - generating instant results...")
            include_sites = []  # Force placeholder
        else:
            include_sites = [s.strip() for s in (job.platform or "").split(",") if s.strip() and s.strip().lower() != "any"]
            if include_sites:
                _append_log(job, f"Limiting platforms to: {', '.join(include_sites)}")
            else:
                _append_log(job, "Using all available scrapers (this may take time).")
        
        print(f"🚀 Calling generate_bundle for job {job_id}")
        zip_path = orch.generate_bundle(
            final_prompt,
            log_callback=lambda m: _append_log(job, m),
            include_sites=include_sites or None,
        )
        print(f"✅ Job {job_id} bundle generated: {zip_path}", flush=True)
        
        timer.cancel()  # Cancel timeout if completed successfully
        print(f"⏰ Timer cancelled for job {job_id}", flush=True)
        
        if timeout_triggered:
            raise TimeoutError("Job timed out")
        
        print(f"📝 Updating job status to done for {job_id}", flush=True)
        with JOBS_LOCK:
            job.zip_path = zip_path
            job.status = "done"
            RECENTS.appendleft(job.id)
            _append_log(job, f"Bundle ready: {zip_path}")
        print(f"🎉 Job {job_id} completed successfully", flush=True)
    except TimeoutError as exc:
        print(f"⏱️ Job {job_id} timed out")
        timer.cancel()
        with JOBS_LOCK:
            job.status = "error"
            job.error = "Job timed out - try selecting fewer platforms or use placeholder mode"
            _append_log(job, f"Timeout: {exc}")
    except Exception as exc:  # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
        print(f"❌ Job {job_id} failed with error: {exc}")
        print(tb)
        timer.cancel()
        with JOBS_LOCK:
            job.status = "error"
            job.error = str(exc)
            _append_log(job, f"Error: {exc}")
    finally:
        with ACTIVE_LOCK:
            ACTIVE.discard(job_id)
        print(f"🏁 Job {job_id} thread finished")


def _supervisor_loop():
    print("🚀 Supervisor thread started")
    while True:
        # Launch jobs while capacity available
        launched = False
        with ACTIVE_LOCK:
            if QUEUE:
                print(f"📋 Queue has {len(QUEUE)} job(s), active: {len(ACTIVE)}")
            while len(ACTIVE) < MAX_CONCURRENT and QUEUE:
                job_id = QUEUE.popleft()
                ACTIVE.add(job_id)
                print(f"▶️  Launching job {job_id}")
                th = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
                th.start()
                launched = True
        if not launched:
            time.sleep(0.2)


@app.on_event("startup")
def _startup_supervisor():
    global SUPERVISOR_STARTED
    print("🔧 FastAPI startup event triggered")
    if not SUPERVISOR_STARTED:
        print("🚀 Starting supervisor thread...")
        t = threading.Thread(target=_supervisor_loop, daemon=True)
        t.start()
        SUPERVISOR_STARTED = True
        print("✅ Supervisor started")
    else:
        print("ℹ️  Supervisor already running")


class SubmitPayload(BaseModel):
    prompt: str
    platforms: List[str] = []
    difficulty: Optional[str] = None
    placeholderMode: bool = False


@app.post("/api/submit")
def api_submit(payload: SubmitPayload, request: Request):
    job_id = uuid.uuid4().hex[:12]
    platforms = ", ".join([p for p in payload.platforms if p])
    difficulty = payload.difficulty or "Any"
    job = Job(id=job_id, prompt=payload.prompt, platform=platforms or "Any", difficulty=difficulty)
    # Store placeholder mode flag
    job.error = "placeholder" if payload.placeholderMode else None  # reuse error field as a flag
    with JOBS_LOCK:
        JOBS[job_id] = job
    QUEUE.append(job_id)
    print(f"📝 Job {job_id} created and queued. Queue length: {len(QUEUE)}")
    return JSONResponse({
        "job_id": job_id,
        "status_url": str(request.url_for("job_status", job_id=job_id)),
    })


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": None,
            "placeholder": (
                "Describe the problems you need, e.g.\n"
                "'Give me 5 easy Codeforces array problems with input/output examples.'"
            ),
            "platforms": ["Any", "Codeforces", "LeetCode", "CodeChef", "GeeksforGeeks", "AtCoder"],
            "difficulties": ["Any", "Easy", "Medium", "Hard"],
        },
    )


@app.post("/submit")
def submit_job(
    request: Request,
    prompt: str = Form(...),
    platform: str = Form("Any"),
    difficulty: str = Form("Any"),
):
    job_id = uuid.uuid4().hex[:12]
    job = Job(id=job_id, prompt=prompt, platform=platform, difficulty=difficulty)
    with JOBS_LOCK:
        JOBS[job_id] = job
    QUEUE.append(job_id)
    dest = request.url_for("job_page", job_id=job_id)
    return RedirectResponse(url=str(dest), status_code=303)


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_page(request: Request, job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return HTMLResponse(f"<h3>Job {job_id} not found</h3>", status_code=404)
    return templates.TemplateResponse(
        "job.html",
        {
            "request": request,
            "job_id": job_id,
            "created": job.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "prompt": job.prompt,
            "platform": job.platform,
            "difficulty": job.difficulty,
        },
    )


@app.get("/jobs/{job_id}/status")
def job_status(request: Request, job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return JSONResponse({"error": "not-found"}, status_code=404)
        data = {
            "status": job.status,
            "logs": job.logs[-500:],  # cap
            "download_url": (str(request.url_for("download", job_id=job_id)) if job.status == "done" else None),
            "error": job.error,
        }
        return JSONResponse(data)


def _zip_roots(zf: zipfile.ZipFile) -> List[str]:
    roots: set[str] = set()
    for n in zf.namelist():
        part = n.split("/")[0]
        if part:
            roots.add(part)
    return sorted(roots)


def _read_first_text(zf: zipfile.ZipFile, paths: List[str]) -> Optional[str]:
    for p in paths:
        try:
            with zf.open(p) as fp:
                data = fp.read(4000).decode("utf-8", errors="replace")
                return data
        except KeyError:
            continue
        except Exception:
            continue
    return None


@app.get("/jobs/{job_id}/problems")
def job_problems(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job or not job.zip_path:
            return JSONResponse({"error": "not-found"}, status_code=404)
        zpath = job.zip_path
    items = []
    with zipfile.ZipFile(zpath, "r") as zf:
        roots = _zip_roots(zf)
        for r in roots:
            # Try to extract a description snippet
            desc = _read_first_text(zf, [
                f"{r}/README.md",
                f"{r}/README.txt",
                f"{r}/description.md",
                f"{r}/problem.md",
                f"{r}/DESC.txt",
            ])
            title = r
            if desc:
                # Use first non-empty line as title if it looks like a heading
                for line in desc.splitlines():
                    t = line.strip().lstrip("# ")
                    if t:
                        title = t[:120]
                        break
            items.append({"id": r, "name": title, "description": (desc or "")[:800]})
    return JSONResponse({"problems": items})


class ZipSelection(BaseModel):
    ids: List[str]


@app.post("/jobs/{job_id}/zip")
def zip_selected(job_id: str, payload: ZipSelection):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job or not job.zip_path:
            return JSONResponse({"error": "not-found"}, status_code=404)
        src_zip = job.zip_path
    # Build a filtered zip
    out_dir = Path(tempfile.mkdtemp(prefix="tcg-sel-"))
    dest = out_dir / f"{job_id}-selected.zip"
    include = set(payload.ids)
    with zipfile.ZipFile(src_zip, "r") as zsrc, zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zdst:
        for info in zsrc.infolist():
            root = info.filename.split("/")[0]
            if root in include:
                data = zsrc.read(info.filename)
                zdst.writestr(info, data)
    return FileResponse(path=dest, filename=dest.name, media_type="application/zip")


@app.get("/download/{job_id}")
def download(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job or not job.zip_path:
            return JSONResponse({"error": "not-found"}, status_code=404)
        return FileResponse(path=job.zip_path, filename=job.zip_path.name, media_type="application/zip")


@app.get("/recent", response_class=HTMLResponse)
def recent(request: Request):
    items = []
    with JOBS_LOCK:
        for jid in list(RECENTS):
            j = JOBS.get(jid)
            if j and j.zip_path:
                items.append(
                    {
                        "id": j.id,
                        "when": j.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "name": j.zip_path.name,
                    }
                )
    return templates.TemplateResponse("recent.html", {"request": request, "items": items})


def run() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    # Run without reload to keep it simple and compatible in venv
    uvicorn.run("webapp.main:app", host="127.0.0.1", port=port, reload=False)

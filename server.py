"""
CX Audit Web Server
--------------------
Flask server that serves the dashboard and provides REST APIs for:
  - Starting new audits
  - Polling run status
  - Listing/loading personas
  - Issues log (aggregated from journey_log.json friction points)

Usage:
    python -X utf8 server.py
    Then open http://localhost:5000
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import config

app = Flask(__name__, static_folder="dashboard", static_url_path="")
CORS(app)

# Active run tracking: run_id → {process, status, started_at, ...}
_active_runs: dict[str, dict] = {}
_lock = threading.Lock()

ISSUES_FILE = config.REPORTS_DIR / "issues.json"


# ── Static dashboard ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("dashboard", "index.html")


@app.route("/reports/<path:path>")
def serve_reports(path):
    return send_from_directory(str(config.REPORTS_DIR), path)


@app.route("/screenshots/<path:path>")
def serve_screenshots(path):
    return send_from_directory(str(config.SCREENSHOTS_DIR), path)


@app.route("/videos/<path:path>")
def serve_videos(path):
    return send_from_directory(str(config.VIDEOS_DIR), path)


@app.route("/logs/<path:path>")
def serve_logs(path):
    return send_from_directory(str(config.LOGS_DIR), path)


# ── Personas API ──────────────────────────────────────────────────────────────

@app.route("/api/personas", methods=["GET"])
def list_personas():
    """Return list of persona files with metadata."""
    personas_dir = config.BASE_DIR / "personas"
    files = []
    if personas_dir.exists():
        for f in personas_dir.glob("*.md"):
            size_kb = round(f.stat().st_size / 1024, 1)
            files.append({"name": f.name, "path": f"personas/{f.name}", "size_kb": size_kb})
    return jsonify({"files": files})


@app.route("/api/personas/parse", methods=["GET", "POST"])
def parse_personas():
    """Parse and return all personas from a file."""
    if request.method == "POST":
        # FormData: personas_file (upload) or personas_path (path string)
        uploaded = request.files.get("personas_file")
        if uploaded:
            import tempfile
            tmp = Path(tempfile.mktemp(suffix=".md"))
            uploaded.save(tmp)
            path = tmp
        else:
            ppath = request.form.get("personas_path", "")
            if ppath:
                path = config.BASE_DIR / ppath if not Path(ppath).is_absolute() else Path(ppath)
            else:
                return jsonify({"error": "No file or path provided"}), 400
    else:
        fname = request.args.get("file", "bajaj_personas.md")
        path  = config.BASE_DIR / "personas" / fname

    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    try:
        from parsers.persona_parser import PersonaParser
        personas = PersonaParser.parse(path)
        try:
            display_path = str(path.relative_to(config.BASE_DIR))
        except ValueError:
            display_path = str(path)
        result = {
            "path": display_path,
            "personas": [
                {
                    "name":        p.name,
                    "slug":        p.slug,
                    "intent":      p.intent,
                    "age":         str(p.age or ""),
                    "occupation":  p.occupation or "",
                    "product_tag": (p.raw_attributes or {}).get("product", "General"),
                }
                for p in personas
            ],
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/personas/create", methods=["POST"])
def create_personas():
    """Save inline personas to a temp .md file and return its path."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    personas = data.get("personas", [])
    if not personas:
        return jsonify({"error": "No personas provided"}), 400

    run_id = str(uuid.uuid4())[:8]
    temp_path = config.BASE_DIR / "personas" / f"_inline_{run_id}.md"
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for p in personas:
        lines.append(f"\n## Persona: {p.get('name', 'Unknown')}")
        for k, label in [
            ("intent", "Intent"), ("age", "Age"), ("occupation", "Occupation"),
            ("location", "Location"), ("financial_literacy", "Financial Literacy"),
            ("digital_proficiency", "Digital Proficiency"),
            ("behaviour", "Behaviour"), ("constraints", "Constraints"),
        ]:
            val = (p.get(k) or "").strip()
            if val:
                lines.append(f"- {label}: {val}")
    temp_path.write_text("\n".join(lines), encoding="utf-8")

    rel = str(temp_path.relative_to(config.BASE_DIR))
    return jsonify({"ok": True, "path": rel})


@app.route("/api/personas/add", methods=["POST"])
def add_persona():
    """Append a new persona to an existing personas file."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    fname = data.get("file", "bajaj_personas.md")
    path  = config.BASE_DIR / "personas" / fname
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["\n---\n"]
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    lines.append(f"## Persona: {name}")

    field_map = {
        "age": "Age", "gender": "Gender", "occupation": "Occupation",
        "location": "Location", "device": "Device",
        "financial_literacy": "Financial Literacy",
        "intent": "Intent", "constraints": "Constraints",
        "behaviour": "Behaviour", "background": "Background",
        "patience": "Patience", "navigation_style": "Navigation Style",
        "dropout_trigger": "Dropout Trigger", "success_criteria": "Success Criteria",
    }
    for key, label in field_map.items():
        val = data.get(key, "").strip()
        if val:
            lines.append(f"- {label}: {val}")

    block = "\n".join(lines) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)

    return jsonify({"ok": True, "persona": name})


# ── Manifest and results ──────────────────────────────────────────────────────

@app.route("/api/manifest")
def get_manifest():
    path = config.REPORTS_DIR / "manifest.json"
    if not path.exists():
        return jsonify({"slugs": [], "persona_count": 0})
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.route("/api/results/<slug>")
def get_result(slug):
    path = config.REPORTS_DIR / slug / "journey_log.json"
    if not path.exists():
        return jsonify({"error": "Not found"}), 404
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.route("/api/results")
def list_results():
    slugs = []
    if config.REPORTS_DIR.exists():
        for d in sorted(config.REPORTS_DIR.iterdir()):
            if d.is_dir() and (d / "journey_log.json").exists():
                slugs.append(d.name)
    return jsonify({"slugs": slugs})


# ── Runs API (dashboard-compatible) ──────────────────────────────────────────

@app.route("/api/runs", methods=["GET"])
def list_runs():
    """Return all completed runs (current + all archived) for the dashboard."""
    runs = []
    current_run_id = ""

    # Current run from manifest.json (no archived_reports_path — loaded directly)
    manifest_path = config.REPORTS_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            current_run_id = m.get("run_id", "")
            runs.append({
                "id":                    current_run_id,
                "status":                "complete",
                "manifest_slugs":        m.get("slugs", []),
                "created_at":            m.get("generated_at", ""),
                "archived_reports_path": None,
            })
        except Exception:
            pass

    # Archived runs — scan every subdirectory of run_archive/
    archive_root = config.REPORTS_DIR / "run_archive"
    if archive_root.is_dir():
        for run_dir in sorted(archive_root.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
            run_id = run_dir.name
            # Skip the current run — it's already loaded from manifest above
            if run_id == current_run_id:
                continue
            # Read the archived manifest to get slugs + metadata
            archived_manifest = run_dir / "manifest.json"
            slugs = []
            created_at = ""
            try:
                if archived_manifest.exists():
                    am = json.loads(archived_manifest.read_text(encoding="utf-8"))
                    slugs = am.get("slugs", [])
                    created_at = am.get("generated_at", "")
            except Exception:
                pass
            # Fall back to listing subdirectories as slugs if manifest is absent
            if not slugs:
                slugs = [d.name for d in run_dir.iterdir()
                         if d.is_dir() and (d / "journey_log.json").exists()]
            if not slugs:
                continue
            # Point screenshots/videos at the archived copies if they exist, so a
            # later same-persona run can't overwrite what this tile shows.
            _ss_dir = run_dir / "_screenshots"
            _vid_dir = run_dir / "_videos"
            runs.append({
                "id":                    run_id,
                "status":                "complete",
                "archived_slugs":        slugs,
                "created_at":            created_at,
                "archived_reports_path": f"reports/run_archive/{run_id}",
                "archived_screenshots_path": (
                    f"reports/run_archive/{run_id}/_screenshots" if _ss_dir.is_dir() else None
                ),
                "archived_videos_path": (
                    f"reports/run_archive/{run_id}/_videos" if _vid_dir.is_dir() else None
                ),
            })

    return jsonify({"runs": runs})


@app.route("/api/audit/start", methods=["POST"])
def start_audit():
    """Start a new web audit run (dashboard form submission)."""
    # Accept both JSON and FormData
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    run_id        = str(uuid.uuid4())[:8]
    target_url    = data.get("target_url", config.TARGET_URL)
    auth_mode     = data.get("auth_mode", "logged_out")
    eval_type     = data.get("eval_type", "both")
    start_from    = data.get("start_from", "homepage")
    max_steps     = int(data.get("max_steps", config.MAX_STEPS))
    personas_path = data.get("personas_path") or data.get("personas_file", "personas/bajaj_personas.md")
    login_user    = data.get("login_username", "")

    # Handle uploaded persona file
    uploaded = request.files.get("personas_file")
    if uploaded:
        import tempfile
        tmp = config.BASE_DIR / "personas" / f"_upload_{run_id}.md"
        uploaded.save(tmp)
        personas_path = str(tmp.relative_to(config.BASE_DIR))

    # Handle selected persona slugs
    selected_json = data.get("selected_personas", "")
    selected_slugs = []
    if selected_json:
        try:
            selected_slugs = json.loads(selected_json)
        except Exception:
            pass

    cmd = [
        sys.executable, "-X", "utf8", "main.py",
        "--target-url",    target_url,
        "--auth-mode",     auth_mode,
        "--eval-type",     eval_type,
        "--start-from",    start_from,
        "--max-steps",     str(max_steps),
        "--personas-file", personas_path,
        "--run-id",        run_id,
    ]
    if login_user and auth_mode == "logged_in":
        cmd += ["--login-username", login_user]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(config.BASE_DIR),
            env=env,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    with _lock:
        _active_runs[run_id] = {
            "process":    proc,
            "status":     "running",
            "started_at": time.time(),
            "cmd":        " ".join(cmd),
        }

    def _stream_log():
        log_file = config.LOGS_DIR / f"run_{run_id}.log"
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                for line in proc.stdout:
                    f.write(line)
                    f.flush()
        except Exception:
            pass
        proc.wait()
        with _lock:
            if run_id in _active_runs:
                _active_runs[run_id]["status"] = "complete" if proc.returncode == 0 else "failed"
                _active_runs[run_id]["exit_code"] = proc.returncode

    threading.Thread(target=_stream_log, daemon=True).start()

    return jsonify({"run_id": run_id, "status": "running", "audit_type": "web"})


# Legacy alias
@app.route("/api/run", methods=["POST"])
def start_run_legacy():
    return start_audit()


@app.route("/api/runs/<run_id>/status", methods=["GET"])
def run_status(run_id):
    with _lock:
        run = _active_runs.get(run_id)

    log_path = config.LOGS_DIR / f"run_{run_id}.log"
    last_lines: list[str] = []
    if log_path.exists():
        try:
            all_lines = log_path.read_text(encoding="utf-8").splitlines()
            last_lines = all_lines[-20:]
        except Exception:
            pass

    if not run:
        manifest_path = config.REPORTS_DIR / "manifest.json"
        if manifest_path.exists():
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            if m.get("run_id") == run_id:
                return jsonify({
                    "run_id":         run_id,
                    "status":         "complete",
                    "manifest_slugs": m.get("slugs", []),
                    "log_tail":       "\n".join(last_lines),
                })
        return jsonify({"run_id": run_id, "status": "unknown"})

    status = run.get("status", "running")

    # Attach manifest slugs when complete
    manifest_slugs = []
    if status in ("complete", "failed"):
        manifest_path = config.REPORTS_DIR / "manifest.json"
        if manifest_path.exists():
            try:
                m = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest_slugs = m.get("slugs", [])
            except Exception:
                pass

    return jsonify({
        "run_id":         run_id,
        "status":         status,
        "manifest_slugs": manifest_slugs,
        "log_tail":       "\n".join(last_lines),
    })


# Legacy alias
@app.route("/api/run/<run_id>/status", methods=["GET"])
def run_status_legacy(run_id):
    return run_status(run_id)


@app.route("/api/runs/<run_id>/cancel", methods=["POST"])
def cancel_run(run_id):
    with _lock:
        run = _active_runs.get(run_id)
    if run:
        proc = run.get("process")
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
        with _lock:
            _active_runs[run_id]["status"] = "cancelled"
    return jsonify({"ok": True})


@app.route("/api/run/<run_id>/log", methods=["GET"])
def run_log(run_id):
    log_path = config.LOGS_DIR / f"run_{run_id}.log"
    if not log_path.exists():
        return jsonify({"lines": []})
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return jsonify({"lines": lines})


# ── Delete run ────────────────────────────────────────────────────────────────

def _remove_slug_from_manifest(manifest_path, slug):
    """Drop a slug from a manifest.json so a deleted run does not reappear."""
    try:
        if not manifest_path.exists():
            return
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(m.get("slugs"), list) and slug in m["slugs"]:
            m["slugs"] = [s for s in m["slugs"] if s != slug]
            if "persona_count" in m:
                m["persona_count"] = len(m["slugs"])
            manifest_path.write_text(json.dumps(m, indent=2), encoding="utf-8")
    except Exception:
        pass


def _prune_archive_index(index_path, run_id, slug):
    """Remove a slug (or the whole entry if now empty) from archive_index.json."""
    try:
        if not index_path.exists():
            return
        idx = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(idx, list):
            return
        out = []
        for e in idx:
            if e.get("run_id") == run_id:
                slugs = [s for s in e.get("slugs", []) if s != slug]
                if not slugs:
                    continue  # drop the whole archive entry
                e["slugs"] = slugs
                e["persona_count"] = len(slugs)
            out.append(e)
        index_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    except Exception:
        pass


@app.route("/api/persona-runs/<slug>", methods=["DELETE"])
def delete_persona_run(slug):
    """
    Delete ONE specific persona run permanently (survives reload). Scoped by
    run_id + slug — deleting one run of a persona never touches its other runs.
    """
    import shutil
    run_id = request.args.get("run_id", "")
    reports = config.REPORTS_DIR

    # Is this the current (live) run or an archived one?
    manifest_path = reports / "manifest.json"
    current_run_id = ""
    try:
        if manifest_path.exists():
            current_run_id = json.loads(manifest_path.read_text(encoding="utf-8")).get("run_id", "")
    except Exception:
        current_run_id = ""

    is_current = (not run_id) or (run_id == current_run_id)

    if is_current:
        # Live run — remove the persona dir, its manifest entry, and its issues.
        run_dir = reports / slug
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
        _remove_slug_from_manifest(manifest_path, slug)
        _remove_issues_for_slug(slug)
    else:
        # Archived run — remove the persona dir + its archived media, and prune
        # the manifest + archive_index so it doesn't reappear on reload.
        arch = reports / "run_archive" / run_id
        for p in (arch / slug, arch / "_screenshots" / slug):
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
        vid = arch / "_videos" / f"{slug}.webm"
        try:
            if vid.exists():
                vid.unlink()
        except Exception:
            pass
        _remove_slug_from_manifest(arch / "manifest.json", slug)
        _prune_archive_index(reports / "run_archive" / "archive_index.json", run_id, slug)
        # If no personas remain in this archive, remove the whole archive dir.
        try:
            remaining = [x for x in arch.iterdir()
                         if x.is_dir() and not x.name.startswith("_")
                         and (x / "journey_log.json").exists()]
            if not remaining:
                shutil.rmtree(arch, ignore_errors=True)
        except Exception:
            pass

    return jsonify({"ok": True})


@app.route("/api/results/<slug>", methods=["DELETE"])
def delete_result(slug):
    """Legacy delete endpoint."""
    import shutil
    run_dir = config.REPORTS_DIR / slug
    if run_dir.exists():
        shutil.rmtree(run_dir, ignore_errors=True)
    return jsonify({"ok": True})


# ── Issues API ────────────────────────────────────────────────────────────────

def _load_issues_store() -> dict:
    """Load the persistent issues store."""
    if ISSUES_FILE.exists():
        try:
            return json.loads(ISSUES_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"issues": [], "resolved": {}, "deleted": set()}


def _save_issues_store(store: dict) -> None:
    store_copy = dict(store)
    store_copy["deleted"] = list(store.get("deleted", set()))
    ISSUES_FILE.write_text(json.dumps(store_copy, indent=2), encoding="utf-8")


def _remove_issues_for_slug(slug: str) -> None:
    store = _load_issues_store()
    store["issues"] = [i for i in store.get("issues", []) if i.get("persona_slug") != slug]
    _save_issues_store(store)


def _aggregate_issues() -> list[dict]:
    """Build fresh issues from all persona journey_log.json files."""
    issues = []
    if not config.REPORTS_DIR.exists():
        return issues

    for slug_dir in sorted(config.REPORTS_DIR.iterdir()):
        if not slug_dir.is_dir():
            continue
        log_path = slug_dir / "journey_log.json"
        if not log_path.exists():
            continue
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        journey   = data.get("journey", {})
        cx_audit  = data.get("cx_audit") or {}
        design    = data.get("design_audit") or {}
        content   = data.get("content_analysis") or {}
        persona_name = journey.get("persona", slug_dir.name)
        product_tag  = (journey.get("persona_data") or {}).get("product", "General")

        # CX friction points
        for fp in cx_audit.get("friction_points", []):
            issues.append({
                "id":             f"cx_{slug_dir.name}_{len(issues)}",
                "persona_slug":   slug_dir.name,
                "persona_name":   persona_name,
                "product_tag":    product_tag,
                "issue_category": "cx",
                "priority":       "P1" if fp.get("severity") == "high" else "P2" if fp.get("severity") == "medium" else "P3",
                "title":          fp.get("description", "")[:120],
                "description":    fp.get("description", ""),
                "location":       fp.get("location", ""),
                "impact":         fp.get("impact", ""),
                "recommendation": "",
                "status":         "open",
                "created_at":     journey.get("started_at", ""),
            })

        # CX recommendations → P1 as issues
        for r in cx_audit.get("recommendations", []):
            if r.get("priority") == "P1":
                issues.append({
                    "id":             f"rec_{slug_dir.name}_{len(issues)}",
                    "persona_slug":   slug_dir.name,
                    "persona_name":   persona_name,
                    "product_tag":    product_tag,
                    "issue_category": "cx",
                    "priority":       "P1",
                    "title":          r.get("area", "")[:80],
                    "description":    r.get("action", ""),
                    "location":       r.get("area", ""),
                    "impact":         r.get("expected_impact", ""),
                    "recommendation": r.get("action", ""),
                    "status":         "open",
                    "created_at":     journey.get("started_at", ""),
                })

        # Design issues
        for di in design.get("issues", []):
            issues.append({
                "id":             f"design_{slug_dir.name}_{len(issues)}",
                "persona_slug":   slug_dir.name,
                "persona_name":   persona_name,
                "product_tag":    product_tag,
                "issue_category": "design",
                "priority":       "P1" if di.get("severity") == "high" else "P2" if di.get("severity") == "medium" else "P3",
                "title":          (di.get("title") or di.get("element") or di.get("description", ""))[:120],
                "description":    di.get("description", ""),
                "location":       di.get("element", ""),
                "impact":         "",
                "recommendation": di.get("recommendation") or di.get("fix", ""),
                "status":         "open",
                "created_at":     journey.get("started_at", ""),
            })

        # Content gaps
        for gap in content.get("content_gaps", []):
            issues.append({
                "id":             f"content_{slug_dir.name}_{len(issues)}",
                "persona_slug":   slug_dir.name,
                "persona_name":   persona_name,
                "product_tag":    product_tag,
                "issue_category": "content",
                "priority":       "P2",
                "title":          gap[:120],
                "description":    gap,
                "location":       "",
                "impact":         "",
                "recommendation": "",
                "status":         "open",
                "created_at":     journey.get("started_at", ""),
            })

    return issues


@app.route("/api/issues", methods=["GET"])
def list_issues():
    sort     = request.args.get("sort", "priority")
    product  = request.args.get("product", "")
    priority = request.args.get("priority", "")
    status   = request.args.get("status", "")

    # Load or rebuild issues
    store = _load_issues_store()
    fresh = _aggregate_issues()

    # Merge: preserve status overrides from store
    status_map  = {i["id"]: i.get("status", "open") for i in store.get("issues", [])}
    deleted_set = set(store.get("deleted", []))

    issues = []
    for i in fresh:
        if i["id"] in deleted_set:
            continue
        i = dict(i)
        if i["id"] in status_map:
            i["status"] = status_map[i["id"]]
        issues.append(i)

    # Apply filters
    if product:
        issues = [i for i in issues if i.get("product_tag") == product]
    if priority:
        issues = [i for i in issues if i.get("priority") == priority]
    if status:
        issues = [i for i in issues if i.get("status") == status]

    # Sort
    prio_order = {"P1": 0, "P2": 1, "P3": 2}
    sev_order  = {"high": 0, "medium": 1, "low": 2}
    if sort == "priority":
        issues.sort(key=lambda i: prio_order.get(i.get("priority", "P3"), 3))
    elif sort == "persona":
        issues.sort(key=lambda i: i.get("persona_name", ""))
    elif sort == "category":
        issues.sort(key=lambda i: i.get("issue_category", ""))

    products = sorted({i.get("product_tag", "General") for i in issues})

    return jsonify({"issues": issues, "products": products})


@app.route("/api/issues/<issue_id>", methods=["PATCH"])
def update_issue(issue_id):
    data  = request.get_json() or {}
    store = _load_issues_store()

    # Update or insert into store
    existing = next((i for i in store.get("issues", []) if i["id"] == issue_id), None)
    if existing:
        existing.update(data)
    else:
        store.setdefault("issues", []).append({"id": issue_id, **data})

    _save_issues_store(store)
    return jsonify({"ok": True})


@app.route("/api/issues/<issue_id>", methods=["DELETE"])
def delete_issue(issue_id):
    store = _load_issues_store()
    deleted = set(store.get("deleted", []))
    deleted.add(issue_id)
    store["deleted"] = deleted
    store["issues"] = [i for i in store.get("issues", []) if i["id"] != issue_id]
    _save_issues_store(store)
    return jsonify({"ok": True})


# ── App audit stub (for dashboard compatibility) ──────────────────────────────

@app.route("/api/audit/app/start", methods=["POST"])
def start_app_audit():
    return jsonify({"error": "App (mobile/Appium) audit is not supported in this build"}), 400


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("CX Audit Platform running at http://localhost:5000")
    print("Open the dashboard in your browser.")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

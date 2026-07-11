"""
Repair screen recordings for runs completed before the video-consolidation fix.

Playwright records one raw file per page under videos/<slug>/<hash>.webm, but
older runs never consolidated them into the flat videos/<slug>.webm that the
report + dashboard reference. This walks a project root and:

  1. Consolidates the largest raw recording into videos/<slug>.webm
  2. Backfills journey_log.video_path (live reports + archived runs) so the
     dashboard shows the video without needing the /api/video server fallback
  3. Ensures each archived run keeps its own copy under _videos/<slug>.webm

Usage:
    python fix_videos.py [PROJECT_ROOT]        # defaults to the current folder
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def _largest_raw(raw_dir: Path) -> Path | None:
    if not raw_dir.is_dir():
        return None
    webms = sorted(raw_dir.glob("*.webm"), key=lambda p: p.stat().st_size, reverse=True)
    return webms[0] if webms else None


def _patch_video_path(jl_path: Path, slug: str, changed: list[str]) -> None:
    """Set journey.video_path to videos/<slug>.webm when it is empty.
    The dashboard's artifactRel() only uses the basename, so the same value
    resolves for both live (/videos) and archived (_videos) bases."""
    try:
        data = json.loads(jl_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  ! could not read {jl_path}: {exc}")
        return
    journey = data.get("journey") if isinstance(data.get("journey"), dict) else data
    if journey.get("video_path"):
        return
    journey["video_path"] = f"videos/{slug}.webm"
    jl_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    changed.append(f"patched video_path → {jl_path}")


def fix_root(root: Path) -> list[str]:
    changed: list[str] = []
    videos = root / "videos"
    reports = root / "reports"

    # 1. Consolidate raw → flat and remember which slugs have a flat file.
    flat_for: dict[str, Path] = {}
    if videos.is_dir():
        for sub in videos.iterdir():
            if not sub.is_dir():
                continue
            slug = sub.name
            flat = videos / f"{slug}.webm"
            if not flat.exists():
                raw = _largest_raw(sub)
                if raw:
                    shutil.copy2(raw, flat)
                    changed.append(f"consolidated {slug}.webm ({raw.stat().st_size // 1024} KB)")
            if flat.exists():
                flat_for[slug] = flat

    if not reports.is_dir():
        return changed

    # 2. Live reports/<slug>/journey_log.json
    for sub in reports.iterdir():
        if sub.is_dir() and sub.name != "run_archive":
            jl = sub / "journey_log.json"
            if jl.exists() and sub.name in flat_for:
                _patch_video_path(jl, sub.name, changed)

    # 3. Archived runs: patch json + ensure _videos/<slug>.webm exists.
    arch_root = reports / "run_archive"
    if arch_root.is_dir():
        for run in arch_root.iterdir():
            if not run.is_dir():
                continue
            arch_vid = run / "_videos"
            for sub in run.iterdir():
                if not sub.is_dir() or sub.name.startswith("_"):
                    continue
                slug = sub.name
                if slug not in flat_for:
                    continue
                jl = sub / "journey_log.json"
                if jl.exists():
                    _patch_video_path(jl, slug, changed)
                dest = arch_vid / f"{slug}.webm"
                if not dest.exists():
                    arch_vid.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(flat_for[slug], dest)
                    changed.append(f"archived _videos/{slug}.webm")

    return changed


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"Repairing videos under: {root}")
    changes = fix_root(root)
    if changes:
        for c in changes:
            print(f"  [ok] {c}")
        print(f"\nDone - {len(changes)} change(s).")
    else:
        print("  Nothing to repair (no raw recordings found, or all already consolidated).")

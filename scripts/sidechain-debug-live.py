#!/usr/bin/env python3
"""Operational-only live debugger for the Chronicle sidechain evidence workflow.

This file never changes evidence acceptance. It only observes existing progress/diagnostic
files and emits a compact current-state snapshot plus an append-only event stream.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import pathlib
import subprocess
import time
from typing import Any

ROOT = pathlib.Path("artifacts/chronicle-sidechain-scan")
RUNTIME = ROOT / "runtime"
DEBUG_FILE = RUNTIME / "SIDECHAIN-DEBUG.json"
DEBUG_TRACE = RUNTIME / "SIDECHAIN-DEBUG.jsonl"
STAGE_FILE = RUNTIME / "WORKFLOW-STAGE.json"
ISSUE = os.environ.get("CHRONICLE_PROGRESS_ISSUE", "1020")
INTERVAL = max(10, int(os.environ.get("CHRONICLE_DEBUG_PUBLISH_SECONDS", "15")))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def first_json(patterns: list[str]) -> tuple[str | None, Any]:
    for pattern in patterns:
        if not pattern:
            continue
        for raw in glob.glob(pattern, recursive=True):
            p = pathlib.Path(raw)
            if p.is_file():
                obj = read_json(p)
                if obj is not None:
                    return str(p), obj
    return None, None


def atomic_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_event(event: str, detail: dict[str, Any]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": now(),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "source_sha": os.environ.get("GITHUB_SHA"),
        "event": event,
        "detail": detail,
    }
    with DEBUG_TRACE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def stage() -> dict[str, Any]:
    obj = read_json(STAGE_FILE)
    return obj if isinstance(obj, dict) else {}


def latest_trace_tail(limit: int = 12) -> list[Any]:
    candidates = list(ROOT.glob("**/CAR-TRACE.jsonl")) + list(pathlib.Path("runtime").glob("CAR-TRACE.jsonl"))
    for path in candidates:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
            out = []
            for line in lines:
                try:
                    out.append(json.loads(line))
                except Exception:
                    out.append({"raw": line[:1000]})
            return out
        except Exception:
            continue
    return []


def active_workers(car: dict[str, Any]) -> list[dict[str, Any]]:
    workers = car.get("workers") or {}
    if isinstance(workers, list):
        vals = [dict(v) if isinstance(v, dict) else {"detail": v} for v in workers]
    elif isinstance(workers, dict):
        vals = [{"worker": k, **(v if isinstance(v, dict) else {"detail": v})} for k, v in workers.items()]
    else:
        vals = []
    stamp = dt.datetime.now(dt.timezone.utc)
    for item in vals:
        started = item.get("started_at")
        if started:
            try:
                t = dt.datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                item["elapsed_seconds"] = max(0, int((stamp - t).total_seconds()))
            except Exception:
                pass
        if not item.get("asset_id") and item.get("chain") and item.get("contract") and item.get("token_id") is not None:
            item["asset_id"] = f"{item.get('chain')}:{item.get('contract')}/{item.get('token_id')}"
    return vals


def summarize_rebuild(rebuild: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(rebuild, dict):
        return {}
    return {
        "schema": rebuild.get("schema"),
        "started_at": rebuild.get("started_at"),
        "finished_at": rebuild.get("finished_at"),
        "roots_mapped": rebuild.get("roots_mapped"),
        "refs_mapped": rebuild.get("refs_mapped"),
        "roots_with_candidates": rebuild.get("roots_with_candidates"),
        "roots_without_candidates": rebuild.get("roots_without_candidates"),
        "roots_considered": rebuild.get("roots_considered"),
        "already_valid": rebuild.get("already_valid"),
        "invalid_removed": rebuild.get("invalid_removed"),
        "direct_raw_rebuilt": rebuild.get("direct_raw_rebuilt"),
        "kubo_rebuilt": rebuild.get("kubo_rebuilt"),
        "recovered_count": len(rebuild.get("recovered") or []),
        "unrecovered_count": len(rebuild.get("unrecovered") or []),
        "recovered": (rebuild.get("recovered") or [])[:20],
        "unrecovered": (rebuild.get("unrecovered") or [])[:20],
    }


def problem_root_mapping(cache: dict[str, Any], root_map: dict[str, Any], failed: list[str]) -> list[dict[str, Any]]:
    problem_roots: list[str] = []
    for error in cache.get("errors") or []:
        if isinstance(error, dict) and error.get("root_cid") and error["root_cid"] not in problem_roots:
            problem_roots.append(error["root_cid"])
    for cid in failed:
        if cid and cid not in problem_roots:
            problem_roots.append(cid)
    mapped = {}
    for row in root_map.get("roots") or []:
        if isinstance(row, dict) and row.get("root_cid"):
            mapped[row["root_cid"]] = row
    out = []
    for cid in problem_roots[:40]:
        row = mapped.get(cid) or {}
        refs = []
        for ref in (row.get("refs") or [])[:8]:
            if not isinstance(ref, dict):
                continue
            refs.append({
                "asset_id": ref.get("asset_id"),
                "role": ref.get("role"),
                "leaf_path": ref.get("leaf_path"),
                "original_uri": ref.get("original_uri"),
                "payload_status": ref.get("payload_status"),
                "declared_file": ref.get("declared_file"),
                "declared_file_exists": ref.get("declared_file_exists"),
                "candidate_count": len(ref.get("candidates") or []),
                "candidates": (ref.get("candidates") or [])[:8],
            })
        out.append({
            "root_cid": cid,
            "mapped": bool(row),
            "ref_count": row.get("ref_count"),
            "candidate_count": row.get("candidate_count"),
            "refs": refs,
        })
    return out


def build_snapshot() -> dict[str, Any]:
    stage_obj = stage()
    car_path, car = first_json([
        "artifacts/chronicle-sidechain-scan/**/CAR-PROGRESS.json",
        "runtime/CAR-PROGRESS.json",
    ])
    l2_path, l2 = first_json([
        os.environ.get("CHRONICLE_L2_PROGRESS_FILE", "/tmp/chronicle-sidechain-l2-progress.json"),
        "/tmp/chronicle-sidechain-l2-progress.json",
        "**/chronicle-sidechain-l2-progress.json",
    ])
    rebuild_path, rebuild = first_json([
        "artifacts/chronicle-sidechain-scan/**/HISTORICAL-CAR-REBUILD.json",
        "runtime/HISTORICAL-CAR-REBUILD.json",
    ])
    root_map_path, root_map = first_json([
        "artifacts/chronicle-sidechain-scan/**/HISTORICAL-CAR-ROOT-MAP.json",
        "runtime/HISTORICAL-CAR-ROOT-MAP.json",
    ])
    offline_path, offline = first_json(["artifacts/chronicle-sidechain-scan/**/OFFLINE-VERIFICATION.json"])
    l1_path, l1 = first_json([
        "artifacts/chronicle-sidechain-scan/**/L1-LEAF-DIAGNOSTICS.json",
        "runtime/L1-LEAF-DIAGNOSTICS.json",
    ])
    car = car if isinstance(car, dict) else {}
    l2 = l2 if isinstance(l2, dict) else {}
    rebuild = rebuild if isinstance(rebuild, dict) else {}
    root_map = root_map if isinstance(root_map, dict) else {}
    offline = offline if isinstance(offline, dict) else {}
    l1 = l1 if isinstance(l1, dict) else {}

    cache = car.get("cache_audit") or {}
    failed = car.get("failed_cids") or []
    root_details = problem_root_mapping(cache, root_map, failed)
    snapshot = {
        "schema": "trinity-accord/chronicle-sidechain-debug/v2",
        "operational_only": True,
        "timestamp": now(),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "source_sha": os.environ.get("GITHUB_SHA"),
        "phase": stage_obj.get("phase") or car.get("phase") or l2.get("phase") or "unknown",
        "step": stage_obj.get("step") or car.get("current_substep") or "unknown",
        "step_status": stage_obj.get("status") or car.get("status") or "running",
        "step_started_at": stage_obj.get("started_at"),
        "car": {
            "records_completed": car.get("records_completed"),
            "records_expected": car.get("records_expected"),
            "cache_checked": cache.get("checked"),
            "cache_valid": cache.get("valid"),
            "cache_removed": cache.get("removed"),
            "problem_root_count": len(root_details),
            "problem_roots": root_details,
            "failed_count": len(failed),
            "failed_cids": failed,
            "last_cid": car.get("last_cid"),
            "last_event": car.get("last_event"),
            "last_event_at": car.get("last_event_at"),
            "last_event_detail": car.get("last_event_detail"),
            "historical_rebuild_live": car.get("historical_car_rebuild_live"),
            "workers": active_workers(car),
            "recent_recovery_events": (car.get("recent_recovery_events") or [])[-12:],
            "recent_failures": (car.get("recent_failures") or [])[-12:],
        },
        "l2": {
            "blocks_completed": l2.get("blocks_completed"),
            "blocks_failed": l2.get("blocks_failed"),
            "unique_blocks_total": l2.get("unique_blocks_total"),
            "records_pass": l2.get("records_pass"),
            "records_expected": l2.get("records_expected"),
            "last_event": (l2.get("events") or [])[-1] if isinstance(l2.get("events"), list) and l2.get("events") else None,
        },
        "historical_rebuild": summarize_rebuild(rebuild),
        "offline_verification": {
            "pass": offline.get("pass"),
            "error_count": len(offline.get("errors") or []) if isinstance(offline.get("errors"), list) else offline.get("error_count"),
            "errors": (offline.get("errors") or [])[:20] if isinstance(offline.get("errors"), list) else None,
        },
        "l1_diagnostics": l1,
        "trace_tail": latest_trace_tail(),
        "sources": {
            "car": car_path,
            "l2": l2_path,
            "historical_rebuild": rebuild_path,
            "historical_root_map": root_map_path,
            "offline": offline_path,
            "l1": l1_path,
        },
    }
    return snapshot


def compact_markdown(s: dict[str, Any]) -> str:
    c, l2 = s["car"], s["l2"]
    workers = c.get("workers") or []
    worker_lines = []
    for w in workers[:8]:
        worker_lines.append(
            f"- worker `{w.get('worker', '?')}` asset=`{w.get('asset_id', '?')}` record={w.get('record_index', '?')}/{w.get('total', '?')} elapsed={w.get('elapsed_seconds', '?')}s"
        )
    if not worker_lines:
        worker_lines = ["- no active worker snapshot"]
    root_lines = []
    for row in (c.get("problem_roots") or [])[:20]:
        refs = row.get("refs") or []
        first = refs[0] if refs else {}
        root_lines.append(
            f"- `{row.get('root_cid')}` mapped={row.get('mapped')} candidates={row.get('candidate_count')} refs={row.get('ref_count')} asset=`{first.get('asset_id')}` role=`{first.get('role')}` status=`{first.get('payload_status')}`"
        )
    if not root_lines:
        root_lines = ["- no strict-cache problem roots"]
    rebuild = s.get("historical_rebuild") or {}
    last_problem = None
    failures = c.get("recent_failures") or []
    if failures:
        last_problem = failures[-1]
    elif c.get("last_event_detail"):
        last_problem = c.get("last_event_detail")
    lines = [
        "# Sidechain evidence live debug",
        "",
        "> Operational telemetry only. This does not amend Canon or evidence contents.",
        "",
        f"- Run: `{s.get('run_id')}` attempt `{s.get('run_attempt')}`",
        f"- Source SHA: `{s.get('source_sha')}`",
        f"- Current phase: **{s.get('phase')}**",
        f"- Current step: **{s.get('step')}** — `{s.get('step_status')}`",
        f"- Heartbeat: `{s.get('timestamp')}`",
        f"- CAR records: **{c.get('records_completed')}/{c.get('records_expected')}**; strict cache **{c.get('cache_valid')}/{c.get('cache_checked')}**; problem roots **{c.get('problem_root_count')}**; final failed roots **{c.get('failed_count')}**",
        f"- Historical local rebuild: mapped **{rebuild.get('roots_mapped')}** roots, with candidates **{rebuild.get('roots_with_candidates')}**, without candidates **{rebuild.get('roots_without_candidates')}**, exact rebuilt **{(rebuild.get('direct_raw_rebuilt') or 0) + (rebuild.get('kubo_rebuilt') or 0)}**, unrecovered **{rebuild.get('unrecovered_count')}**",
        f"- L2: blocks **{l2.get('blocks_completed')}/{l2.get('unique_blocks_total')}**, failed **{l2.get('blocks_failed')}**, records pass **{l2.get('records_pass')}/{l2.get('records_expected')}**",
        "",
        "## Active workers",
        *worker_lines,
        "",
        "## Strict-cache problem roots",
        *root_lines,
        "",
        f"## Last event\n`{str(c.get('last_event_detail') or c.get('last_event') or 'none')[:1800]}`",
        "",
        f"## Latest problem\n```json\n{json.dumps(last_problem, ensure_ascii=False, indent=2)[:5000]}\n```",
        "",
        "## Machine snapshot",
        "```json",
        json.dumps(s, ensure_ascii=False, indent=2)[:45000],
        "```",
    ]
    return "\n".join(lines)


def publish_issue(snapshot: dict[str, Any]) -> None:
    if not os.environ.get("GH_TOKEN"):
        return
    body = compact_markdown(snapshot)
    tmp = pathlib.Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "sidechain-debug-issue.md"
    tmp.write_text(body, encoding="utf-8")
    subprocess.run(
        ["gh", "issue", "edit", ISSUE, "--repo", os.environ.get("GITHUB_REPOSITORY", "thechurchofagi/trinity-accord"), "--body-file", str(tmp)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def snapshot_and_publish(event: str = "heartbeat") -> dict[str, Any]:
    s = build_snapshot()
    atomic_json(DEBUG_FILE, s)
    append_event(event, {
        "phase": s.get("phase"),
        "step": s.get("step"),
        "step_status": s.get("step_status"),
        "car_records_completed": s["car"].get("records_completed"),
        "car_problem_root_count": s["car"].get("problem_root_count"),
        "car_failed_count": s["car"].get("failed_count"),
        "l2_blocks_completed": s["l2"].get("blocks_completed"),
    })
    publish_issue(s)
    print(
        f"[SIDECHAIN DEBUG] phase={s.get('phase')} step={s.get('step')} status={s.get('step_status')} "
        f"car={s['car'].get('records_completed')}/{s['car'].get('records_expected')} "
        f"problem_roots={s['car'].get('problem_root_count')} failed={s['car'].get('failed_count')} "
        f"l2={s['l2'].get('blocks_completed')}/{s['l2'].get('unique_blocks_total')}",
        flush=True,
    )
    return s


def mark(args: argparse.Namespace) -> None:
    old = stage()
    started = old.get("started_at") if old.get("phase") == args.phase and old.get("step") == args.step else now()
    obj = {
        "phase": args.phase,
        "step": args.step,
        "status": args.status,
        "detail": args.detail,
        "started_at": started,
        "updated_at": now(),
    }
    atomic_json(STAGE_FILE, obj)
    append_event("stage_mark", obj)
    snapshot_and_publish("stage_snapshot")


def stream(args: argparse.Namespace) -> int:
    pid = args.pid
    append_event("stream_start", {"pid": pid, "interval_seconds": INTERVAL})
    while True:
        snapshot_and_publish("heartbeat")
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(INTERVAL)
    snapshot_and_publish("stream_stop")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mark")
    m.add_argument("--phase", required=True)
    m.add_argument("--step", required=True)
    m.add_argument("--status", default="running")
    m.add_argument("--detail", default="")
    s = sub.add_parser("stream")
    s.add_argument("--pid", required=True, type=int)
    sub.add_parser("snapshot")
    args = p.parse_args()
    if args.cmd == "mark":
        mark(args)
    elif args.cmd == "stream":
        return stream(args)
    else:
        snapshot_and_publish("manual_snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

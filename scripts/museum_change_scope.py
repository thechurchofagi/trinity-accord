#!/usr/bin/env python3
"""Conservatively classify isolated museum edits; uncertainty runs full checks."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}\Z")


def museum_paths(paths: list[str]) -> bool:
    return bool(paths) and all(
        path.startswith("museum/")
        and ".." not in PurePosixPath(path).parts
        and "\\" not in path
        for path in paths
    )


def git(*args: str, root: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE, timeout=45)


def ensure_commit(sha: str, root: Path = ROOT) -> None:
    if not isinstance(sha, str) or not SHA.fullmatch(sha) or sha == "0" * 40:
        raise ValueError("missing or invalid comparison commit")
    try:
        git("cat-file", "-e", sha + "^{commit}", root=root)
    except subprocess.CalledProcessError:
        git("fetch", "--no-tags", "--depth=1", "origin", sha, root=root)
        git("cat-file", "-e", sha + "^{commit}", root=root)


def changed_paths(base: str, head: str, root: Path = ROOT) -> list[str]:
    ensure_commit(base, root)
    ensure_commit(head, root)
    # No API file-count limit, and both sides of a rename are included.
    raw = git("diff", "--no-renames", "--name-only", "-z", base, head, "--", root=root)
    return [p.decode("utf-8") for p in raw.split(b"\0") if p]


def ordinary_museum_tree(head: str, root: Path = ROOT) -> bool:
    rows = git("ls-tree", "-r", "-z", head, "--", "museum/", root=root).split(b"\0")
    # A symlink or submodule can escape the static export boundary.
    return all(not row or row.split(b" ", 1)[0] in (b"100644", b"100755") for row in rows)


def previous_pages_sha(repo: str, current_id: str, created: str, token: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not token:
        raise ValueError("Pages baseline lookup unavailable")
    url = ("https://api.github.com/repos/" + repo
           + "/actions/workflows/deploy-pages.yml/runs?branch=main&status=success&per_page=100")
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        runs = json.load(response)["workflow_runs"]
    candidates = [r for r in runs if str(r["id"]) != current_id
                  and r.get("conclusion") == "success" and r.get("event") == "push"
                  and r.get("head_branch") == "main"
                  and r.get("head_repository", {}).get("full_name") == repo
                  and (not created or r.get("created_at", "") < created)]
    if not candidates:
        raise ValueError("no prior successful main Pages push")
    return max(candidates, key=lambda r: r["created_at"])["head_sha"]


def classify(event: dict, event_name: str, head: str, *, deployment: bool = False,
             root: Path = ROOT, baseline_lookup=previous_pages_sha) -> dict:
    result = {"museum_only": False, "baseline_sha": "", "changed_count": 0,
              "reason": "full checks are the default"}
    try:
        if event_name == "pull_request" and not deployment:
            base = event["pull_request"]["base"]["sha"]
        elif event_name == "push":
            if event.get("after") != head:
                raise ValueError("checkout does not match the pushed commit")
            base = event["before"]
        elif event_name == "workflow_run" and deployment:
            run = event["workflow_run"]
            if (run.get("event") != "push" or run.get("head_branch") != "main"
                    or run.get("head_sha") != head or run.get("conclusion") != "success"
                    or run.get("head_repository", {}).get("full_name") != event["repository"]["full_name"]):
                raise ValueError("not a successful matching main Pages push")
            base = ""  # The successful publication baseline supplies the range below.
        else:
            raise ValueError("manual, scheduled, or unknown event requires full checks")
        if event_name != "workflow_run":
            paths = changed_paths(base, head, root)
            result["changed_count"] = len(paths)
            if not museum_paths(paths):
                raise ValueError("event changes include main-site files or an empty range")
        if deployment:
            if event_name == "push" and event.get("ref") != "refs/heads/main":
                raise ValueError("deployment is not a main push")
            run = event.get("workflow_run", {})
            base = baseline_lookup(event["repository"]["full_name"],
                                   str(run.get("id", os.environ.get("GITHUB_RUN_ID", ""))),
                                   run.get("created_at", ""), os.environ.get("GH_TOKEN", ""))
            paths = changed_paths(base, head, root)
            result["changed_count"] = len(paths)
            if not museum_paths(paths):
                raise ValueError("unpublished changes outside museum since last successful Pages push")
        if not ordinary_museum_tree(head, root):
            raise ValueError("museum includes a symlink or submodule")
        result.update(museum_only=True, baseline_sha=base,
                      reason="only ordinary museum files changed" + (" since successful publication" if deployment else ""))
    except (KeyError, TypeError, AttributeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        # Do not expose authentication or request details in summaries.
        result["reason"] = str(exc) if isinstance(exc, ValueError) else type(exc).__name__ + ": comparison unavailable"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment", action="store_true")
    args = parser.parse_args()
    head = git("rev-parse", "HEAD").decode().strip()
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    result = classify(event, os.environ["GITHUB_EVENT_NAME"], head, deployment=args.deployment)
    output = {**result, "museum_only": str(result["museum_only"]).lower()}
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as handle:
            for name in ("museum_only", "baseline_sha", "changed_count"):
                handle.write(f"{name}={output[name]}\n")
    print(json.dumps(output, sort_keys=True), flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as handle:
            handle.write("### Museum change scope\n\n" + json.dumps(output, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

INTAKE_IMMUTABLE_PREFIXES = (
    "record-chain/intake/submissions/",
    "record-chain/intake/receipts/",
)

PENDING_PREFIXES = (
    "record-chain/pending/",
)

AUTO_FINALIZE_PREFIXES = (
    "record-chain/records/",
    "record-chain/indexes/",
    "record-chain/processed/",
    "record-chain/rejected/",
)

AUTO_FINALIZE_FILES = {
    "record-chain/chain-tip.json",
    "record-chain/hash-chain/main.chain.jsonl",
    "api/record-chain-head.json",
    "api/record-chain-index.json",
    "api/record-chain-index.by-type.json",
    "api/record-chain-index.latest.json",
}

OTS_PREFIXES = ("record-chain/ots/native-anchors/",)
OTS_FILES = {"api/record-chain-native-ots-latest.json"}

ARWEAVE_PREFIXES = ("record-chain/arweave-archives/",)
ARWEAVE_FILES = {"api/record-chain-arweave-index.json"}

PUBLIC_GENERATED_FILES = {
    "api/public-home-status.json",
    "index.md",
    "sitemap.xml",
}

MAINTENANCE_OVERRIDE_PREFIX = "record-chain/maintenance-overrides/"
MAINTENANCE_OVERRIDE_TOKEN = "RECORD_CHAIN_MAINTENANCE_OVERRIDE_OK"

APPROVED_GATEWAY_PREFIXES = (
    "intake: submission ",
    "intake: pending ",
    "intake: receipt ",
)

APPROVED_ACTIONS_ACTOR = "github-actions[bot]"
APPROVED_AUTO_FINALIZE_MESSAGE = "record-chain: auto-finalize accepted submissions"
APPROVED_OTS_MESSAGE = "anchor: stamp native record-chain head with OTS"
APPROVED_ARWEAVE_MESSAGE = "archive: update native record-chain Arweave archive metadata"

PROTECTED_CATEGORIES = {
    "gateway_intake",
    "pending",
    "auto_finalize",
    "ots",
    "arweave",
}


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr}\n{result.stdout}")
    return result.stdout


def changed_files(base: str, head: str) -> list[str]:
    if set(base) == {"0"}:
        output = run_git(["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", head])
    else:
        output = run_git(["diff", "--name-only", f"{base}..{head}"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def commits_in_range(base: str, head: str) -> list[str]:
    if set(base) == {"0"}:
        return [head]
    output = run_git(["rev-list", "--reverse", f"{base}..{head}"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def commit_message(ref: str) -> str:
    return run_git(["log", "-1", "--pretty=%B", ref]).strip()


def startswith_any(path: str, prefixes: Iterable[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def parse_actor_list(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def category(path: str) -> str:
    if startswith_any(path, INTAKE_IMMUTABLE_PREFIXES):
        return "gateway_intake"
    if startswith_any(path, PENDING_PREFIXES):
        return "pending"
    if startswith_any(path, AUTO_FINALIZE_PREFIXES) or path in AUTO_FINALIZE_FILES:
        return "auto_finalize"
    if startswith_any(path, OTS_PREFIXES) or path in OTS_FILES:
        return "ots"
    if startswith_any(path, ARWEAVE_PREFIXES) or path in ARWEAVE_FILES:
        return "arweave"
    if path in PUBLIC_GENERATED_FILES:
        return "public_generated"
    if path.startswith(MAINTENANCE_OVERRIDE_PREFIX):
        return "maintenance_override"
    return "unrestricted"


def has_valid_maintenance_override(files: list[str]) -> bool:
    override_files = [
        ROOT / path
        for path in files
        if path.startswith(MAINTENANCE_OVERRIDE_PREFIX) and path.endswith(".json")
    ]
    if not override_files:
        return False

    for path in override_files:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (
            data.get("schema") == "trinityaccord.record-chain-maintenance-override.v1"
            and data.get("approval_token") == MAINTENANCE_OVERRIDE_TOKEN
            and isinstance(data.get("reason"), str)
            and data["reason"].strip()
        ):
            return True
    return False


def protected_categories(files: list[str]) -> set[str]:
    return {category(path) for path in files} & PROTECTED_CATEGORIES


def actor_is_actions(actor: str | None) -> bool:
    return actor == APPROVED_ACTIONS_ACTOR


def require_actions_actor(actor: str | None, writer: str) -> tuple[bool, str]:
    if actor_is_actions(actor):
        return True, f"{writer} actor verified"
    return False, f"{writer} writes must be produced by {APPROVED_ACTIONS_ACTOR}; got actor={actor!r}"


def require_gateway_actor(actor: str | None, allowed_gateway_actors: set[str]) -> tuple[bool, str]:
    if not allowed_gateway_actors:
        return False, "gateway intake actor allow-list is not configured"
    if actor in allowed_gateway_actors:
        return True, "gateway intake actor verified"
    return False, f"gateway intake actor not allowed: actor={actor!r} allowed={sorted(allowed_gateway_actors)!r}"


def allowed_for_push(
    files: list[str],
    message: str,
    commits: list[str],
    actor: str | None,
    allowed_gateway_actors: set[str],
) -> tuple[bool, str]:
    cats = {category(path) for path in files}
    protected = protected_categories(files)

    if not protected:
        return True, "no protected runtime data changed"

    # Maintenance override is intentionally NOT accepted on direct push.
    # It must be reviewed through a PR.
    if len(commits) != 1:
        return False, (
            "protected runtime data changed across multiple commits; "
            "only single-commit approved writers are allowed"
        )

    # Gateway contents API writes one intake artifact per commit. Pending belongs
    # both to Gateway creation and Auto Finalize deletion/move, so it is modeled
    # as its own category and allowed for both specific writers.
    if cats <= {"gateway_intake", "pending"} and any(message.startswith(prefix) for prefix in APPROVED_GATEWAY_PREFIXES):
        ok, reason = require_gateway_actor(actor, allowed_gateway_actors)
        return (True, "gateway intake commit") if ok else (False, reason)

    if cats <= {"auto_finalize", "pending"} and message == APPROVED_AUTO_FINALIZE_MESSAGE:
        ok, reason = require_actions_actor(actor, "auto-finalize")
        return (True, "auto-finalize commit") if ok else (False, reason)

    if cats <= {"ots"} and message == APPROVED_OTS_MESSAGE:
        ok, reason = require_actions_actor(actor, "OTS anchor")
        return (True, "OTS anchor commit") if ok else (False, reason)

    if cats <= {"arweave", "public_generated"} and message == APPROVED_ARWEAVE_MESSAGE:
        ok, reason = require_actions_actor(actor, "Arweave archive")
        return (True, "Arweave archive commit") if ok else (False, reason)

    return False, f"unauthorized push write categories={sorted(cats)} message={message!r} actor={actor!r}"


def allowed_for_pull_request(files: list[str]) -> tuple[bool, str]:
    protected = [
        path for path in files
        if category(path) in PROTECTED_CATEGORIES
    ]
    if not protected:
        return True, "no protected record-chain runtime data changed"

    if has_valid_maintenance_override(files):
        return True, "explicit maintenance override"

    return False, "pull request modifies protected runtime data without maintenance override: " + ", ".join(protected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--mode", choices=["push", "pull-request"], required=True)
    parser.add_argument("--github-actor", default=None)
    parser.add_argument("--gateway-actors", default="")
    args = parser.parse_args()

    files = changed_files(args.base, args.head)
    print("Changed files:")
    for path in files:
        print(f"  {category(path):20s} {path}")

    if args.mode == "push":
        commits = commits_in_range(args.base, args.head)
        print(f"Commit count: {len(commits)}")
        print(f"GitHub actor: {args.github_actor!r}")
        ok, reason = allowed_for_push(
            files,
            commit_message(args.head),
            commits,
            args.github_actor,
            parse_actor_list(args.gateway_actors),
        )
    else:
        ok, reason = allowed_for_pull_request(files)

    print(f"Decision: {'PASS' if ok else 'FAIL'} — {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

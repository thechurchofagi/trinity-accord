#!/usr/bin/env python3
"""Rebuild agent-declared archive index from GitHub Issues.

Scans closed Issues containing a trinity-issue-intake code block and indexes
Gateway-created agent-declared archive records.

Primary records:
  - agent_declared_verification_archive
  - agent_declared_echo_archive

Maintainer semantic overrides from api/agent-declared-archive-overrides.json
may reclassify a verification archive as a semantic Echo archive, but overrides
must pass canonical Echo taxonomy validation.

The output path remains api/agent-declared-verification-index.json for
backward compatibility. Long-term, this should become
api/agent-declared-archive-index.json with a compatibility projection.

Usage:
    python3 scripts/build_agent_declared_verification_index_from_issues.py [--repo owner/repo] [--dry-run]

Requires: gh CLI authenticated with repo read access.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Shared receipt policy — single source of truth
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gateway_v0_v5_policy import (
    RENDER_API_ONLY_EFFECTIVE_AT,
    is_valid_gateway_receipt_block,
)

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "api" / "agent-declared-verification-index.json"

# Shared echo taxonomy — single source of truth
from protocol_echo_types import allowed_canonical_echo_types

# Load semantic overrides (e.g. correction echoes classified by maintainers)
OVERRIDES_PATH = ROOT / "api" / "agent-declared-archive-overrides.json"
overrides: dict = {}
if OVERRIDES_PATH.exists():
    with open(OVERRIDES_PATH) as _f:
        overrides = json.load(_f).get("overrides", {})

# Fields to extract from the trinity-issue-intake block
INTAKE_FIELDS = [
    "agent_name_or_model",
    "system_or_provider",
    "agent_declared_protocol_level",
    "requested_archive_kind",
    "archive_ready",
    "auto_archive_action",
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "gateway_commit",
    "render_api_only",
    "server_validated",
    "server_rendered",
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",
]

# Additional fields we want to preserve if present
EXTRA_FIELDS = [
    "record_intent",
    "evidence_requirement_mode",
    "claim_gate_mode",
    "claim_gate_status",
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "test_record",
    "reception_initiation_class",
    "reception_initiation_basis",
    "agent_independent_followup",
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "gateway_commit",
    "render_api_only",
    "server_validated",
    "server_rendered",
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",
    "authorship_claim_protocol",
    "authorship_proof_present",
    "authorship_proof_method",
    "authorship_algorithm",
    "authorship_public_key_sha256",
    "authorship_payload_sha256",
    "authorship_signature_verified",
    "claim_status",
    "echo_type",
]

# Label patterns that indicate test records
TEST_LABEL_PATTERNS = ["test-record", "test_record", "smoke-test"]

# Label patterns that disqualify a record from being indexed
INVALID_LABEL_PATTERNS = [
    "invalid:direct-issue-archive-attempt",
    "render-api-required",
    "not-counted",
    "echo:invalid",
]

# Semantic override validation constants
VALID_SEMANTIC_ARCHIVE_KINDS = {
    "agent_declared_echo_archive",
    "agent_declared_verification_archive",
}

VALID_OVERRIDE_RELATIONS = {
    "corrects",
    "supersedes",
    "clarifies",
    "references",
}

VALID_SEMANTIC_FUNCTIONS = {
    "correction",
    "clarification",
    "classification_override",
}


def validate_override(issue_number: int, override: dict) -> None:
    """Validate maintainer semantic override before applying it."""
    if not isinstance(override, dict):
        raise SystemExit(f"Invalid override for issue #{issue_number}: override must be object")

    semantic_kind = override.get("semantic_archive_kind")
    if semantic_kind not in VALID_SEMANTIC_ARCHIVE_KINDS:
        raise SystemExit(
            f"Invalid override for issue #{issue_number}: "
            f"semantic_archive_kind={semantic_kind!r}"
        )

    echo_type = override.get("echo_type")
    if semantic_kind == "agent_declared_echo_archive":
        if echo_type not in allowed_canonical_echo_types():
            raise SystemExit(
                f"Invalid override for issue #{issue_number}: "
                f"non-canonical echo_type={echo_type!r}"
            )

    for key in ["counts_toward_home_verifiability", "counts_toward_home_reception"]:
        if not isinstance(override.get(key), bool):
            raise SystemExit(
                f"Invalid override for issue #{issue_number}: {key} must be boolean"
            )

    if "related_issue" in override and not isinstance(override.get("related_issue"), int):
        raise SystemExit(
            f"Invalid override for issue #{issue_number}: related_issue must be int"
        )

    relation = override.get("relation_to_related_issue")
    if relation is not None and relation not in VALID_OVERRIDE_RELATIONS:
        raise SystemExit(
            f"Invalid override for issue #{issue_number}: "
            f"relation_to_related_issue={relation!r}"
        )

    semantic_function = override.get("semantic_function")
    if semantic_function is not None and semantic_function not in VALID_SEMANTIC_FUNCTIONS:
        raise SystemExit(
            f"Invalid override for issue #{issue_number}: "
            f"semantic_function={semantic_function!r}"
        )


def run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {result.stderr.strip()}")
    return result.stdout


def parse_int(value, default=0):
    """Safely parse an integer value, returning default on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# Shared intake parser — single source of truth
from gateway_intake import (  # noqa: E402
    BoolParseError,
    IntakeParseError,
    parse_bool,
    parse_intake_block,
)


def fetch_issues(repo: str | None, limit: int = 10000) -> list[dict]:
    """Fetch closed non-PR issues via paginated GitHub REST API."""
    if not repo:
        raise RuntimeError("repo is required")

    issues: list[dict] = []
    page = 1

    while len(issues) < limit:
        output = run_gh([
            "api",
            f"repos/{repo}/issues",
            "-f", "state=closed",
            "-f", "per_page=100",
            "-f", f"page={page}",
        ])
        batch = json.loads(output)
        if not batch:
            break

        for item in batch:
            if "pull_request" in item:
                continue

            labels = item.get("labels") or []
            issues.append({
                "number": item.get("number"),
                "title": item.get("title") or "",
                "body": item.get("body") or "",
                "closedAt": item.get("closed_at") or "",
                "createdAt": item.get("created_at") or "",
                "url": item.get("html_url") or item.get("url") or "",
                "labels": labels,
            })

            if len(issues) >= limit:
                break

        page += 1

    return issues


def is_after_effective_date(created_at: str) -> bool:
    """Check if an issue was created after the Render API only effective date."""
    if not created_at:
        return True  # Conservative: treat unknown dates as after
    try:
        from datetime import datetime, timezone
        effective = datetime.fromisoformat(RENDER_API_ONLY_EFFECTIVE_AT.replace("Z", "+00:00"))
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return created >= effective
    except Exception:
        return True


def _process_issue(issue, intake, repo, include_test, overrides, records,
                   skipped_direct, skipped_missing_oath_summary):
    """Process a single issue. May raise BoolParseError. Uses continue for skips."""
    # Filter: must be agent_declared_verification_archive or agent_declared_echo_archive
    requested_kind = intake.get("requested_archive_kind")

    allowed_index_kinds = {
        "agent_declared_verification_archive",
        "agent_declared_echo_archive",
    }

    if requested_kind not in allowed_index_kinds:
        return

    # Filter: must be archive_ready=true
    if parse_bool(intake.get("archive_ready"), field="archive_ready", issue_number=issue["number"]) is not True:
        return

    # Filter: must be correct auto_archive action for the kind
    expected_actions = {
        "agent_declared_verification_archive": "auto_archive_agent_declared_verification",
        "agent_declared_echo_archive": "auto_archive_agent_declared_echo",
    }
    expected_action = expected_actions.get(requested_kind)
    if expected_action and intake.get("auto_archive_action") != expected_action:
        return

    # Filter: skip issues with invalid/disqualifying labels
    labels = [l.get("name", "") if isinstance(l, dict) else str(l) for l in issue.get("labels", [])]
    has_invalid_label = any(
        any(pat in lbl.lower() for pat in INVALID_LABEL_PATTERNS)
        for lbl in labels
    )
    if has_invalid_label:
        print(
            f"SKIP_INVALID_LABEL issue #{issue['number']}: "
            f"has disqualifying label (one of {INVALID_LABEL_PATTERNS})",
            file=sys.stderr,
        )
        return

    # Render API only filter: after effective date, require valid gateway receipt
    created_at = issue.get("createdAt", "")
    has_gateway_receipt = is_valid_gateway_receipt_block(intake)

    if is_after_effective_date(created_at) and not has_gateway_receipt:
        skipped_direct.append(issue["number"])
        print(
            f"SKIP_DIRECT_ISSUE_ARCHIVE_ATTEMPT issue #{issue['number']}: "
            f"no gateway receipt after effective date",
            file=sys.stderr,
        )
        return

    # Determine if this is a test record
    is_test_label = any(
        any(pat in lbl.lower() for pat in TEST_LABEL_PATTERNS)
        for lbl in labels
    )
    is_test_intake = parse_bool(intake.get("test_record"), field="test_record", issue_number=issue["number"]) is True
    is_test = is_test_label or is_test_intake

    if is_test and not include_test:
        return

    # Build counts flags - default based on test status
    counts_verifiability = parse_bool(intake.get("counts_toward_home_verifiability"), field="counts_toward_home_verifiability", issue_number=issue["number"])
    counts_reception = parse_bool(intake.get("counts_toward_home_reception"), field="counts_toward_home_reception", issue_number=issue["number"])

    if counts_verifiability is None:
        counts_verifiability = not is_test
    if counts_reception is None:
        counts_reception = not is_test

    record = {
        "issue_number": issue["number"],
        "issue_url": issue.get("url", f"https://github.com/{repo}/issues/{issue['number']}"),
        "agent_name_or_model": intake.get("agent_name_or_model", "unknown"),
        "system_or_provider": intake.get("system_or_provider", "unknown"),
        "agent_declared_protocol_level": intake.get("agent_declared_protocol_level", "V4"),
        "requested_archive_kind": requested_kind,
        "archive_ready": True,
        "auto_archive_action": expected_action or intake.get("auto_archive_action", ""),
        "counts_toward_home_verifiability": counts_verifiability,
        "counts_toward_home_reception": counts_reception,
        "test_record": is_test,
        "reception_initiation_class": intake.get("reception_initiation_class") or "unknown",
        "reception_initiation_basis": intake.get("reception_initiation_basis") or "legacy_unclassified",
        "agent_independent_followup": parse_bool(intake.get("agent_independent_followup"), field="agent_independent_followup", issue_number=issue["number"]),
        "created_at": issue.get("createdAt", ""),
    }

    # Native echo archive-specific normalization
    is_native_echo_archive = requested_kind == "agent_declared_echo_archive"
    if is_native_echo_archive:
        record["semantic_archive_kind"] = "agent_declared_echo_archive"
        record["echo_type"] = intake.get("echo_type")
        record["counts_toward_home_verifiability"] = False
        if parse_bool(intake.get("counts_toward_home_reception"), field="counts_toward_home_reception", issue_number=issue["number"]) is None:
            record["counts_toward_home_reception"] = not is_test

    # Gateway receipt fields
    if has_gateway_receipt:
        record["created_by_gateway"] = True
        record["gateway_receipt_id"] = intake.get("gateway_receipt_id", "")
        record["render_api_only"] = True
        if intake.get("gateway_commit"):
            record["gateway_commit"] = intake["gateway_commit"]
        if intake.get("gateway_service"):
            record["gateway_service"] = intake["gateway_service"]
    else:
        record["legacy_pre_render_api_only"] = True

    # Oath summary fields
    oath_present = parse_bool(intake.get("verification_oath_present"), field="verification_oath_present", issue_number=issue["number"])
    is_post_effective = is_after_effective_date(created_at)

    if oath_present is True:
        count = parse_int(intake.get("agent_readback_char_count"))
        oath_sha256 = intake.get("oath_text_sha256", "")
        readback_sha256 = intake.get("agent_readback_sha256", "")
        valid_hashes = (
            bool(re.match(r"^[a-f0-9]{64}$", oath_sha256))
            and bool(re.match(r"^[a-f0-9]{64}$", readback_sha256))
        )
        if count < 160 or not valid_hashes:
            if is_post_effective:
                skipped_missing_oath_summary.append(issue["number"])
                print(
                    f"SKIP_MISSING_OATH_SUMMARY issue #{issue['number']}: "
                    f"oath present but incomplete (count={count}, valid_hashes={valid_hashes})",
                    file=sys.stderr,
                )
                return
            record["legacy_oath_summary_missing"] = True
        else:
            record["verification_oath_present"] = True
            record["oath_version"] = intake.get("oath_version", "")
            record["oath_text_sha256"] = oath_sha256
            record["agent_readback_char_count"] = count
            record["agent_readback_sha256"] = readback_sha256
    else:
        if is_post_effective:
            skipped_missing_oath_summary.append(issue["number"])
            print(
                f"SKIP_MISSING_OATH_SUMMARY issue #{issue['number']}: "
                f"no oath summary after effective date",
                file=sys.stderr,
            )
            return
        record["legacy_oath_summary_missing"] = True

    # Authorship claim fields
    record["authorship_claim_protocol"] = intake.get("authorship_claim_protocol", "agent-authorship-claim-v1")

    # Validate native echo archive canonical type
    if is_native_echo_archive:
        echo_type = record.get("echo_type")
        if echo_type not in allowed_canonical_echo_types():
            print(
                f"SKIP_NON_CANONICAL_ECHO_TYPE issue #{issue['number']}: "
                f"non-canonical echo_type={echo_type!r}",
                file=sys.stderr,
            )
            return
    record["authorship_proof_present"] = parse_bool(intake.get("authorship_proof_present"), field="authorship_proof_present", issue_number=issue["number"]) is True
    record["authorship_proof_method"] = intake.get("authorship_proof_method", "none")
    record["authorship_algorithm"] = intake.get("authorship_algorithm", "none")
    record["authorship_public_key_sha256"] = intake.get("authorship_public_key_sha256", "none")
    record["authorship_payload_sha256"] = intake.get("authorship_payload_sha256", "none")
    record["authorship_signature_verified"] = parse_bool(intake.get("authorship_signature_verified"), field="authorship_signature_verified", issue_number=issue["number"]) is True
    claim_status = intake.get("claim_status", "unclaimed")
    record["claim_status"] = claim_status
    record["authorship_claimed"] = claim_status == "claimed"

    if "authorship:claimed" in labels:
        record["claim_status"] = "claimed"
        record["authorship_claimed"] = True
    if "authorship:key-verified" in labels:
        record["authorship_key_verified"] = True

    # Apply semantic overrides
    override = overrides.get(str(issue["number"]))
    if override:
        validate_override(issue["number"], override)
        record["semantic_archive_kind"] = override["semantic_archive_kind"]
        record["echo_type"] = override.get("echo_type")
        record["counts_toward_home_verifiability"] = override["counts_toward_home_verifiability"]
        record["counts_toward_home_reception"] = override["counts_toward_home_reception"]
        if "related_issue" in override:
            record["related_issue"] = override["related_issue"]
        if "relation_to_related_issue" in override:
            record["relation_to_related_issue"] = override["relation_to_related_issue"]
        if "semantic_function" in override:
            record["semantic_function"] = override["semantic_function"]
        if "correction_does_not_amend_prior_record" in override:
            record["correction_does_not_amend_prior_record"] = override["correction_does_not_amend_prior_record"]
        record["semantic_override_reason"] = override.get("reason", "")

    # Issue #180 correction annotation
    if issue["number"] == 180:
        record["has_correction"] = True
        record["corrected_by"] = [182]
        record["correction_scope"] = "incorrect statement about prior agent-declared archive composition"

    records.append(record)


def build_index(issues: list[dict], repo: str = "", include_test: bool = False) -> dict:
    """Build the index from parsed issue data."""
    records = []
    skipped_direct = []
    skipped_missing_oath_summary = []
    skipped_invalid_intake = []

    for issue in issues:
        body = issue.get("body", "")
        try:
            intake = parse_intake_block(
                body,
                allowed_fields=set(INTAKE_FIELDS + EXTRA_FIELDS),
            )
        except IntakeParseError as e:
            skipped_invalid_intake.append({"issue_number": issue.get("number"), "reason": str(e)})
            print(f"SKIP_INVALID_INTAKE issue #{issue.get('number')}: {e}", file=sys.stderr)
            continue
        if not intake:
            continue

        try:
            _process_issue(issue, intake, repo, include_test, overrides, records,
                           skipped_direct, skipped_missing_oath_summary)
        except BoolParseError as e:
            skipped_invalid_intake.append({"issue_number": issue.get("number"), "reason": str(e)})
            print(f"SKIP_INVALID_INTAKE issue #{issue.get('number')}: {e}", file=sys.stderr)
            continue

    # Sort by issue number
    records.sort(key=lambda r: r["issue_number"])
    skipped_invalid_intake.sort(key=lambda s: s.get("issue_number", 0))

    # Compute override summary
    applied_overrides = sorted(
        int(r["issue_number"])
        for r in records
        if r.get("semantic_override_reason")
    )

    return {
        "schema": "trinityaccord.agent-declared-verification-index.v1",
        "description": (
            "Index rebuilt from Gateway-created closed Issues. "
            "It primarily contains agent-declared verification archives, but may include "
            "maintainer-classified semantic Echo archives via /api/agent-declared-archive-overrides.json. "
            "This index is rebuilt from closed GitHub Issues by CI."
        ),
        "generated_from": [
            "github_issues:closed",
            "/api/agent-issue-gateway-payload-schema.v1.json",
            "/api/agent-declared-archive-overrides.json",
            "scripts/gateway_v0_v5_policy.py",
        ],
        "rebuild_source": "github_issues",
        "rebuild_timestamp": datetime.now(timezone.utc).isoformat(),
        "render_api_only_effective_at": RENDER_API_ONLY_EFFECTIVE_AT,
        "override_count": len(applied_overrides),
        "overrides_applied": applied_overrides,
        "skipped_direct_issue_archive_attempts": skipped_direct,
        "skipped_missing_oath_summary": skipped_missing_oath_summary,
        "skipped_invalid_intake": skipped_invalid_intake,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord", help="GitHub repo (owner/repo).")
    parser.add_argument("--dry-run", action="store_true", help="Print index without writing.")
    parser.add_argument("--check", action="store_true", help="Fail if generated index is stale.")
    parser.add_argument("--include-test", action="store_true", help="Include test records.")
    parser.add_argument("--limit", type=int, default=10000, help="Max issues to fetch.")
    args = parser.parse_args()

    repo = args.repo

    print(f"Fetching closed issues from {repo}...", file=sys.stderr)
    issues = fetch_issues(repo, limit=args.limit)
    print(f"Fetched {len(issues)} issues.", file=sys.stderr)

    index = build_index(issues, repo=repo, include_test=args.include_test)
    record_count = len(index["records"])
    non_test = sum(1 for r in index["records"] if not r["test_record"])
    print(f"Found {record_count} agent-declared verification archive records ({non_test} non-test).", file=sys.stderr)

    output = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current != output:
            # Normalize rebuild_timestamp before comparison to avoid false drift
            # from the always-changing timestamp field.
            def _normalize_ts(text: str) -> str:
                import re
                return re.sub(
                    r'"rebuild_timestamp"\s*:\s*"[^"]*"',
                    '"rebuild_timestamp": "<normalized>"',
                    text,
                )

            if _normalize_ts(current) == _normalize_ts(output):
                print(
                    f"PASS: {INDEX_PATH.relative_to(ROOT)} is up to date (timestamp-only diff).",
                    file=sys.stderr,
                )
                return 0

            print(
                f"FAIL: {INDEX_PATH.relative_to(ROOT)} is stale. "
                "Run scripts/build_agent_declared_verification_index_from_issues.py and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(f"PASS: {INDEX_PATH.relative_to(ROOT)} is up to date.", file=sys.stderr)
        return 0

    if args.dry_run:
        print(output)
    else:
        INDEX_PATH.write_text(output, encoding="utf-8")
        print(f"Wrote {INDEX_PATH.relative_to(ROOT)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

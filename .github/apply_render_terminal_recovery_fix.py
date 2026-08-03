from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "render_manual_deploy.py"

text = TARGET.read_text(encoding="utf-8")

old = '''DEPLOY_SUCCESS_STATUSES = frozenset({"live"})
DEPLOY_FAILURE_STATUSES = frozenset({
    "build_failed",
    "update_failed",
    "pre_deploy_failed",
    "canceled",
    "deactivated",
})
'''
new = '''DEPLOY_SUCCESS_STATUSES = frozenset({"live"})
DEPLOY_FAILURE_STATUSES = frozenset({
    "build_failed",
    "update_failed",
    "pre_deploy_failed",
    "canceled",
    "deactivated",
})
# Render's documented lifecycle states that still represent an existing deploy
# worth reusing. Terminal failures must never block a fresh retry or be reused
# as if they could still become live.
DEPLOY_RECOVERABLE_STATUSES = frozenset({
    "created",
    "build_in_progress",
    "pre_deploy_in_progress",
    "update_in_progress",
    "live",
})
'''
if text.count(old) != 1:
    raise SystemExit("status constants anchor mismatch")
text = text.replace(old, new, 1)

old = '''        deploy_id = deploy_id_from_response(record)
        commit_id = deploy_commit_id(record)
        created_at = deploy_created_at_epoch(record)
        if (
            deploy_id
            and commit_id == expected_commit_id
            and created_at is not None
            and created_at >= threshold
        ):
            candidates.append(record)
'''
new = '''        deploy_id = deploy_id_from_response(record)
        commit_id = deploy_commit_id(record)
        created_at = deploy_created_at_epoch(record)
        status = deploy_status(record)
        if (
            deploy_id
            and commit_id == expected_commit_id
            and created_at is not None
            and created_at >= threshold
            and status in DEPLOY_RECOVERABLE_STATUSES
        ):
            candidates.append(record)
'''
if text.count(old) != 1:
    raise SystemExit("candidate filter anchor mismatch")
text = text.replace(old, new, 1)

old = '''    """Return uniquely attributable deploys for one exact commit/time window."""
'''
new = '''    """Return nonterminal/live deploys for one exact commit/time window.

    Historical terminal records such as ``deactivated`` or ``build_failed`` are
    evidence of previous attempts, not reusable deployments. They are ignored so
    an optional pre-create recovery can safely fall through to one fresh POST.
    """
'''
if text.count(old) != 1:
    raise SystemExit("candidate docstring anchor mismatch")
text = text.replace(old, new, 1)

TARGET.write_text(text, encoding="utf-8")
print("PASS: staged terminal Render recovery filtering")

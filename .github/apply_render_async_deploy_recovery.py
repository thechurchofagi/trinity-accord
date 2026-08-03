from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "render_manual_deploy.py"
TEST = ROOT / "tests" / "test_render_async_deploy_recovery.py"

text = TARGET.read_text(encoding="utf-8")

old = "import argparse\nimport json\nimport os\n"
new = "import argparse\nimport json\nimport os\nfrom datetime import datetime, timezone\n"
if text.count(old) != 1:
    raise SystemExit("import anchor mismatch")
text = text.replace(old, new, 1)

anchor = '''def deploy_status(result: Any) -> str:
    value = deploy_object(result).get("status")
    return str(value or "").strip().lower()


def wait_for_deploy(
'''
insert = '''def deploy_status(result: Any) -> str:
    value = deploy_object(result).get("status")
    return str(value or "").strip().lower()


def deploy_created_at_epoch(result: Any) -> float | None:
    """Return a Render deploy creation timestamp as UTC epoch seconds."""
    deploy = deploy_object(result)
    value = deploy.get("createdAt") or deploy.get("created_at")
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).timestamp()


def parse_utc_epoch(value: str, *, label: str) -> float:
    """Parse one strict ISO-8601 timestamp used as a recovery boundary."""
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        fail(f"{label} must be an ISO-8601 timestamp with timezone")
    if parsed.tzinfo is None:
        fail(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc).timestamp()


def list_recent_deploys(service_id: str, token: str) -> list[dict[str, Any]]:
    result = request(f"/services/{service_id}/deploys?limit=20", token)
    if not isinstance(result, list):
        fail("Render deploy list did not return a list")
    return [item for item in result if isinstance(item, dict)]


def exact_deploy_candidates(
    records: list[dict[str, Any]],
    *,
    expected_commit_id: str,
    not_before_epoch: float,
    clock_skew_seconds: float = 5.0,
) -> list[dict[str, Any]]:
    """Return uniquely attributable deploys for one exact commit/time window."""
    threshold = not_before_epoch - max(0.0, clock_skew_seconds)
    candidates: list[dict[str, Any]] = []
    for record in records:
        deploy_id = deploy_id_from_response(record)
        commit_id = deploy_commit_id(record)
        created_at = deploy_created_at_epoch(record)
        if (
            deploy_id
            and commit_id == expected_commit_id
            and created_at is not None
            and created_at >= threshold
        ):
            candidates.append(record)
    candidates.sort(key=lambda item: str(deploy_id_from_response(item) or ""))
    return candidates


def recover_unique_deploy_id(
    *,
    service_id: str,
    token: str,
    expected_commit_id: str,
    not_before_epoch: float,
    timeout_seconds: float,
    poll_seconds: float,
    require_match: bool,
) -> str | None:
    """Recover one asynchronously accepted deploy without guessing or duplication."""
    deadline = time.monotonic() + max(0.0, timeout_seconds)
    while True:
        candidates = exact_deploy_candidates(
            list_recent_deploys(service_id, token),
            expected_commit_id=expected_commit_id,
            not_before_epoch=not_before_epoch,
        )
        if len(candidates) > 1:
            ids = ",".join(
                str(deploy_id_from_response(item) or "unknown")
                for item in candidates
            )
            fail(
                "Render deploy recovery is ambiguous: multiple exact-commit "
                f"deploys matched the recovery window ({ids})"
            )
        if len(candidates) == 1:
            deploy_id = deploy_id_from_response(candidates[0])
            if not deploy_id:
                fail("Render deploy recovery matched a record without an id")
            print(
                f"RENDER_DEPLOY_ID_RECOVERED service_id={service_id} "
                f"deploy_id={deploy_id} commit_id={expected_commit_id}"
            )
            return deploy_id
        if time.monotonic() >= deadline:
            if require_match:
                fail(
                    "Render accepted the deploy request but no unique exact-commit "
                    "deploy appeared within the recovery timeout"
                )
            return None
        time.sleep(max(0.0, poll_seconds))


def wait_for_deploy(
'''
if text.count(anchor) != 1:
    raise SystemExit("deploy helper insertion anchor mismatch")
text = text.replace(anchor, insert, 1)

old_args = '''    parser.add_argument("--wait-timeout", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    args = parser.parse_args()
'''
new_args = '''    parser.add_argument("--wait-timeout", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    parser.add_argument(
        "--recover-existing-since",
        default="",
        help="ISO-8601 lower bound for reusing one exact-commit deploy before creating another",
    )
    parser.add_argument("--deploy-id-recovery-timeout", type=float, default=60.0)
    args = parser.parse_args()
'''
if text.count(old_args) != 1:
    raise SystemExit("parser anchor mismatch")
text = text.replace(old_args, new_args, 1)

old_validation = '''    if args.poll_seconds < 0:
        fail("--poll-seconds must be non-negative")
    if args.reconcile_config and not args.deploy:
'''
new_validation = '''    if args.poll_seconds < 0:
        fail("--poll-seconds must be non-negative")
    if args.deploy_id_recovery_timeout < 0:
        fail("--deploy-id-recovery-timeout must be non-negative")
    recover_existing_since = args.recover_existing_since.strip()
    recover_existing_epoch: float | None = None
    if recover_existing_since:
        if not args.deploy:
            fail("--recover-existing-since requires --deploy")
        if not commit_id:
            fail("--recover-existing-since requires --commit-id")
        recover_existing_epoch = parse_utc_epoch(
            recover_existing_since,
            label="--recover-existing-since",
        )
    if args.reconcile_config and not args.deploy:
'''
if text.count(old_validation) != 1:
    raise SystemExit("validation anchor mismatch")
text = text.replace(old_validation, new_validation, 1)

old_deploy = '''    body = {"clearCache": "do_not_clear"}
    if commit_id:
        body["commitId"] = commit_id
    result = request(f"/services/{sid}/deploys", token, method="POST", body=body)
    deploy_id = deploy_id_from_response(result)
    if not deploy_id:
        fail("Render accepted the deploy request without returning a deploy ID; deployment is unconfirmed")

    observed_commit = deploy_commit_id(result)
    if observed_commit and commit_id and observed_commit != commit_id:
        fail(
            f"Render created deploy {deploy_id} for unexpected commit "
            f"{observed_commit}; expected {commit_id}"
        )
'''
new_deploy = '''    deploy_id: str | None = None
    result: Any = {}
    if recover_existing_epoch is not None:
        deploy_id = recover_unique_deploy_id(
            service_id=str(sid),
            token=token,
            expected_commit_id=commit_id,
            not_before_epoch=recover_existing_epoch,
            timeout_seconds=min(10.0, args.deploy_id_recovery_timeout),
            poll_seconds=min(2.0, args.poll_seconds),
            require_match=False,
        )
        if deploy_id:
            result = request(f"/services/{sid}/deploys/{deploy_id}", token)
            print(
                f"RENDER_DEPLOY_REUSED service={args.service} "
                f"deploy_id={deploy_id} commit_id={commit_id}"
            )

    if not deploy_id:
        body = {"clearCache": "do_not_clear"}
        if commit_id:
            body["commitId"] = commit_id
        request_started_epoch = time.time()
        result = request(f"/services/{sid}/deploys", token, method="POST", body=body)
        deploy_id = deploy_id_from_response(result)
        if not deploy_id:
            deploy_id = recover_unique_deploy_id(
                service_id=str(sid),
                token=token,
                expected_commit_id=commit_id,
                not_before_epoch=request_started_epoch,
                timeout_seconds=args.deploy_id_recovery_timeout,
                poll_seconds=min(2.0, args.poll_seconds),
                require_match=True,
            )
            result = request(f"/services/{sid}/deploys/{deploy_id}", token)

    observed_commit = deploy_commit_id(result)
    if observed_commit and commit_id and observed_commit != commit_id:
        fail(
            f"Render created deploy {deploy_id} for unexpected commit "
            f"{observed_commit}; expected {commit_id}"
        )
'''
if text.count(old_deploy) != 1:
    raise SystemExit("deploy flow anchor mismatch")
text = text.replace(old_deploy, new_deploy, 1)

TARGET.write_text(text, encoding="utf-8")

TEST.write_text('''from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_manual_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_manual_deploy_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def deploy(deploy_id: str, commit: str, created: str, status: str = "build_in_progress"):
    return {
        "deploy": {
            "id": deploy_id,
            "commit": {"id": commit},
            "createdAt": created,
            "status": status,
        }
    }


def test_exact_deploy_candidates_bind_commit_and_time():
    module = load_module()
    expected = "a" * 40
    records = [
        deploy("dep-old", expected, "2026-08-03T14:00:00Z"),
        deploy("dep-wrong", "b" * 40, "2026-08-03T14:16:40Z"),
        deploy("dep-right", expected, "2026-08-03T14:16:40Z"),
    ]
    matches = module.exact_deploy_candidates(
        records,
        expected_commit_id=expected,
        not_before_epoch=module.parse_utc_epoch(
            "2026-08-03T14:16:36Z", label="test"
        ),
    )
    assert [module.deploy_id_from_response(item) for item in matches] == ["dep-right"]


def test_recover_unique_deploy_id_polls_until_visible(monkeypatch):
    module = load_module()
    expected = "c" * 40
    responses = [[], [deploy("dep-recovered", expected, "2026-08-03T14:16:40Z")]]
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: responses.pop(0))
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    ticks = iter([0.0, 0.0, 0.1])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    recovered = module.recover_unique_deploy_id(
        service_id="srv-test",
        token="token",
        expected_commit_id=expected,
        not_before_epoch=module.parse_utc_epoch("2026-08-03T14:16:36Z", label="test"),
        timeout_seconds=1.0,
        poll_seconds=0.0,
        require_match=True,
    )
    assert recovered == "dep-recovered"


def test_recovery_fails_closed_on_multiple_matches(monkeypatch):
    module = load_module()
    expected = "d" * 40
    records = [
        deploy("dep-one", expected, "2026-08-03T14:16:40Z"),
        deploy("dep-two", expected, "2026-08-03T14:16:41Z"),
    ]
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: records)
    monkeypatch.setattr(module.time, "monotonic", lambda: 0.0)
    with pytest.raises(SystemExit):
        module.recover_unique_deploy_id(
            service_id="srv-test",
            token="token",
            expected_commit_id=expected,
            not_before_epoch=module.parse_utc_epoch("2026-08-03T14:16:36Z", label="test"),
            timeout_seconds=1.0,
            poll_seconds=0.0,
            require_match=True,
        )


def test_recovery_returns_none_when_optional_window_has_no_match(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: [])
    ticks = iter([0.0, 1.0])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    assert module.recover_unique_deploy_id(
        service_id="srv-test",
        token="token",
        expected_commit_id="e" * 40,
        not_before_epoch=0.0,
        timeout_seconds=0.5,
        poll_seconds=0.0,
        require_match=False,
    ) is None


def test_wait_for_deploy_rejects_wrong_commit(monkeypatch):
    module = load_module()
    monkeypatch.setattr(
        module,
        "request",
        lambda *_args, **_kwargs: deploy(
            "dep-wrong", "f" * 40, "2026-08-03T14:16:40Z", status="live"
        ),
    )
    with pytest.raises(SystemExit):
        module.wait_for_deploy(
            service_id="srv-test",
            deploy_id="dep-wrong",
            token="token",
            expected_commit_id="a" * 40,
            timeout_seconds=1,
            poll_seconds=0,
        )


def test_parse_utc_epoch_requires_timezone():
    module = load_module()
    with pytest.raises(SystemExit):
        module.parse_utc_epoch("2026-08-03T14:16:36", label="test")
''', encoding="utf-8")

print("PASS: staged Render asynchronous deploy-ID recovery and regression tests")

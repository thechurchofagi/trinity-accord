#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    conftest = ROOT / "apps/record_chain_intake_gateway/tests/conftest.py"
    old_fixture = '''@pytest.fixture
def mock_github():
    """Mock the GitHub adapter so tests don't make real API calls."""
    put_mock = AsyncMock(return_value={"commit": {"sha": "abc123"}})
    sha_mock = AsyncMock(return_value=None)
    text_mock = AsyncMock(return_value=None)
    dispatch_mock = AsyncMock(return_value=None)
    delete_mock = AsyncMock(return_value={})

    env = {
        "TRINITY_REPO_FULL_NAME": "thechurchofagi/trinity-accord",
        "TRINITY_TARGET_BRANCH": "main",
        "TRINITY_GITHUB_TOKEN": "test-token",
    }

    with patch.dict(os.environ, env), \\
         patch("app.put_file", put_mock), \\
         patch("app.get_file_sha", sha_mock), \\
         patch("app.get_file_text", text_mock), \\
         patch("app.dispatch_workflow", dispatch_mock), \\
         patch("app.delete_file", delete_mock):
        yield {
            "put_file": put_mock,
            "get_file_sha": sha_mock,
            "get_file_text": text_mock,
            "dispatch_workflow": dispatch_mock,
            "delete_file": delete_mock,
        }
'''
    new_fixture = '''@pytest.fixture
def mock_github():
    """Mock atomic GitHub intake persistence and read/dispatch adapters."""
    atomic_mock = AsyncMock(return_value={"commit": {"sha": "abc123"}})
    sha_mock = AsyncMock(return_value=None)
    text_mock = AsyncMock(return_value=None)
    dispatch_mock = AsyncMock(return_value=None)

    env = {
        "TRINITY_REPO_FULL_NAME": "thechurchofagi/trinity-accord",
        "TRINITY_TARGET_BRANCH": "main",
        "TRINITY_GITHUB_TOKEN": "test-token",
    }

    with patch.dict(os.environ, env), \\
         patch("app.create_files_atomic", atomic_mock), \\
         patch("app.get_file_sha", sha_mock), \\
         patch("app.get_file_text", text_mock), \\
         patch("app.dispatch_workflow", dispatch_mock):
        yield {
            "create_files_atomic": atomic_mock,
            "get_file_sha": sha_mock,
            "get_file_text": text_mock,
            "dispatch_workflow": dispatch_mock,
        }
'''
    replace_once(conftest, old_fixture, new_fixture, "shared GitHub fixture")

    atomic = ROOT / "apps/record_chain_intake_gateway/gateway/github_atomic.py"
    old_env = '''def _repo() -> str:
    value = os.getenv("TRINITY_GITHUB_REPO", "thechurchofagi/trinity-accord").strip()
    if not value or "/" not in value:
        raise RuntimeError("TRINITY_GITHUB_REPO must be in owner/repo form")
    return value


def _branch() -> str:
    value = os.getenv("TRINITY_GITHUB_TARGET_BRANCH", "main").strip()
    if not value:
        raise RuntimeError("TRINITY_GITHUB_TARGET_BRANCH must not be empty")
    return value
'''
    new_env = '''def _repo() -> str:
    value = os.getenv("TRINITY_REPO_FULL_NAME", "").strip()
    if not value or "/" not in value:
        raise RuntimeError("TRINITY_REPO_FULL_NAME must be in owner/repo form")
    return value


def _branch() -> str:
    value = os.getenv("TRINITY_TARGET_BRANCH", "main").strip()
    if not value:
        raise RuntimeError("TRINITY_TARGET_BRANCH must not be empty")
    return value
'''
    replace_once(atomic, old_env, new_env, "atomic adapter environment contract")

    app = ROOT / "apps/record_chain_intake_gateway/app.py"
    old_comment = '''    # --- persist to GitHub ---
    # Safe order:
    #   1. submission
    #   2. receipt
    #   3. idempotency index
    #   4. pending LAST
    #
    # The pending file is the append-eligibility marker. It must not be visible
    # until durable intake state exists and is globally idempotent.
    commit_sha: str | None = None
    created_files_for_rollback: list[tuple[str, str]] = []
    append_status = "pending"
'''
    new_comment = '''    # --- atomically persist the complete intake transaction ---
    # The pending append-eligibility marker and every durable dependency become
    # visible in the same branch state; no partial transaction is published.
    commit_sha: str | None = None
    append_status = "pending"
'''
    replace_once(app, old_comment, new_comment, "Gateway persistence comment")

    for path in (conftest, atomic, app):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    print("ATOMIC_GATEWAY_TEST_FIXTURE_MIGRATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

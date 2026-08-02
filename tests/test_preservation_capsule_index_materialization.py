from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_preservation_capsule as builder  # noqa: E402
import preservation_capsule as package  # noqa: E402


_HELPERS_SPEC = importlib.util.spec_from_file_location(
    "preservation_capsule_test_helpers",
    ROOT / "tests" / "test_preservation_capsule.py",
)
assert _HELPERS_SPEC is not None and _HELPERS_SPEC.loader is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
_HELPERS_SPEC.loader.exec_module(_HELPERS)
make_repository = _HELPERS.make_repository
write = _HELPERS.write


def test_index_materialization_preserves_force_tracked_ignored_file(tmp_path: Path) -> None:
    repo, _ = make_repository(tmp_path)
    write(repo / ".gitignore", b"tracked-ignored.bin\n")
    write(repo / "tracked-ignored.bin", b"tracked despite ignore rules\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=repo, check=True)
    subprocess.run(
        ["git", "add", "-f", "tracked-ignored.bin"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "track an ignored file"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    frozen_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    expected_tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    capsule = tmp_path / "capsule"
    builder.build(repo, capsule, frozen_commit)
    verified = package.verify_local_package(capsule)
    assert verified["git_tree_oid"] == expected_tree

    tracked = json.loads((capsule / "tracked-files.json").read_text(encoding="utf-8"))
    entry = next(
        item for item in tracked["files"] if item["path"] == "tracked-ignored.bin"
    )
    assert entry["mode"] == "100644"
    assert entry["bytes"] == len(b"tracked despite ignore rules\n")

    restored = tmp_path / "restored"
    subprocess.run(
        [
            sys.executable,
            str(capsule / "restore-trinity-accord.py"),
            "--deposit-dir",
            str(capsule),
            "--output-dir",
            str(restored),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    restored_repo = restored / "repository"
    restored_tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=restored_repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert restored_tree == expected_tree
    assert (restored_repo / "tracked-ignored.bin").read_bytes() == (
        b"tracked despite ignore rules\n"
    )

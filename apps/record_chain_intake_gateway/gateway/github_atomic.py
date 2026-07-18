"""Atomic multi-file GitHub persistence for Record-Chain intake.

The GitHub Contents API creates one commit per file.  A Record-Chain intake
transaction spans four files and must become visible as one repository state,
so this module uses the Git Data API to create blobs, one tree, one commit, and
one fast-forward branch-ref update.
"""
from __future__ import annotations

import base64
import logging
import os
from typing import Any
from urllib.parse import quote

import httpx

logger = logging.getLogger("trinity.gateway.github_atomic")

_GITHUB_API = "https://api.github.com"


class AtomicCreateConflict(RuntimeError):
    """Raised when an atomic create would overwrite an existing path."""


def _repo() -> str:
    value = os.getenv("TRINITY_GITHUB_REPO", "thechurchofagi/trinity-accord").strip()
    if not value or "/" not in value:
        raise RuntimeError("TRINITY_GITHUB_REPO must be in owner/repo form")
    return value


def _branch() -> str:
    value = os.getenv("TRINITY_GITHUB_TARGET_BRANCH", "main").strip()
    if not value:
        raise RuntimeError("TRINITY_GITHUB_TARGET_BRANCH must not be empty")
    return value


def _headers() -> dict[str, str]:
    token = os.getenv("TRINITY_GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TRINITY_GITHUB_TOKEN is required for GitHub writes")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _contents_url(path: str) -> str:
    encoded = quote(path, safe="/")
    return f"{_GITHUB_API}/repos/{_repo()}/contents/{encoded}"


async def _get_file_text_at_ref(
    client: httpx.AsyncClient,
    path: str,
    ref: str,
) -> str | None:
    """Read UTF-8 repository content at an immutable ref."""
    response = await client.get(
        _contents_url(path),
        headers=_headers(),
        params={"ref": ref},
    )
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error {response.status_code} fetching {path} at {ref}"
        )

    data: dict[str, Any] = response.json()
    if data.get("encoding", "base64") != "base64":
        return str(data.get("content", ""))
    try:
        return base64.b64decode(data.get("content", "")).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(
            f"Failed to decode file content for {path} at {ref}: {exc}"
        ) from exc


async def _atomic_files_state(
    client: httpx.AsyncClient,
    files: dict[str, str],
    ref: str,
) -> tuple[bool, bool]:
    """Return ``(all_absent, all_exact)`` for requested paths at ``ref``."""
    states: list[str] = []
    for path, intended in files.items():
        remote = await _get_file_text_at_ref(client, path, ref)
        if remote is None:
            states.append("absent")
        elif remote == intended:
            states.append("exact")
        else:
            states.append("different")
    return (
        all(state == "absent" for state in states),
        all(state == "exact" for state in states),
    )


async def create_files_atomic(
    files: dict[str, str],
    message: str,
    *,
    max_attempts: int = 4,
) -> dict[str, Any]:
    """Create several UTF-8 files in one fast-forward Git commit.

    Existing paths are never overwritten. Branch races are retried. If the
    ref-update response is ambiguous, exact readback determines whether the
    transaction committed before an error was observed.
    """
    if not files:
        raise ValueError("create_files_atomic requires at least one file")
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")

    branch = _branch()
    ref_path = f"heads/{branch}"
    ref_url = f"{_GITHUB_API}/repos/{_repo()}/git/ref/{ref_path}"
    update_ref_url = f"{_GITHUB_API}/repos/{_repo()}/git/refs/{ref_path}"

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(1, max_attempts + 1):
            ref_response = await client.get(ref_url, headers=_headers())
            if ref_response.status_code != 200:
                raise RuntimeError(
                    f"GitHub API error {ref_response.status_code} reading branch {branch}"
                )
            head_sha = ref_response.json().get("object", {}).get("sha")
            if not head_sha:
                raise RuntimeError(f"GitHub branch {branch} has no commit SHA")

            all_absent, all_exact = await _atomic_files_state(
                client,
                files,
                head_sha,
            )
            if all_exact:
                logger.warning(
                    "Reconciled an already-materialized atomic write at %s",
                    head_sha,
                )
                return {
                    "commit": {"sha": head_sha},
                    "atomic": True,
                    "reconciled_existing": True,
                }
            if not all_absent:
                raise AtomicCreateConflict(
                    "Atomic intake paths are partially present or contain different bytes"
                )

            commit_response = await client.get(
                f"{_GITHUB_API}/repos/{_repo()}/git/commits/{head_sha}",
                headers=_headers(),
            )
            if commit_response.status_code != 200:
                raise RuntimeError(
                    f"GitHub API error {commit_response.status_code} reading {head_sha}"
                )
            base_tree_sha = commit_response.json().get("tree", {}).get("sha")
            if not base_tree_sha:
                raise RuntimeError(f"GitHub commit {head_sha} has no tree SHA")

            tree_entries: list[dict[str, str]] = []
            for path, content in files.items():
                blob_response = await client.post(
                    f"{_GITHUB_API}/repos/{_repo()}/git/blobs",
                    headers=_headers(),
                    json={"content": content, "encoding": "utf-8"},
                )
                if blob_response.status_code != 201:
                    raise RuntimeError(
                        f"GitHub API error {blob_response.status_code} creating blob for {path}"
                    )
                blob_sha = blob_response.json().get("sha")
                if not blob_sha:
                    raise RuntimeError(f"GitHub returned no blob SHA for {path}")
                tree_entries.append(
                    {
                        "path": path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_sha,
                    }
                )

            tree_response = await client.post(
                f"{_GITHUB_API}/repos/{_repo()}/git/trees",
                headers=_headers(),
                json={"base_tree": base_tree_sha, "tree": tree_entries},
            )
            if tree_response.status_code != 201:
                raise RuntimeError(
                    f"GitHub API error {tree_response.status_code} creating atomic tree"
                )
            tree_sha = tree_response.json().get("sha")
            if not tree_sha:
                raise RuntimeError("GitHub returned no atomic tree SHA")

            new_commit_response = await client.post(
                f"{_GITHUB_API}/repos/{_repo()}/git/commits",
                headers=_headers(),
                json={
                    "message": message,
                    "tree": tree_sha,
                    "parents": [head_sha],
                },
            )
            if new_commit_response.status_code != 201:
                raise RuntimeError(
                    f"GitHub API error {new_commit_response.status_code} creating atomic commit"
                )
            new_commit_sha = new_commit_response.json().get("sha")
            if not new_commit_sha:
                raise RuntimeError("GitHub returned no atomic commit SHA")

            try:
                update_response = await client.patch(
                    update_ref_url,
                    headers=_headers(),
                    json={"sha": new_commit_sha, "force": False},
                )
            except Exception:
                _, exact_after_error = await _atomic_files_state(
                    client,
                    files,
                    branch,
                )
                if exact_after_error:
                    logger.warning(
                        "Reconciled ambiguous atomic ref update for %s",
                        new_commit_sha,
                    )
                    return {
                        "commit": {"sha": new_commit_sha},
                        "atomic": True,
                        "reconciled_after_error": True,
                    }
                raise

            if update_response.status_code == 200:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_existing": False,
                }

            if update_response.status_code in (409, 422) and attempt < max_attempts:
                logger.info(
                    "Branch moved during atomic write; retrying %d/%d",
                    attempt + 1,
                    max_attempts,
                )
                continue

            _, exact_after_response = await _atomic_files_state(
                client,
                files,
                branch,
            )
            if exact_after_response:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_after_error": True,
                }
            raise RuntimeError(
                f"GitHub API error {update_response.status_code} advancing branch"
            )

    raise RuntimeError("Atomic GitHub write exhausted branch-race retries")

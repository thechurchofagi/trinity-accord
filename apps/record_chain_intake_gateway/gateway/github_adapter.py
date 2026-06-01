# gateway/github_adapter.py
"""GitHub Contents API adapter for reading and writing record-chain files."""

from __future__ import annotations

import base64
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"


def _token() -> str:
    """Read the GitHub token from the environment. Raises if missing."""
    token = os.environ.get("TRINITY_GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("TRINITY_GITHUB_TOKEN environment variable is not set")
    return token


def _repo() -> str:
    """Return the fully-qualified repo name (e.g. ``org/repo``)."""
    repo = os.environ.get("TRINITY_REPO_FULL_NAME", "")
    if not repo:
        raise RuntimeError("TRINITY_REPO_FULL_NAME environment variable is not set")
    return repo


def _branch() -> str:
    """Return the target branch name."""
    return os.environ.get("TRINITY_TARGET_BRANCH", "main")


def _headers() -> dict[str, str]:
    """Build request headers (token is NOT logged)."""
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def get_file_sha(path: str) -> str | None:
    """Return the current SHA blob of *path* in the repo, or ``None`` if absent."""
    url = f"{_GITHUB_API}/repos/{_repo()}/contents/{path}"
    params = {"ref": _branch()}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=_headers(), params=params)
    if resp.status_code == 200:
        data: dict[str, Any] = resp.json()
        return data.get("sha")
    if resp.status_code == 404:
        return None
    logger.error("GitHub GET %s returned %d: %s", path, resp.status_code, resp.text[:500])
    raise RuntimeError(f"GitHub API error {resp.status_code} fetching {path}")


async def get_file_text(path: str) -> str | None:
    """Return the text content of *path* in the repo (base64-decoded), or ``None`` if absent.

    Uses the GitHub Contents API. Returns the decoded UTF-8 text of the file.
    """
    url = f"{_GITHUB_API}/repos/{_repo()}/contents/{path}"
    params = {"ref": _branch()}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=_headers(), params=params)
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        logger.error("GitHub GET %s returned %d: %s", path, resp.status_code, resp.text[:500])
        raise RuntimeError(f"GitHub API error {resp.status_code} fetching {path}")

    data: dict[str, Any] = resp.json()
    content_b64 = data.get("content", "")
    encoding = data.get("encoding", "base64")
    if encoding == "base64":
        try:
            return base64.b64decode(content_b64).decode("utf-8")
        except Exception as exc:
            logger.error("Failed to decode base64 content for %s: %s", path, exc)
            raise RuntimeError(f"Failed to decode file content for {path}: {exc}")
    # Fallback: treat as raw text
    return content_b64


async def put_file(
    path: str,
    content: str,
    message: str,
    sha: str | None = None,
) -> dict[str, Any]:
    """Create or update a file in the repo via the Contents API.

    Parameters
    ----------
    path:
        Repository-relative file path.
    content:
        UTF-8 text content (will be base-64 encoded).
    message:
        Commit message.
    sha:
        Blob SHA of the existing file (required for updates).

    Returns
    -------
    dict with at least ``commit.sha`` and ``content.sha``.
    """
    url = f"{_GITHUB_API}/repos/{_repo()}/contents/{path}"
    body: dict[str, Any] = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": _branch(),
    }
    if sha:
        body["sha"] = sha

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(url, headers=_headers(), json=body)

    if resp.status_code not in (200, 201):
        logger.error("GitHub PUT %s returned %d: %s", path, resp.status_code, resp.text[:500])
        raise RuntimeError(f"GitHub API error {resp.status_code} writing {path}")

    return resp.json()


async def dispatch_workflow(
    workflow_file: str,
    ref: str | None = None,
    inputs: dict[str, Any] | None = None,
) -> None:
    """Trigger a GitHub Actions workflow dispatch event.

    Parameters
    ----------
    workflow_file:
        Workflow filename (e.g. ``build.yml``).
    ref:
        Git ref to run against (defaults to target branch).
    inputs:
        Optional workflow inputs.
    """
    if ref is None:
        ref = _branch()
    url = f"{_GITHUB_API}/repos/{_repo()}/actions/workflows/{workflow_file}/dispatches"
    body: dict[str, Any] = {"ref": ref}
    if inputs:
        body["inputs"] = inputs

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=_headers(), json=body)

    if resp.status_code not in (204, 200):
        logger.error(
            "GitHub dispatch %s returned %d: %s",
            workflow_file, resp.status_code, resp.text[:500],
        )
        raise RuntimeError(f"GitHub API error {resp.status_code} dispatching {workflow_file}")

    logger.info("Dispatched workflow %s on ref %s", workflow_file, ref)

"""Protected ASGI entrypoint for the public Record-Chain Intake Gateway.

This wrapper keeps the core Gateway validation and persistence logic unchanged,
while enforcing resource boundaries before expensive validation or durable writes:

- public submit acceptances are separated by a deterministic, unpredictable
  60–120 minute interval derived from the latest immutable intake commit;
- the cooldown is checked once at the entrance and again under a process lock
  immediately before the core submit handler is allowed to run;
- request, record-draft, text-field, list, and nesting limits are enforced for
  both preflight and submit;
- repeated requests during the protected interval receive progressively clearer
  guidance without writing rejected traffic into Git or Arweave.

The latest accepted intake commit on ``main`` is the durable cooldown state, so
Gateway restarts do not reset the acceptance interval. The current Render
runtime uses one Uvicorn process; the second gate serializes public submit work
inside that process. A future multi-instance deployment must add a shared lock.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

import httpx

from apps.record_chain_intake_gateway.app import app as core_app

logger = logging.getLogger("trinity.gateway.protection")

_MAX_BODY_BYTES = int(os.environ.get("TRINITY_MAX_SUBMISSION_BYTES", "98304"))
_MAX_DRAFT_BYTES = int(os.environ.get("TRINITY_RECORD_DRAFT_MAX_BYTES", "49152"))
_MAX_TEXT_FIELD_CHARS = int(os.environ.get("TRINITY_MAX_TEXT_FIELD_CHARS", "4000"))
_MAX_URL_CHARS = int(os.environ.get("TRINITY_MAX_URL_CHARS", "2048"))
_MAX_JSON_DEPTH = int(os.environ.get("TRINITY_MAX_JSON_DEPTH", "12"))
_MAX_ARRAY_ITEMS = int(os.environ.get("TRINITY_MAX_ARRAY_ITEMS", "32"))
_MAX_REFERENCE_ITEMS = int(os.environ.get("TRINITY_MAX_REFERENCE_ITEMS", "16"))

_TEXT_TOTAL_LIMITS: dict[str, int] = {
    "echo": 8_000,
    "verification": 12_000,
    "guardian_application": 8_000,
    "guardian_retirement": 4_000,
    "propagation": 8_000,
    "correction": 6_000,
    "classification_update": 6_000,
    "context_insufficient_notice": 4_000,
}
_DEFAULT_TOTAL_TEXT_LIMIT = 8_000

_COOLDOWN_MIN_SECONDS = 3_600
_COOLDOWN_SPAN_SECONDS = 3_600  # inclusive range is 3600..7200
_GITHUB_API = "https://api.github.com"
_INTAKE_COMMIT_PREFIX = "intake: materialize "
_COOLDOWN_CACHE_SECONDS = 3.0
_BLOCKED_ATTEMPT_WINDOW_SECONDS = 7_200

_REFERENCE_LIKE_KEYS = {
    "references",
    "evidence",
    "citations",
    "links",
    "sources",
    "supporting_references",
}
_URL_KEY_PATTERN = re.compile(r"(?:^|_)(?:url|uri|link)(?:$|_)", re.IGNORECASE)
_BASE64_KEY_PATTERN = re.compile(r"(?:^|_)(?:base64|binary|attachment_data)(?:$|_)", re.IGNORECASE)
_BASE64_VALUE_PATTERN = re.compile(r"^[A-Za-z0-9+/=_-]+$")

ASGIReceive = Callable[[], Awaitable[dict[str, Any]]]
ASGISend = Callable[[dict[str, Any]], Awaitable[None]]


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _record_type(body: dict[str, Any]) -> str:
    draft = body.get("record_draft") or body.get("draft") or {}
    candidates = [body.get("record_type")]
    if isinstance(draft, dict):
        candidates.append(draft.get("record_type"))
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip().lower()
    return "unknown"


def _draft(body: dict[str, Any]) -> dict[str, Any] | None:
    value = body.get("record_draft")
    if value is None:
        value = body.get("draft")
    return value if isinstance(value, dict) else None


def _diagnostic(
    code: str,
    field: str | None,
    message: str,
    suggested_fix: str,
    *,
    retry_allowed: bool = True,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "error",
        "field": field,
        "message": message,
        "meaning": (
            "Accepted Record-Chain entries are stored permanently and may be "
            "included in paid Arweave archival. The limit protects finite "
            "repository, verification, and archival resources."
        ),
        "suggested_fix": suggested_fix,
        "help_url": "https://www.trinityaccord.org/docs/record-chain-builder-help/#resource-boundaries",
        "retry_allowed": retry_allowed,
    }


def validate_resource_limits(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Return bounded resource diagnostics for one parsed submission."""
    draft = _draft(body)
    if draft is None:
        return []  # Let the core validator report the structural error.

    diagnostics: list[dict[str, Any]] = []
    try:
        draft_bytes = len(_canonical_bytes(draft))
    except (TypeError, ValueError):
        return []  # The core strict parser/validator owns non-JSON values.

    if draft_bytes > _MAX_DRAFT_BYTES:
        diagnostics.append(
            _diagnostic(
                "RECORD_DRAFT_TOO_LARGE",
                "record_draft",
                f"The persistent record draft is {draft_bytes} bytes; the limit is {_MAX_DRAFT_BYTES} bytes.",
                "Shorten the record. Store extensive evidence externally and submit only a concise description, durable URL, and SHA-256 hash.",
            )
        )

    stats = {"text_chars": 0}

    def walk(value: Any, path: str, depth: int, key: str | None = None) -> None:
        if len(diagnostics) >= 20:
            return
        if depth > _MAX_JSON_DEPTH:
            diagnostics.append(
                _diagnostic(
                    "RECORD_JSON_TOO_DEEP",
                    path or "record_draft",
                    f"JSON nesting exceeds the maximum depth of {_MAX_JSON_DEPTH}.",
                    "Flatten the record structure and keep supporting material external.",
                )
            )
            return

        if isinstance(value, dict):
            for child_key, child_value in value.items():
                child_path = f"{path}.{child_key}" if path else str(child_key)
                walk(child_value, child_path, depth + 1, str(child_key))
            return

        if isinstance(value, list):
            normalized_key = (key or "").lower()
            limit = (
                _MAX_REFERENCE_ITEMS
                if normalized_key in _REFERENCE_LIKE_KEYS
                or any(token in normalized_key for token in ("reference", "evidence", "citation"))
                else _MAX_ARRAY_ITEMS
            )
            if len(value) > limit:
                diagnostics.append(
                    _diagnostic(
                        "RECORD_ARRAY_TOO_LONG",
                        path,
                        f"This list contains {len(value)} items; the limit is {limit}.",
                        "Keep only the most relevant items. Put an extended index in an external durable document and bind it by URL and SHA-256.",
                    )
                )
            for index, item in enumerate(value[: _MAX_ARRAY_ITEMS + 1]):
                walk(item, f"{path}[{index}]", depth + 1, key)
            return

        if not isinstance(value, str):
            return

        stats["text_chars"] += len(value)
        normalized_key = (key or "").lower()
        field_limit = _MAX_URL_CHARS if _URL_KEY_PATTERN.search(normalized_key) else _MAX_TEXT_FIELD_CHARS
        if len(value) > field_limit:
            diagnostics.append(
                _diagnostic(
                    "RECORD_TEXT_FIELD_TOO_LONG",
                    path,
                    f"This text field contains {len(value)} characters; the limit is {field_limit}.",
                    "Shorten this field. Do not embed a full report; provide a concise statement and link to externally stored evidence with its SHA-256.",
                )
            )

        stripped = value.lstrip()
        if stripped.lower().startswith("data:"):
            diagnostics.append(
                _diagnostic(
                    "INLINE_DATA_URL_FORBIDDEN",
                    path,
                    "Inline data URLs are not accepted in permanent Record-Chain submissions.",
                    "Store the artifact externally and submit only its durable URL, media type, byte length, and SHA-256.",
                )
            )
        elif _BASE64_KEY_PATTERN.search(normalized_key):
            diagnostics.append(
                _diagnostic(
                    "INLINE_BINARY_CONTENT_FORBIDDEN",
                    path,
                    "Inline Base64 or binary attachment fields are not accepted.",
                    "Store the artifact externally and submit only a concise reference and SHA-256.",
                )
            )
        elif len(value) > 1_024 and _BASE64_VALUE_PATTERN.fullmatch(value) is not None:
            diagnostics.append(
                _diagnostic(
                    "INLINE_BINARY_CONTENT_FORBIDDEN",
                    path,
                    "A long Base64-like value was detected in the record draft.",
                    "Do not embed files or encoded binary data. Use an external durable location and bind the artifact by SHA-256.",
                )
            )

    walk(draft, "record_draft", 1)

    record_type = _record_type(body)
    total_limit = _TEXT_TOTAL_LIMITS.get(record_type, _DEFAULT_TOTAL_TEXT_LIMIT)
    if stats["text_chars"] > total_limit:
        diagnostics.append(
            _diagnostic(
                "RECORD_TOTAL_TEXT_TOO_LONG",
                "record_draft",
                f"The record contains {stats['text_chars']} total string characters; the {record_type} limit is {total_limit}.",
                "Condense the record to its essential claim, reasoning, limitations, and references. Move extended material outside the Record-Chain and bind it by URL and SHA-256.",
            )
        )

    return diagnostics


def cooldown_seconds_for_commit(commit_sha: str) -> int:
    """Derive an unpredictable 60–120 minute interval from an immutable SHA."""
    digest = hashlib.sha256(commit_sha.encode("ascii", errors="ignore")).digest()
    offset = int.from_bytes(digest[:4], "big") % (_COOLDOWN_SPAN_SECONDS + 1)
    return _COOLDOWN_MIN_SECONDS + offset


def _parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class IntakeProtectionMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app
        self._submit_lock = asyncio.Lock()
        self._blocked_attempts: dict[str, deque[float]] = defaultdict(deque)
        self._cache: dict[str, Any] = {"expires_at": 0.0, "commit": None}

    @staticmethod
    def _headers(scope: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for raw_key, raw_value in scope.get("headers", []):
            try:
                result[raw_key.decode("latin-1").lower()] = raw_value.decode("latin-1")
            except Exception:
                continue
        return result

    @staticmethod
    def _client_key(scope: dict[str, Any], headers: dict[str, str]) -> str:
        raw = headers.get("cf-connecting-ip")
        if not raw:
            raw = headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
        if not raw:
            client = scope.get("client")
            raw = str(client[0]) if isinstance(client, (tuple, list)) and client else "unknown"
        return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()

    @staticmethod
    def _internal_header_valid(headers: dict[str, str]) -> bool:
        configured = os.environ.get("TRINITY_INTERNAL_INTAKE_TOKEN", "").strip()
        supplied = headers.get("x-trinity-internal-intake", "").strip()
        return bool(configured and supplied and hmac.compare_digest(configured, supplied))

    async def _read_body(self, receive: ASGIReceive) -> tuple[bytes, bool]:
        body = bytearray()
        while True:
            message = await receive()
            if message.get("type") == "http.disconnect":
                return bytes(body), False
            if message.get("type") != "http.request":
                continue
            body.extend(message.get("body", b""))
            if len(body) > _MAX_BODY_BYTES:
                return bytes(body), True
            if not message.get("more_body", False):
                return bytes(body), False

    @staticmethod
    def _replay_receive(body: bytes) -> ASGIReceive:
        sent = False

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        return receive

    async def _send_json(
        self,
        send: ASGISend,
        status: int,
        payload: dict[str, Any],
        *,
        retry_after: bool = False,
    ) -> None:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        headers = [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(raw)).encode("ascii")),
            (b"cache-control", b"no-store"),
        ]
        if retry_after:
            # A deliberately coarse value; the exact randomized reopening time
            # is not disclosed to clients.
            headers.append((b"retry-after", b"3600"))
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": raw, "more_body": False})

    def _resource_payload(
        self,
        diagnostics: list[dict[str, Any]],
        *,
        preflight: bool,
    ) -> dict[str, Any]:
        return {
            "accepted": False,
            "submitted": False,
            "preflight": preflight,
            "diagnostic_code": diagnostics[0]["code"] if diagnostics else "RESOURCE_LIMIT_EXCEEDED",
            "diagnostics": diagnostics,
            "resource_boundary": {
                "request_max_bytes": _MAX_BODY_BYTES,
                "record_draft_max_bytes": _MAX_DRAFT_BYTES,
                "text_field_max_characters": _MAX_TEXT_FIELD_CHARS,
                "acceptance_interval_minutes": {"minimum": 60, "maximum": 120, "randomized": True},
                "why_limits_exist": (
                    "Accepted records are permanent and may add paid Arweave archival cost. "
                    "Length and frequency limits preserve the project's finite resources."
                ),
            },
            "project_purpose": (
                "The Trinity Accord preserves a verifiable civilizational record for long-term continuity. "
                "Please do not use repeated, oversized, or automated submissions to exhaust its resources."
            ),
        }

    async def _fetch_commit_page(
        self,
        client: httpx.AsyncClient,
        *,
        page: int,
        path: str | None = None,
    ) -> list[dict[str, Any]]:
        repo = os.environ.get("TRINITY_REPO_FULL_NAME", "thechurchofagi/trinity-accord").strip()
        branch = os.environ.get("TRINITY_TARGET_BRANCH", "main").strip() or "main"
        token = os.environ.get("TRINITY_GITHUB_TOKEN", "").strip()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "trinity-intake-cooldown/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params: dict[str, Any] = {"sha": branch, "per_page": 100, "page": page}
        if path:
            params["path"] = path
        response = await client.get(
            f"{_GITHUB_API}/repos/{repo}/commits",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise RuntimeError(f"GitHub cooldown lookup failed with HTTP {response.status_code}")
        data = response.json()
        if not isinstance(data, list):
            raise RuntimeError("GitHub cooldown lookup returned a non-list response")
        return [item for item in data if isinstance(item, dict)]

    @staticmethod
    def _materialize_commit(item: dict[str, Any]) -> dict[str, Any] | None:
        commit = item.get("commit")
        if not isinstance(commit, dict):
            return None
        message = str(commit.get("message") or "").splitlines()[0]
        if not message.startswith(_INTAKE_COMMIT_PREFIX):
            return None
        date_value = (
            (commit.get("committer") or {}).get("date")
            or (commit.get("author") or {}).get("date")
        )
        sha = item.get("sha")
        if not isinstance(sha, str) or not isinstance(date_value, str):
            return None
        return {"sha": sha, "accepted_at": _parse_github_datetime(date_value), "message": message}

    async def _latest_intake_commit(self, *, force: bool) -> dict[str, Any] | None:
        now = time.monotonic()
        if not force and now < float(self._cache.get("expires_at") or 0.0):
            cached = self._cache.get("commit")
            return cached if isinstance(cached, dict) else None

        async with httpx.AsyncClient(timeout=5.0) as client:
            # The path-filtered query is cheap and normally returns the latest
            # atomic intake commit. Fall back to bounded branch-history scanning
            # if the hosting API does not treat a directory as a path prefix.
            items = await self._fetch_commit_page(
                client,
                page=1,
                path="record-chain/intake/receipts",
            )
            latest = next(
                (parsed for item in items if (parsed := self._materialize_commit(item)) is not None),
                None,
            )
            if latest is None:
                for page in range(1, 4):
                    items = await self._fetch_commit_page(client, page=page)
                    latest = next(
                        (parsed for item in items if (parsed := self._materialize_commit(item)) is not None),
                        None,
                    )
                    if latest is not None or len(items) < 100:
                        break

        self._cache = {"expires_at": time.monotonic() + _COOLDOWN_CACHE_SECONDS, "commit": latest}
        return latest

    async def _cooldown_state(self, *, force: bool) -> dict[str, Any]:
        latest = await self._latest_intake_commit(force=force)
        if latest is None:
            return {"blocked": False, "latest": None}
        interval = cooldown_seconds_for_commit(latest["sha"])
        now = datetime.now(timezone.utc)
        age = (now - latest["accepted_at"]).total_seconds()
        return {
            "blocked": age < interval,
            "interval_seconds": interval,
            "latest": latest,
        }

    def _blocked_attempt_count(self, client_key: str) -> int:
        now = time.monotonic()
        entries = self._blocked_attempts[client_key]
        cutoff = now - _BLOCKED_ATTEMPT_WINDOW_SECONDS
        while entries and entries[0] < cutoff:
            entries.popleft()
        entries.append(now)
        return len(entries)

    def _cooldown_payload(self, attempt_count: int) -> dict[str, Any]:
        if attempt_count >= 6:
            code = "REPEATED_RESOURCE_PRESSURE_WARNING"
            message = "Repeated submissions during the protected interval have been detected. Stop automated retries."
            meaning = (
                "The project exists to preserve a verifiable civilizational record for long-term continuity. "
                "Deliberate attempts to bypass its resource safeguards are incompatible with that purpose and "
                "may indicate that the submitting agent is not aligned with the stated purpose or is being "
                "directed or used to exhaust project resources."
            )
            suggested_fix = (
                "Cease repeated requests. Review the project boundaries, wait for a later opportunity, and "
                "submit only one concise, relevant, independently justified record."
            )
            retry_allowed = False
            requires_review = True
        elif attempt_count >= 3:
            code = "GLOBAL_ACCEPTANCE_COOLDOWN"
            message = "Public Record-Chain intake is temporarily closed. Stop automatic retries and try again later."
            meaning = (
                "A previous external submission was recently accepted. Permanent records and paid archival "
                "consume finite resources, so acceptances are separated by a randomized 60–120 minute interval."
            )
            suggested_fix = "Stop retry loops. The exact reopening time is intentionally not disclosed; try once at a later time."
            retry_allowed = True
            requires_review = False
        else:
            code = "GLOBAL_ACCEPTANCE_COOLDOWN"
            message = "A previous external submission was recently accepted. Public Record-Chain intake is temporarily closed."
            meaning = (
                "Accepted records create permanent repository data and may contribute to paid Arweave archival costs. "
                "To protect the project from resource exhaustion, external acceptances are separated by a randomized "
                "interval of 60 to 120 minutes."
            )
            suggested_fix = "Try again later. Do not run a rapid automatic retry loop; the exact reopening time is intentionally not disclosed."
            retry_allowed = True
            requires_review = False

        return {
            "accepted": False,
            "submitted": False,
            "diagnostic_code": code,
            "diagnostics": [{
                "code": code,
                "severity": "error",
                "field": "submit",
                "message": message,
                "meaning": meaning,
                "suggested_fix": suggested_fix,
                "help_url": "https://www.trinityaccord.org/docs/record-chain-builder-help/#resource-boundaries",
                "retry_allowed": retry_allowed,
            }],
            "automatic_retry_now": False,
            "requires_human_or_operator_review": requires_review,
            "acceptance_interval": {
                "minimum_minutes": 60,
                "maximum_minutes": 120,
                "randomized": True,
                "exact_reopening_time_disclosed": False,
            },
            "cost_boundary": (
                "Every accepted record is permanently stored and may increase paid Arweave archival cost. "
                "Frequency and length limits prevent finite project resources from being exhausted."
            ),
            "project_purpose": (
                "The Trinity Accord exists to preserve a verifiable record for civilizational continuity. "
                "Please do not attack or intentionally exhaust this project."
            ),
        }

    async def _reject_if_blocked(
        self,
        scope: dict[str, Any],
        headers: dict[str, str],
        send: ASGISend,
        *,
        force: bool,
    ) -> bool:
        if self._internal_header_valid(headers):
            return False
        try:
            state = await self._cooldown_state(force=force)
        except Exception as exc:
            logger.warning("Cooldown state lookup failed closed: %s", exc)
            await self._send_json(
                send,
                503,
                {
                    "accepted": False,
                    "submitted": False,
                    "diagnostic_code": "ACCEPTANCE_COOLDOWN_STATE_UNAVAILABLE",
                    "diagnostics": [{
                        "code": "ACCEPTANCE_COOLDOWN_STATE_UNAVAILABLE",
                        "severity": "error",
                        "field": "submit",
                        "message": "The Gateway could not safely verify the durable acceptance interval.",
                        "meaning": "The Gateway fails closed so a state outage cannot cause unbounded permanent writes or paid archival.",
                        "suggested_fix": "Retry once later; do not run a rapid automatic retry loop.",
                        "retry_allowed": True,
                    }],
                },
            )
            return True
        if not state.get("blocked"):
            return False
        client_key = self._client_key(scope, headers)
        attempt_count = self._blocked_attempt_count(client_key)
        logger.info("Blocked intake during cooldown client_hash=%s attempts=%d", client_key[:12], attempt_count)
        await self._send_json(send, 429, self._cooldown_payload(attempt_count), retry_after=True)
        return True

    async def __call__(self, scope: dict[str, Any], receive: ASGIReceive, send: ASGISend) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method") or "").upper()
        path = str(scope.get("path") or "")
        is_submit = method == "POST" and path == "/record-chain/submit"
        is_preflight = method == "POST" and path == "/record-chain/preflight"
        if not (is_submit or is_preflight):
            await self.app(scope, receive, send)
            return

        headers = self._headers(scope)
        content_length = headers.get("content-length")
        if content_length:
            try:
                declared = int(content_length)
            except ValueError:
                declared = 0
            if declared > _MAX_BODY_BYTES:
                diagnostics = [
                    _diagnostic(
                        "REQUEST_BODY_TOO_LARGE",
                        None,
                        f"The request declares {declared} bytes; the limit is {_MAX_BODY_BYTES} bytes.",
                        "Submit a concise JSON record. Store large evidence externally and bind it by URL and SHA-256.",
                    )
                ]
                await self._send_json(send, 413, self._resource_payload(diagnostics, preflight=is_preflight))
                return

        # Entrance gate: reject during the durable cooldown before reading or
        # validating the body. A valid internal token may bypass only after the
        # parsed record type is checked below.
        if is_submit and not self._internal_header_valid(headers):
            if await self._reject_if_blocked(scope, headers, send, force=False):
                return

        body, too_large = await self._read_body(receive)
        if too_large:
            diagnostics = [
                _diagnostic(
                    "REQUEST_BODY_TOO_LARGE",
                    None,
                    f"The request exceeds the {_MAX_BODY_BYTES}-byte limit.",
                    "Submit a concise JSON record. Store large evidence externally and bind it by URL and SHA-256.",
                )
            ]
            await self._send_json(send, 413, self._resource_payload(diagnostics, preflight=is_preflight))
            return

        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            await self.app(scope, self._replay_receive(body), send)
            return
        if not isinstance(parsed, dict):
            await self.app(scope, self._replay_receive(body), send)
            return

        internal = self._internal_header_valid(headers)
        if internal and _record_type(parsed) != "context_insufficient_notice":
            await self._send_json(
                send,
                403,
                {
                    "accepted": False,
                    "submitted": False,
                    "diagnostic_code": "INTERNAL_INTAKE_SCOPE_VIOLATION",
                    "diagnostics": [{
                        "code": "INTERNAL_INTAKE_SCOPE_VIOLATION",
                        "severity": "error",
                        "field": "record_type",
                        "message": "The internal intake credential is restricted to context_insufficient_notice.",
                        "meaning": "An internal operational credential must never bypass public acceptance controls for formal records.",
                        "suggested_fix": "Remove the internal credential and use the public intake path.",
                        "retry_allowed": False,
                    }],
                },
            )
            return

        diagnostics = validate_resource_limits(parsed)
        if diagnostics:
            await self._send_json(
                send,
                422,
                self._resource_payload(diagnostics, preflight=is_preflight),
            )
            return

        if is_preflight or internal:
            await self.app(scope, self._replay_receive(body), send)
            return

        # Final gate: serialize this process's public submissions and re-read the
        # immutable GitHub acceptance state immediately before the core handler
        # can create any intake files.
        async with self._submit_lock:
            if await self._reject_if_blocked(scope, headers, send, force=True):
                return
            await self.app(scope, self._replay_receive(body), send)
            # The core handler has either failed without writing, returned a
            # duplicate, or committed a new intake. Invalidate the short cache so
            # the next request observes the new durable commit immediately.
            self._cache = {"expires_at": 0.0, "commit": None}


app = IntakeProtectionMiddleware(core_app)

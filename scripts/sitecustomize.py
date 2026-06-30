"""Runtime compatibility hooks for repository scripts.

Python loads this module automatically for commands executed as
``python scripts/<name>.py``.  Keep this file small and limited to repository
script compatibility; it must not change production Gateway runtime behavior.
"""
from __future__ import annotations

import builtins
import itertools
from types import ModuleType
from typing import Any

_ORIGINAL_IMPORT = builtins.__import__
_PATCHED_ATTR = "_trinity_record_chain_projection_compat_patched"


def _patch_gateway_authorship(module: ModuleType) -> None:
    """Patch Gateway authorship candidates for legacy builder projection fields.

    R62+ final records can contain protocol projection fields such as the draft
    schema marker that older builder/gateway combinations did not include in the
    Ed25519 signed payload hash. The actual signature still has to verify; this
    only adds narrow candidate payload domains for repository-side reverify.
    """
    if getattr(module, _PATCHED_ATTR, False):
        return

    base_candidates = getattr(module, "_signing_payload_candidates", None)
    canonical_bytes = getattr(module, "canonical_bytes", None)
    sha256_bytes = getattr(module, "sha256_bytes", None)
    strip_authorship = getattr(module, "strip_authorship_for_signing", None)
    if not all(callable(obj) for obj in (base_candidates, canonical_bytes, sha256_bytes, strip_authorship)):
        return

    def patched_candidates(record_draft: dict[str, Any]) -> list[tuple[str, dict[str, Any], bytes, str]]:
        candidates = list(base_candidates(record_draft))
        seen = {item[3] for item in candidates}
        primary_draft = strip_authorship(record_draft)
        fields = tuple(field for field in ("schema", "created_at") if field in primary_draft)
        for size in range(1, len(fields) + 1):
            for subset in itertools.combinations(fields, size):
                recovered = dict(primary_draft)
                for field in subset:
                    recovered.pop(field, None)
                payload = canonical_bytes(recovered)
                payload_sha = sha256_bytes(payload)
                if payload_sha in seen:
                    continue
                seen.add(payload_sha)
                candidates.append((
                    "record_draft_without_gateway_projection_" + "_and_".join(subset),
                    recovered,
                    payload,
                    payload_sha,
                ))
        return candidates

    setattr(module, "_signing_payload_candidates", patched_candidates)
    setattr(module, _PATCHED_ATTR, True)


def _import_hook(name: str, globals: dict[str, Any] | None = None, locals: dict[str, Any] | None = None,
                 fromlist: tuple[str, ...] = (), level: int = 0) -> Any:
    module = _ORIGINAL_IMPORT(name, globals, locals, fromlist, level)
    if name == "gateway.authorship":
        target = module if fromlist else getattr(module, "authorship", None)
        if isinstance(target, ModuleType):
            _patch_gateway_authorship(target)
    return module


builtins.__import__ = _import_hook

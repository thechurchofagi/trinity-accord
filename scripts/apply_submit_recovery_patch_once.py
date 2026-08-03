#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    replace_exact(
        "apps/record_chain_intake_gateway/app.py",
        '        receipt_path=receipt_path,\n        now=now,\n        oath_verification_summary=oath_summary,\n',
        '        receipt_path=receipt_path,\n        gateway_version=get_runtime_info()["version"],\n        now=now,\n        oath_verification_summary=oath_summary,\n',
    )
    replace_exact(
        "apps/record_chain_intake_gateway/app.py",
        '    pending_content_dict = strip_unsigned_projection_fields(draft)\n    if authorship_verified and proof:\n        pending_content_dict["authorship_proof"] = proof\n',
        '    pending_content_dict = strip_unsigned_projection_fields(draft)\n'
        '    if authorship_verified:\n'
        '        pending_content_dict["authorship_verification_status"] = {\n'
        '            "signed_payload_scope": "pre_append_record_draft",\n'
        '            "verified_by_gateway_before_pending": True,\n'
        '            "verified_by_append_before_record": False,\n'
        '            "final_record_contains_append_assigned_fields_not_in_signed_payload": True,\n'
        '        }\n'
        '    if authorship_verified and proof:\n'
        '        pending_content_dict["authorship_proof"] = proof\n',
    )

    replace_exact(
        "apps/record_chain_intake_gateway/protected_app.py",
        "from apps.record_chain_intake_gateway.app import app as core_app\n",
        "from apps.record_chain_intake_gateway import app as core_gateway\n"
        "from apps.record_chain_intake_gateway.gateway.canonical import sha256_canonical_json\n"
        "from apps.record_chain_intake_gateway.gateway.github_adapter import get_file_sha\n\n"
        "core_app = core_gateway.app\n",
    )
    replace_exact(
        "apps/record_chain_intake_gateway/protected_app.py",
        '_INTAKE_COMMIT_PREFIX = "intake: materialize "\n_COOLDOWN_CACHE_SECONDS = 3.0\n',
        '_INTAKE_COMMIT_PREFIX = "intake: materialize "\n_EXACT_RETRY_HEADER = "x-trinity-exact-retry"\n_COOLDOWN_CACHE_SECONDS = 3.0\n',
    )
    replace_exact(
        "apps/record_chain_intake_gateway/protected_app.py",
        '''    @staticmethod
    def _internal_header_valid(headers: dict[str, str]) -> bool:
        configured = os.environ.get("TRINITY_INTERNAL_INTAKE_TOKEN", "").strip()
        supplied = headers.get("x-trinity-internal-intake", "").strip()
        return bool(configured and supplied and hmac.compare_digest(configured, supplied))

    async def _read_body(self, receive: ASGIReceive) -> tuple[bytes, bool]:
''',
        '''    @staticmethod
    def _internal_header_valid(headers: dict[str, str]) -> bool:
        configured = os.environ.get("TRINITY_INTERNAL_INTAKE_TOKEN", "").strip()
        supplied = headers.get("x-trinity-internal-intake", "").strip()
        return bool(configured and supplied and hmac.compare_digest(configured, supplied))

    @staticmethod
    def _exact_retry_requested(headers: dict[str, str]) -> bool:
        return headers.get(_EXACT_RETRY_HEADER, "").strip() == "1"

    async def _materialized_exact_retry(self, body: dict[str, Any]) -> bool:
        submission_sha256 = sha256_canonical_json(body)
        index_path = (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        )
        return await get_file_sha(index_path) is not None

    async def _read_body(self, receive: ASGIReceive) -> tuple[bytes, bool]:
''',
    )
    replace_exact(
        "apps/record_chain_intake_gateway/protected_app.py",
        '''        # Entrance gate: reject during the durable cooldown before reading or
        # validating the body. A valid internal token may bypass only after the
        # parsed record type is checked below.
        if is_submit and not self._internal_header_valid(headers):
            if await self._reject_if_blocked(scope, headers, send, force=False):
                return

        body, too_large = await self._read_body(receive)
''',
        '''        # Normal public submissions are rejected before body parsing during the
        # durable cooldown. One Builder recovery retry may defer this entrance
        # check, but the final gate permits it only when the exact submission's
        # immutable idempotency index already exists.
        exact_retry_requested = is_submit and self._exact_retry_requested(headers)
        if (
            is_submit
            and not self._internal_header_valid(headers)
            and not exact_retry_requested
        ):
            if await self._reject_if_blocked(scope, headers, send, force=False):
                return

        body, too_large = await self._read_body(receive)
''',
    )
    replace_exact(
        "apps/record_chain_intake_gateway/protected_app.py",
        '''        async with self._submit_lock:
            if await self._reject_if_blocked(scope, headers, send, force=True):
                return
            await self.app(scope, self._replay_receive(body), send)
            # The core handler has either failed without writing, returned a
''',
        '''        async with self._submit_lock:
            materialized_exact_retry = False
            if exact_retry_requested:
                try:
                    materialized_exact_retry = await self._materialized_exact_retry(parsed)
                except Exception as exc:
                    logger.warning("Exact-retry idempotency lookup failed closed: %s", exc)
                    await self._send_json(
                        send,
                        503,
                        {
                            "accepted": False,
                            "submitted": False,
                            "diagnostic_code": "EXACT_RETRY_STATE_UNAVAILABLE",
                            "diagnostics": [{
                                "code": "EXACT_RETRY_STATE_UNAVAILABLE",
                                "severity": "error",
                                "field": "submit",
                                "message": "The Gateway could not verify whether this is an already-materialized exact retry.",
                                "meaning": "Exact retries fail closed unless the immutable submission idempotency index can be read.",
                                "suggested_fix": "Retry the exact same signed submission later; do not rebuild or mutate it.",
                                "retry_allowed": True,
                            }],
                        },
                    )
                    return

            if not materialized_exact_retry:
                if await self._reject_if_blocked(scope, headers, send, force=True):
                    return
            else:
                logger.info("Allowing exact materialized submission retry through cooldown")

            await self.app(scope, self._replay_receive(body), send)
            # The core handler has either failed without writing, returned a
''',
    )

    replace_exact(
        "downloads/record-chain-builder.mjs",
        '''async function postJson(url, body) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: resp.status, data };
}
''',
        '''async function postJson(url, body, extraHeaders = {}) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...extraHeaders },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: resp.status, data };
}

async function getJson(url) {
  const resp = await fetch(url, { headers: { "Accept": "application/json" } });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: resp.status, data };
}

function ambiguousSubmitRetryDelayMs() {
  const raw = process.env.TRINITY_SUBMIT_AMBIGUOUS_RETRY_DELAY_MS ?? "750";
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? Math.min(parsed, 10_000) : 750;
}

function receiptDateCandidates() {
  const now = new Date();
  return [0, -1].map((offsetDays) => {
    const date = new Date(now.getTime() + offsetDays * 86_400_000);
    return date.toISOString().slice(0, 10).replaceAll("-", "");
  });
}

async function recoverDurableReceipt(gateway, body) {
  const submissionSha256 = sha256(canonicalBytes(body));
  const receiptIds = receiptDateCandidates().map(
    (datePart) => `rcg-${datePart}-${submissionSha256.slice(0, 24)}`
  );
  const base = gateway.replace(/\\/+$/, "");
  const delayMs = ambiguousSubmitRetryDelayMs();

  for (let attempt = 0; attempt < 3; attempt += 1) {
    for (const receiptId of receiptIds) {
      try {
        const result = await getJson(`${base}/record-chain/receipt/${receiptId}`);
        const receipt = result.data && typeof result.data === "object"
          ? result.data.receipt
          : null;
        if (
          result.status === 200
          && receipt
          && receipt.submission_sha256 === submissionSha256
          && (receipt.server_receipt_id === receiptId || receipt.receipt_id === receiptId)
        ) {
          return {
            accepted: true,
            submitted: true,
            duplicate: true,
            recovered_after_ambiguous_submit: true,
            receipt_id: receiptId,
            record_type: receipt.record_type || "",
            submission_sha256: submissionSha256,
            append_status: result.data.final_status?.append_status || "recovered_existing_receipt",
            receipt,
            warnings: [
              "The initial submit result was ambiguous; the Builder recovered the immutable hash-verified receipt without creating another intake transaction."
            ],
          };
        }
      } catch {
        // Receipt visibility may race the repository or a transient proxy fault.
      }
    }
    if (attempt < 2 && delayMs > 0) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  return null;
}

async function postSubmitJsonWithRecovery(gateway, body) {
  const base = gateway.replace(/\\/+$/, "");
  const url = `${base}/record-chain/submit`;
  let first;
  try {
    first = await postJson(url, body);
  } catch (error) {
    first = { status: 0, data: null, transportError: String(error?.message || error) };
  }

  if (first.status !== 0 && first.status < 500) return first;

  const reason = first.status === 0
    ? `transport error: ${first.transportError}`
    : `HTTP ${first.status}`;
  console.error(
    `Submit result is ambiguous (${reason}). Checking the deterministic durable receipt before one exact recovery retry.`
  );

  const recovered = await recoverDurableReceipt(base, body);
  if (recovered) return { status: 200, data: recovered };

  const delayMs = ambiguousSubmitRetryDelayMs();
  if (delayMs > 0) await new Promise((resolve) => setTimeout(resolve, delayMs));
  try {
    return await postJson(url, body, { "X-Trinity-Exact-Retry": "1" });
  } catch (error) {
    return {
      status: 0,
      data: {
        accepted: false,
        submitted: false,
        diagnostics: [{
          code: "SUBMIT_RESULT_AMBIGUOUS",
          severity: "error",
          message: `The initial submit result was ambiguous and the one exact recovery retry also failed: ${String(error?.message || error)}`,
          suggested_fix: "Retry the exact same signed submission later. Do not rebuild, re-sign, or mutate it.",
          retry_allowed: true,
        }],
      },
    };
  }
}
''',
    )
    replace_exact(
        "downloads/record-chain-builder.mjs",
        '    const { status, data } = await postJson(`${gw}/record-chain/submit`, body);\n',
        '    const { status, data } = await postSubmitJsonWithRecovery(gw, body);\n',
    )

    replace_exact(
        "scripts/update_record_chain_builder_manifest.py",
        '    "submit",\n    "ed25519_authorship_proof",\n',
        '    "submit",\n    "ambiguous_submit_recovery",\n    "ed25519_authorship_proof",\n',
    )

    contract_path = ROOT / "api/record-chain-intake-gateway.v1.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["updated_at"] = "2026-08-03T01:20:00Z"
    contract["server_side_pipeline"]["ambiguous_submit_recovery"] = {
        "builder_checks_deterministic_receipt_first": True,
        "builder_maximum_exact_submit_retries": 1,
        "exact_retry_header": "X-Trinity-Exact-Retry: 1",
        "cooldown_bypass_requires_existing_submission_idempotency_index": True,
        "new_submissions_cannot_bypass_cooldown_with_retry_header": True,
        "same_signed_submission_bytes_required": True,
    }
    contract["runtime_alignment"]["gateway_authorship_verification_status_persisted_before_pending"] = True
    contract["runtime_alignment"]["receipt_gateway_version_uses_deployed_runtime"] = True
    contract_path.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

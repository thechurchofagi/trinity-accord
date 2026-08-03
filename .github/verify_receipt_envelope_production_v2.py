from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request


EXPECTED_MAIN_SHA = "685e14bc0d8d47d0a6999842bfbdf776b81f7544"
RECEIPT_ID = "rcg-20260802-c730d06fc9c928eadf08f342"
SUBMISSION_SHA = "c730d06fc9c928eadf08f342cdce766c6b446fcab83ea0861a7a7399032096bc"
RECORD_ID = "R-000000109"
RECORD_SHA = "9a66d5bac30bc7de4ef05d89f204074a3d643945637ec4035aa2d485296a1600"
RECEIPT_SHA = "7dc8f6b63c9defad4562f7c0c7eb096c912e04a6e07fdac18ff30ecd390b7746"
RECOVERY_WRAPPER_SHA = "190dde5c1d7f9469fb2880eb617c6218ddd654725bd64246f9e2807df1c738e1"
RECOVERY_WRAPPER_SIZE = 11853
BUILDER_CORE_SHA = "6b81d5e855d73db9e9b20dd756ac97ab72a55352589d06c16837779fdf3d0378"
BUILDER_CORE_SIZE = 195854


def _request_json(url: str, *, token: str | None = None, attempts: int = 16) -> tuple[int, dict, dict[str, str]]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        headers = {
            "User-Agent": "Trinity-Accord-Receipt-Envelope-Audit-v2/20260803",
            "Accept": "application/vnd.github+json" if "api.github.com" in url else "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                status = response.status
                response_headers = dict(response.headers.items())
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise AssertionError(f"JSON root is not an object for {url}")
            return status, data, response_headers
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                payload = {"raw": raw.decode("utf-8", errors="replace")}
            last_error = AssertionError(
                f"HTTP {exc.code} for {url}: {json.dumps(payload, sort_keys=True)}"
            )
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts:
                raise last_error
            retry_after = exc.headers.get("Retry-After")
            delay = int(retry_after) if retry_after and retry_after.isdigit() else min(5 * attempt, 20)
            time.sleep(delay)
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                raise
            time.sleep(min(5 * attempt, 20))
    raise last_error or RuntimeError(f"unable to fetch {url}")


def _request_list(url: str, *, token: str) -> tuple[list[dict], dict[str, str]]:
    headers = {
        "User-Agent": "Trinity-Accord-Receipt-Envelope-Audit-v2/20260803",
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        response_headers = dict(response.headers.items())
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise AssertionError(f"expected a JSON list of objects from {url}")
    return data, response_headers


def _last_page_from_link(link: str | None) -> int:
    if not link:
        return 1
    for part in link.split(","):
        if 'rel="last"' not in part:
            continue
        match = re.search(r"[?&]page=(\d+)", part)
        if match:
            return int(match.group(1))
    return 1


def wait_for_deployment_receipt() -> tuple[int, str]:
    token = os.environ["GH_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    base = f"https://api.github.com/repos/{repo}/issues/714/comments?per_page=100"
    sha_marker = f"Deployed source SHA: `{EXPECTED_MAIN_SHA}`"
    success_marker = "Receipt conclusion: `success`"

    for attempt in range(1, 41):
        _, first_headers = _request_list(base + "&page=1", token=token)
        last_page = _last_page_from_link(first_headers.get("Link"))
        pages = sorted({max(1, last_page - 1), last_page}, reverse=True)
        for page in pages:
            comments, _ = _request_list(base + f"&page={page}", token=token)
            for comment in reversed(comments):
                body = comment.get("body")
                if not isinstance(body, str):
                    continue
                if sha_marker not in body or success_marker not in body:
                    continue
                match = re.search(r"Run ID: `([0-9]+)`", body)
                if match is None:
                    raise AssertionError("exact deployment receipt is missing a numeric Run ID")
                return int(match.group(1)), body
        print(f"Exact deployment receipt not visible yet (attempt {attempt}/40).", flush=True)
        time.sleep(15)
    raise AssertionError(f"no successful exact-source deployment receipt for {EXPECTED_MAIN_SHA}")


def fetch_public_json(url: str) -> dict:
    status, data, _ = _request_json(url)
    if status != 200:
        raise AssertionError(f"expected HTTP 200 for {url}, got {status}")
    return data


def main() -> None:
    deploy_run_id, deployment_body = wait_for_deployment_receipt()
    print(deployment_body)

    gateway = "https://trinity-record-chain-gateway.onrender.com"
    site = "https://www.trinityaccord.org"
    audit_run = urllib.parse.quote(os.environ["GITHUB_RUN_ID"], safe="")

    before_tip = fetch_public_json(
        f"{site}/record-chain/chain-tip.json?phase=before&audit_run={audit_run}"
    )
    assert before_tip["latest_record_id"] == RECORD_ID
    assert before_tip["latest_record_index"] == 109
    assert before_tip["native_record_count"] == 109
    assert before_tip["latest_record_sha256"] == RECORD_SHA

    health = fetch_public_json(f"{gateway}/healthz")
    ready = fetch_public_json(f"{gateway}/readyz")
    assert health.get("ok") is True
    assert ready.get("ok") is True
    assert ready.get("version") == "1.2.1-protected"
    assert ready.get("protection_layer_active") is True
    limits = ready.get("read_route_limits")
    assert isinstance(limits, dict)
    assert limits.get("global_per_minute") == 600
    assert limits.get("client_per_minute") == 120
    assert limits.get("recovery_max_concurrency") == 8
    assert limits.get("recovery_cache_max_entries") == 2048

    receipt_envelope = fetch_public_json(
        f"{gateway}/record-chain/receipt/{RECEIPT_ID}"
    )
    assert receipt_envelope.get("found") is True
    assert receipt_envelope.get("receipt_hash_verified") is True
    assert receipt_envelope.get("receipt_url_binding_verified") is True
    assert receipt_envelope.get("stored_submission_hash_verified") is True
    receipt = receipt_envelope.get("receipt")
    assert isinstance(receipt, dict)
    assert receipt.get("server_receipt_id") == RECEIPT_ID
    assert receipt.get("submission_sha256") == SUBMISSION_SHA
    assert receipt.get("receipt_sha256") == RECEIPT_SHA
    assert receipt.get("record_type") == "verification"

    recovery = fetch_public_json(
        f"{gateway}/record-chain/recovery/submission/{SUBMISSION_SHA}"
    )
    assert recovery.get("found") is True
    assert recovery.get("recovery_verified") is True
    assert recovery.get("receipt_hash_verified") is True
    assert recovery.get("stored_submission_hash_verified") is True
    assert recovery.get("idempotency_index_binding_verified") is True
    assert recovery.get("submission_sha256") == SUBMISSION_SHA
    assert recovery.get("receipt_id") == RECEIPT_ID
    assert recovery.get("record_type") == "verification"
    boundary = recovery.get("boundary")
    assert isinstance(boundary, dict)
    assert boundary.get("read_only_recovery") is True
    assert boundary.get("does_not_create_submission") is True
    assert boundary.get("does_not_retry_submission") is True
    assert boundary.get("does_not_bypass_cooldown") is True

    manifest = fetch_public_json(
        f"{site}/api/record-chain-builder-bundles.v1.json?audit_run={audit_run}"
    )
    canonical = manifest["canonical_builder"]
    wrapper = canonical["recovery_wrapper"]
    core = canonical["core"]
    assert wrapper["sha256"] == RECOVERY_WRAPPER_SHA
    assert wrapper["size_bytes"] == RECOVERY_WRAPPER_SIZE
    assert wrapper["stored_submission_hash_verified"] is True
    assert wrapper["idempotency_index_binding_verified"] is True
    assert wrapper["http_429_recovery_attempts"] == 1
    assert wrapper["request_timeout_bounded"] is True
    assert core["sha256"] == BUILDER_CORE_SHA
    assert core["size_bytes"] == BUILDER_CORE_SIZE

    after_tip = fetch_public_json(
        f"{site}/record-chain/chain-tip.json?phase=after&audit_run={audit_run}"
    )
    assert after_tip == before_tip

    summary = {
        "schema": "trinityaccord.receipt-envelope-production-readonly-verification.v2",
        "production_main_sha": EXPECTED_MAIN_SHA,
        "deployment_run_id": str(deploy_run_id),
        "gateway": {
            "health_http": 200,
            "ready_http": 200,
            "version": ready["version"],
            "protection_layer_active": ready["protection_layer_active"],
            "read_route_limits": limits,
        },
        "receipt": {
            "receipt_id": RECEIPT_ID,
            "receipt_hash_verified": True,
            "receipt_url_binding_verified": True,
            "stored_submission_hash_verified": True,
        },
        "recovery": {
            "submission_sha256": SUBMISSION_SHA,
            "recovery_verified": True,
            "receipt_hash_verified": True,
            "stored_submission_hash_verified": True,
            "idempotency_index_binding_verified": True,
            "read_only": True,
        },
        "pages": {
            "chain_tip_before": before_tip,
            "chain_tip_after": after_tip,
            "chain_tip_unchanged": True,
            "recovery_wrapper_sha256": wrapper["sha256"],
            "builder_core_sha256": core["sha256"],
        },
        "submit_called": False,
        "preflight_called": False,
    }
    print("PRODUCTION_READONLY_VERIFICATION=" + json.dumps(summary, sort_keys=True))
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write("## Receipt-envelope production read-only verification v2\n\n")
            handle.write("```json\n")
            handle.write(json.dumps(summary, indent=2, sort_keys=True))
            handle.write("\n```\n")


if __name__ == "__main__":
    main()

from types import SimpleNamespace

import scripts.bitcoin_checkpoint_telemetry as telemetry


def _env():
    return {
        "GITHUB_REPOSITORY": "thechurchofagi/trinity-accord",
        "GITHUB_RUN_ID": "123456",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_SHA": "a" * 40,
    }


def _payload():
    return telemetry.build_payload(
        phase="syncing",
        chain={
            "chain": "main",
            "blocks": 100,
            "headers": 120,
            "bestblockhash": "b" * 64,
            "verificationprogress": 0.125,
            "initialblockdownload": True,
            "size_on_disk": 1234,
            "pruned": True,
            "pruneheight": 1,
            "warnings": [],
        },
        network={
            "networkactive": True,
            "connections": 8,
            "connections_in": 1,
            "connections_out": 7,
        },
        free_kib=9_000_000,
        seconds_remaining=10_000,
        observed_at="2026-08-31T07:15:00Z",
        env=_env(),
    )


def test_payload_is_explicitly_non_authoritative_and_run_bound():
    payload = _payload()
    assert payload["schema"] == telemetry.SCHEMA
    assert payload["authoritative"] is False
    assert payload["purpose"] == "live_observability_only_not_consensus_evidence"
    assert payload["run_id"] == "123456"
    assert payload["workflow_sha"] == "a" * 40
    assert payload["bitcoin"]["height"] == 100
    assert payload["bitcoin"]["headers"] == 120
    assert payload["bitcoin"]["header_backlog"] == 20
    assert payload["network"]["connections"] == 8
    assert payload["runner"]["free_kib"] == 9_000_000


def test_header_backlog_never_goes_negative():
    payload = telemetry.build_payload(
        phase="syncing",
        chain={"blocks": 125, "headers": 120},
        network={},
        free_kib=None,
        seconds_remaining=None,
        observed_at="2026-08-31T07:15:00Z",
        env=_env(),
    )
    assert payload["bitcoin"]["header_backlog"] == 0


def test_markdown_warns_that_live_check_is_not_evidence():
    markdown = telemetry.render_markdown(_payload())
    assert "NON-AUTHORITATIVE LIVE TELEMETRY" in markdown
    assert "mutable Check Run" in markdown
    assert "not a checkpoint" in markdown
    assert '"authoritative": false' in markdown
    assert '"height": 100' in markdown


def test_publish_check_creates_once_then_patches_same_check(monkeypatch, tmp_path):
    calls = []

    def fake_api(method, endpoint, payload):
        calls.append((method, endpoint, payload))
        stdout = '{"id":77}' if method == "POST" else '{}'
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr(telemetry, "_run_gh_api", fake_api)
    env = _env()
    env["BITCOIN_LIVE_CHECK_RUN_ID_FILE"] = str(tmp_path / "check-id")
    markdown = telemetry.render_markdown(_payload())

    assert telemetry.publish_check(markdown, env=env, complete=False, conclusion="neutral")
    assert (tmp_path / "check-id").read_text() == "77\n"
    assert telemetry.publish_check(markdown, env=env, complete=True, conclusion="neutral")

    create_method, create_endpoint, create_payload = calls[0]
    assert create_method == "POST"
    assert create_endpoint.endswith("/check-runs")
    assert create_payload["name"] == telemetry.CHECK_NAME
    assert create_payload["head_sha"] == "a" * 40
    assert create_payload["status"] == "in_progress"

    patch_method, patch_endpoint, patch_payload = calls[1]
    assert patch_method == "PATCH"
    assert patch_endpoint.endswith("/check-runs/77")
    assert patch_payload["status"] == "completed"
    assert patch_payload["conclusion"] == "neutral"
    assert "head_sha" not in patch_payload


def test_payload_only_exposes_aggregate_network_counts():
    payload = _payload()
    assert set(payload["network"]) == {
        "active",
        "connections",
        "connections_in",
        "connections_out",
    }

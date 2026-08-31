from scripts.bitcoin_checkpoint_telemetry import SCHEMA, build_payload, render_markdown


def _env():
    return {
        "GITHUB_REPOSITORY": "thechurchofagi/trinity-accord",
        "GITHUB_RUN_ID": "123456",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_SHA": "a" * 40,
    }


def test_payload_is_explicitly_non_authoritative_and_run_bound():
    payload = build_payload(
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

    assert payload["schema"] == SCHEMA
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
    payload = build_payload(
        phase="syncing",
        chain={"blocks": 125, "headers": 120},
        network={},
        free_kib=None,
        seconds_remaining=None,
        observed_at="2026-08-31T07:15:00Z",
        env=_env(),
    )
    assert payload["bitcoin"]["header_backlog"] == 0


def test_markdown_warns_that_live_release_is_not_evidence():
    payload = build_payload(
        phase="syncing",
        chain={"blocks": 1, "headers": 2},
        network={},
        free_kib=1,
        seconds_remaining=2,
        observed_at="2026-08-31T07:15:00Z",
        env=_env(),
    )
    markdown = render_markdown(payload)
    assert "NON-AUTHORITATIVE LIVE TELEMETRY" in markdown
    assert "not a checkpoint" in markdown
    assert '"authoritative": false' in markdown
    assert '"height": 1' in markdown

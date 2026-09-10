#!/usr/bin/env python3
import pathlib
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from capture_ethereum_beacon_finality import execution_hash, fetch_canonical_ssz, get, parse_providers


def main():
    value = {"data": {"message": {"body": {"execution_payload": {"block_hash": "0xAB"}}}}}
    assert execution_hash(value) == "0xab"
    assert len(parse_providers([])) == 2
    try:
        parse_providers(["only=https://example.com"])
    except ValueError:
        pass
    else:
        raise AssertionError("single-provider finality must fail closed")
    try:
        parse_providers(["../escape=https://one.example", "two=https://two.example"])
    except ValueError:
        pass
    else:
        raise AssertionError("provider names must not escape the evidence directory")

    class Response:
        headers = {}

        def read(self):
            return b"ok"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    with patch(
        "capture_ethereum_beacon_finality.urllib.request.urlopen",
        side_effect=[RuntimeError("rate limit")] * 4 + [Response()],
    ), patch("capture_ethereum_beacon_finality.time.sleep") as sleep:
        raw, headers = get("https://beacon.invalid/test", timeout=7)
    assert raw == b"ok" and headers == {}
    assert [call.args[0] for call in sleep.call_args_list] == [1, 2, 4, 8]

    attempts = []

    def transient_ssz(url, accept, timeout, retries):
        attempts.append(url)
        assert accept == "application/octet-stream" and timeout == 7 and retries == 1
        if "publicnode" in url:
            return b'{}', {"content-type": "application/json"}
        if attempts.count(url) == 1:
            raise RuntimeError("temporary rate limit")
        return b"canonical-ssz", {
            "content-type": "application/octet-stream",
            "eth-consensus-finalized": "true",
            "eth-consensus-version": "capella",
        }

    providers = [("publicnode", "https://publicnode.invalid"), ("lodestar", "https://lodestar.invalid")]
    with patch("capture_ethereum_beacon_finality.get", side_effect=transient_ssz), patch(
        "capture_ethereum_beacon_finality.time.sleep"
    ) as sleep:
        raw, fork, provider = fetch_canonical_ssz(providers, 123, 7, retries=2)
    assert (raw, fork, provider) == (b"canonical-ssz", "capella", "lodestar")
    sleep.assert_called_once_with(1)
    print("ethereum beacon finality capture tests: PASS")


if __name__ == "__main__":
    main()

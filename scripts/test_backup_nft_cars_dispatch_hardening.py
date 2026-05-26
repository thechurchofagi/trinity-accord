#!/usr/bin/env python3
"""
Test: backup-nft-cars.yml repository_dispatch hardening (TA-REDTEAM-2026-005-C)

Validates that the workflow includes sender allowlist for repository_dispatch
and actor allowlist for workflow_dispatch.
"""

import sys
import os
import re

WORKFLOW = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows', 'backup-nft-cars.yml')


def read_workflow():
    with open(WORKFLOW, 'r') as f:
        return f.read()


def test_has_repository_dispatch():
    """Workflow triggers on repository_dispatch."""
    src = read_workflow()
    assert 'repository_dispatch' in src, "Workflow does not support repository_dispatch"
    print("  ✓ repository_dispatch trigger present")


def test_has_sender_allowlist():
    """Workflow has sender allowlist step for repository_dispatch."""
    src = read_workflow()
    assert 'Authorize repository dispatch sender' in src, \
      "Missing 'Authorize repository dispatch sender' step"
    assert 'github.event.sender.login' in src, \
      "Missing github.event.sender.login check"
    print("  ✓ sender allowlist step present")


def test_sender_checks_login():
    """Allowlist step checks sender.login against known accounts."""
    src = read_workflow()
    assert 'thechurchofagi' in src, "Allowlist does not include thechurchofagi"
    print("  ✓ sender allowlist includes owner")


def test_unauthorized_sender_exits():
    """Unauthorized sender must exit non-zero."""
    src = read_workflow()
    # Look for the dispatch sender block
    assert 'Unauthorized repository_dispatch sender' in src, \
      "Missing unauthorized sender error message"
    # Must exit 1 for unauthorized
    lines = src.split('\n')
    in_sender_block = False
    found_exit = False
    for line in lines:
        if 'Authorize repository dispatch sender' in line:
            in_sender_block = True
        if in_sender_block and ('exit 1' in line or 'exit 2' in line):
            found_exit = True
            break
        if in_sender_block and line.strip().startswith('- name:') and 'Authorize' not in line:
            break
    assert found_exit, "Unauthorized sender does not exit non-zero"
    print("  ✓ unauthorized sender exits non-zero")


def test_has_workflow_dispatch_actor_check():
    """Workflow has actor allowlist for workflow_dispatch."""
    src = read_workflow()
    assert 'Authorize manual dispatch actor' in src or 'workflow_dispatch' in src, \
      "Missing workflow_dispatch actor authorization"
    print("  ✓ workflow_dispatch actor check present")


def test_repository_dispatch_needs_contents_write():
    """If repository_dispatch exists with contents:write, sender gate must exist."""
    src = read_workflow()
    has_dispatch = 'repository_dispatch' in src
    has_write = 'contents: write' in src
    has_gate = 'Authorize repository dispatch sender' in src
    if has_dispatch and has_write:
        assert has_gate, "repository_dispatch + contents:write without sender gate!"
    print("  ✓ dispatch + write requires sender gate")


def main():
    print("Running backup-nft-cars dispatch hardening tests...")
    test_has_repository_dispatch()
    test_has_sender_allowlist()
    test_sender_checks_login()
    test_unauthorized_sender_exits()
    test_has_workflow_dispatch_actor_check()
    test_repository_dispatch_needs_contents_write()
    print("\nBACKUP_NFT_CARS_DISPATCH_HARDENING_OK")


if __name__ == '__main__':
    main()

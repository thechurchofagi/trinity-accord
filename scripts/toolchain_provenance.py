#!/usr/bin/env python3
"""Collect toolchain provenance for CI reproducibility.

Outputs JSON with versions of all tools used in verification/generation.
Schema: trinity-accord.toolchain-provenance.v1
"""
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

COMMANDS = {
    "python": ["python3", "--version"],
    "pip": ["python3", "-m", "pip", "--version"],
    "node": ["node", "--version"],
    "npm": ["npm", "--version"],
    "git": ["git", "--version"],
    "gh": ["gh", "--version"],
    "curl": ["curl", "--version"],
    "tar": ["tar", "--version"],
    "gzip": ["gzip", "--version"],
    "sha256sum": ["sha256sum", "--version"],
    "openssl": ["openssl", "version"],
    "ots": ["ots", "--version"],
    "bitcoin_cli": ["bitcoin-cli", "--version"],
}


def run(cmd):
    exe = cmd[0]
    if shutil.which(exe) is None:
        return {"available": False, "version": None, "error": "not found"}
    try:
        res = subprocess.run(cmd, text=True, capture_output=True, timeout=10)
        out = (res.stdout or res.stderr or "").strip().splitlines()
        return {
            "available": res.returncode == 0,
            "version": out[0] if out else "",
            "returncode": res.returncode,
        }
    except Exception as e:
        return {"available": False, "version": None, "error": str(e)}


def collect():
    return {
        "schema": "trinity-accord.toolchain-provenance.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_implementation": platform.python_implementation(),
        },
        "github_actions": {
            "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS"),
            "RUNNER_OS": os.environ.get("RUNNER_OS"),
            "ImageOS": os.environ.get("ImageOS"),
            "ImageVersion": os.environ.get("ImageVersion"),
            "GITHUB_WORKFLOW": os.environ.get("GITHUB_WORKFLOW"),
            "GITHUB_RUN_ID": os.environ.get("GITHUB_RUN_ID"),
            "GITHUB_SHA": os.environ.get("GITHUB_SHA"),
        },
        "tools": {name: run(cmd) for name, cmd in COMMANDS.items()},
    }


def main():
    data = collect()
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

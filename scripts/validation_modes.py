#!/usr/bin/env python3
"""
Unified validation mode enforcement for Trinity Accord.
Modes: dev, archive, ci
"""
import os
import sys

VALID_MODES = ("dev", "archive", "ci")

def get_validation_mode():
    """Get current validation mode from env or CLI context."""
    env_mode = os.environ.get("TRINITY_VALIDATION_MODE", "").strip().lower()
    if env_mode in VALID_MODES:
        return env_mode
    return "archive"  # default is STRICT

def is_strict_mode(mode=None):
    """Check if mode is strict (archive or ci)."""
    if mode is None:
        mode = get_validation_mode()
    return mode in ("archive", "ci")

def enforce_strict_jsonschema(mode=None, allow_missing_flag=False):
    """Enforce jsonschema availability in strict modes.
    
    Returns True if jsonschema is required and available.
    Raises SystemExit if strict mode requires jsonschema but it's missing or --allow-missing-jsonschema is used.
    """
    if mode is None:
        mode = get_validation_mode()
    
    if allow_missing_flag and mode != "dev":
        print(f"ERROR: --allow-missing-jsonschema is dev-only and forbidden in {mode} mode", file=sys.stderr)
        sys.exit(1)
    
    if is_strict_mode(mode):
        try:
            import jsonschema
            return True
        except ImportError:
            print(f"ERROR: jsonschema is required in {mode} mode but not installed", file=sys.stderr)
            sys.exit(1)
    
    # dev mode - jsonschema optional
    try:
        import jsonschema
        return True
    except ImportError:
        print("WARNING: jsonschema not available, running in dev mode with limited validation", file=sys.stderr)
        return False

#!/usr/bin/env python3
"""Compatibility entry point for strict published sidechain Zenodo reconciliation."""
from reconcile_chronicle_sidechain_zenodo_published_v2 import main


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)

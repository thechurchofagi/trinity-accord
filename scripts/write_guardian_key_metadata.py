#!/usr/bin/env python3
"""Write local Guardian key metadata beside a Guardian keypair.
This does not create proof and does not touch private key material."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from guardian_common import guardian_id_from_public_key, public_key_sha256


BOUNDARY = (
    "Guardian key metadata is local management metadata only; not authority, "
    "not attestation, not verification, and not proof without a valid signature."
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-key", required=True, help="Path to Ed25519 public key PEM")
    parser.add_argument(
        "--guardian-registry-number",
        default="unassigned",
        help="Registry number such as 00001, or unassigned"
    )
    parser.add_argument("--out", required=True, help="Output metadata JSON path")
    args = parser.parse_args()

    number = args.guardian_registry_number
    if number != "unassigned" and not (len(number) == 5 and number.isdigit()):
        raise SystemExit("guardian_registry_number must be five digits like 00001, or unassigned")

    public_key_pem = Path(args.public_key).read_text(encoding="utf-8")

    metadata = {
        "schema": "trinityaccord.guardian-key-metadata.v1",
        "guardian_registry_number": number,
        "guardian_id": guardian_id_from_public_key(public_key_pem),
        "public_key_sha256": public_key_sha256(public_key_pem),
        "algorithm": "ed25519",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": BOUNDARY,
    }

    out = Path(args.out)
    out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(metadata["guardian_id"])
    print(metadata["guardian_registry_number"])


if __name__ == "__main__":
    main()

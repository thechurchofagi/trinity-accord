#!/usr/bin/env python3
"""Regression contract for inscription identifiers and visible text links."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "97631551": "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0",
    "98369145": "90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258i0",
    "98387475": "4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8ci0",
    "100385359": "f411d2db9ec9e077277ff1cf3abed39628d86b1d39db1964061eafe5b02c2e81i0",
    "100550942": "25af4e24cb0a2cd85ac396bd88c348f8da3169c24813800ecb8736dd2c7a5ae7i0",
    "100751953": "4711ff186613bdd75b7e36070b3097c38efde110f90df94847592ff6997f45f1i0",
    "103034280": "128aabfa3077efc832d30e6e2a96848a96896bbdbf4a7667912f55d25dcb6687i0",
    "103635270": "0eecd48430f8239f5d543b5cf2ee928969a1aac7660808fd869a78aa27949c9ci0",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    index = json.loads((ROOT / "api/bitcoin-inscription-mirror-index.json").read_text(encoding="utf-8"))
    authority_page = (ROOT / "authority-address-inscriptions.md").read_text(encoding="utf-8")
    originals_page = (ROOT / "inscriptions.md").read_text(encoding="utf-8")
    style = (ROOT / "assets/css/style.scss").read_text(encoding="utf-8")
    home_base = (ROOT / "assets/css/trinity-home-base.css").read_text(encoding="utf-8")

    records = index.get("records", [])
    require(len(records) == 8, "mirror index must contain all eight inscriptions")
    for record in records:
        inscription = record.get("inscription", {})
        number = inscription.get("inscription_number")
        require(number in EXPECTED, f"unexpected or missing inscription number: {number}")
        require(inscription.get("ordinals_inscription_id") == EXPECTED[number], f"full ID mismatch for {number}")
        require(EXPECTED[number] in authority_page, f"authority page missing full ID for {number}")
        require(f"https://ordinals.com/inscription/{EXPECTED[number]}" in authority_page, f"authority page missing chain link for {number}")

    for number in ("97631551", "98369145", "98387475"):
        require(EXPECTED[number] in originals_page, f"canonical page missing full ID for {number}")

    require("| Inscription Number | Status |" in authority_page, "verification table still mislabels numbers as IDs")
    require("text-decoration-line: underline" in style, "content-page text links are not visibly underlined")
    require("text-decoration-line: underline !important" in home_base, "homepage text links are not visibly underlined")
    require("word-break: break-all" in style, "long inscription IDs do not wrap on mobile")

    print("PASS: inscription numbers, full IDs, chain links, and visible link styling are complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

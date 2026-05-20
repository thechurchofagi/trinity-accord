#!/usr/bin/env python3
"""Generate NFT chronicle context artifacts from index.json."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
INDEX = DIR / "index.json"

BOUNDARY_TEXT = (
    "Historical chronicle context, not canonical authority. "
    "Not truth proof. Not Arweave/CAR/media verification by itself. "
    "Ethereum timestamps are event block timestamps."
)


def main():
    if not INDEX.exists():
        print("ERROR: index.json not found")
        return 1

    index = json.loads(INDEX.read_text(encoding="utf-8"))

    if len(index) != 175:
        print(f"ERROR: index must have exactly 175 entries, found {len(index)}")
        return 1

    # Validate all MD files
    for item in index:
        fname = item.get("file")
        if not fname:
            print(f"ERROR: entry missing 'file': {item.get('contract')} {item.get('token_id')}")
            return 1
        p = DIR / fname
        if not p.exists():
            print(f"ERROR: missing file: {fname}")
            return 1
        text = p.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            print(f"ERROR: empty file: {fname}")
            return 1

    # Separate dated and undated
    dated = [e for e in index if e.get("timestamp") is not None]
    undated = [e for e in index if e.get("timestamp") is None]

    # Sort dated by timestamp
    dated.sort(key=lambda x: x["timestamp"])

    print(f"Total entries: {len(index)}")
    print(f"Dated entries: {len(dated)}")
    print(f"Undated entries: {len(undated)}")

    # Build chronicle-index.json
    entries = []
    for e in index:
        entry = {
            "contract": e.get("contract", ""),
            "token_id": str(e.get("token_id", "")),
            "file": e.get("file", ""),
            "timestamp": e.get("timestamp"),
            "datetime": e.get("datetime"),
            "block": e.get("block"),
            "timestamp_method": e.get("timestamp_method"),
            "name": e.get("name", ""),
        }
        entries.append(entry)

    # Sort: dated first (by timestamp), then undated
    dated_entries = [e for e in entries if e["timestamp"] is not None]
    undated_entries = [e for e in entries if e["timestamp"] is None]
    dated_entries.sort(key=lambda x: x["timestamp"])
    sorted_entries = dated_entries + undated_entries

    chronicle_index = {
        "schema": "trinityaccord.nft-chronicle-index.v1",
        "total_entries": 175,
        "dated_entries": len(dated),
        "undated_entries": len(undated),
        "source": "nft-text-descriptions/index.json + individual markdown description files",
        "boundary": {
            "historical_context_not_canonical_authority": True,
            "not_truth_proof": True,
            "not_arweave_or_media_verification_by_itself": True,
            "timestamps_are_ethereum_event_block_timestamps": True,
        },
        "entries": sorted_entries,
    }

    out_index = DIR / "chronicle-index.json"
    out_index.write_text(json.dumps(chronicle_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_index.relative_to(ROOT)}")

    # Build chronicle-full.md
    lines = []
    lines.append("# NFT Chronicle — Full Timeline")
    lines.append("")
    lines.append(f"**Total entries**: {len(index)}")
    lines.append(f"**Dated entries**: {len(dated)}")
    lines.append(f"**Undated entries**: {len(undated)}")
    lines.append("")
    lines.append(f"> {BOUNDARY_TEXT}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Timeline")
    lines.append("")

    for i, e in enumerate(dated_entries, 1):
        dt_str = e.get("datetime", "unknown")
        contract_short = e["contract"][:10] + "..."
        token_short = e["token_id"][:20] + "..." if len(e["token_id"]) > 20 else e["token_id"]
        name = e.get("name", "Untitled")
        lines.append(f"### {i}. {name}")
        lines.append("")
        lines.append(f"- **Timestamp**: {dt_str}")
        lines.append(f"- **Block**: {e.get('block', 'N/A')}")
        lines.append(f"- **Contract**: `{e['contract']}`")
        lines.append(f"- **Token ID**: `{token_short}`")
        lines.append(f"- **Method**: {e.get('timestamp_method', 'N/A')}")
        lines.append(f"- **File**: `{e.get('file', 'N/A')}`")
        lines.append("")

    if undated_entries:
        lines.append("---")
        lines.append("")
        lines.append("## Timestamp-Unresolved Appendix")
        lines.append("")
        lines.append(f"The following {len(undated_entries)} entries have no resolved Ethereum timestamp.")
        lines.append("")
        for e in undated_entries:
            name = e.get("name", "Untitled")
            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- **Contract**: `{e['contract']}`")
            lines.append(f"- **Token ID**: `{e['token_id']}`")
            lines.append(f"- **File**: `{e.get('file', 'N/A')}`")
            lines.append("- **Status**: timestamp unresolved")
            lines.append("")
    else:
        lines.append("---")
        lines.append("")
        lines.append("**Undated entries: 0** — All entries have resolved Ethereum timestamps.")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*{BOUNDARY_TEXT}*")
    lines.append("")

    out_full = DIR / "chronicle-full.md"
    out_full.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_full.relative_to(ROOT)}")

    # Build chronicle-agent-context.md
    ctx = []
    ctx.append("# NFT Chronicle — Agent Context")
    ctx.append("")
    ctx.append("> **Not canonical authority.** This is historical chronicle context for agent consumption.")
    ctx.append("")
    ctx.append(f"> {BOUNDARY_TEXT}")
    ctx.append("")
    ctx.append("## Summary")
    ctx.append("")
    ctx.append(f"- **Total NFTs**: {len(index)}")
    ctx.append(f"- **With Ethereum timestamps**: {len(dated)}")
    ctx.append(f"- **Without timestamps**: {len(undated)}")
    ctx.append(f"- **Timeline span**: {dated[0].get('datetime', 'N/A')} → {dated[-1].get('datetime', 'N/A')}" if dated else "- **Timeline span**: N/A")
    ctx.append("")
    ctx.append("## Timeline Summary")
    ctx.append("")
    ctx.append("The following is a chronological summary of NFT mint events.")
    ctx.append("Each entry represents an ASIMilestone NFT minted on Ethereum.")
    ctx.append("")

    for i, e in enumerate(dated_entries, 1):
        dt = e.get("datetime", "unknown")
        name = e.get("name", "Untitled")
        ctx.append(f"{i}. **{dt}** — {name}")

    if undated_entries:
        ctx.append("")
        ctx.append(f"**{len(undated_entries)} unresolved timestamp(s)**:")
        for e in undated_entries:
            ctx.append(f"- {e.get('name', 'Untitled')} (contract: `{e['contract'][:10]}...`)")

    ctx.append("")
    ctx.append("## Boundary")
    ctx.append("")
    ctx.append("- Historical chronicle context, not canonical authority")
    ctx.append("- Not truth proof")
    ctx.append("- Not Arweave/CAR/media verification by itself")
    ctx.append("- Ethereum timestamps are event block timestamps")
    ctx.append("")
    ctx.append("## Contract")
    ctx.append("")
    ctx.append(f"All entries share contract: `{dated[0]['contract']}`" if dated else "N/A")
    ctx.append("")

    out_ctx = DIR / "chronicle-agent-context.md"
    out_ctx.write_text("\n".join(ctx), encoding="utf-8")
    print(f"Wrote {out_ctx.relative_to(ROOT)}")

    print("Chronicle context generation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

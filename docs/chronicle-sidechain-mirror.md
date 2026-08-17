# Chronicle Polygon + Base historical NFT mirror

This recovery path enumerates the historical ERC-721 and ERC-1155 activity of the Chronicle source address on Polygon (chain ID 137) and Base (chain ID 8453), then preserves the recoverable NFT payloads in an immutable GitHub Release snapshot.

## Scope

The scanner records transfer coordinates, contract/token IDs, transaction hashes, block/timestamp data, on-chain `tokenURI(uint256)` or `uri(uint256)` reads, Blockscout NFT-instance responses, resolved metadata, referenced image/animation/media bytes, and SHA-256 manifests.

Discovery is historical, not balance-based: NFTs that were later transferred away remain in scope. The current `token_index.json` is compared by contract/token ID so the report can identify possible omissions without modifying the existing 175-NFT mirror. Because that comparison does not encode chain identity, a same contract/token coordinate is only an overlap heuristic, not proof of logical record identity.

## Evidence boundary

A sidechain occurrence is not automatically a new logical Chronicle record. Cross-chain remints or duplicate representations must be reviewed semantically before changing any Chronicle count. Likewise, the earliest sidechain NFT transfer found by this workflow is evidence about address history; it does not by itself amend Canon or redefine the formation interval.

The workflow never edits the three Bitcoin Canon inscriptions.

## Sources

Historical discovery uses the Polygon and Base Blockscout v2 address token-transfer API, one ERC standard at a time, and follows `next_page_params` until exhaustion. Every discovery page is preserved verbatim in the mirror. If a v2 call fails, the scanner attempts the corresponding legacy Blockscout account API as a fallback and fails closed if both sources fail.

Token URIs are read independently through Polygon/Base JSON-RPC endpoints. Optional repository secrets `POLYGON_RPC_URL`, `BASE_RPC_URL`, and `BLOCKSCOUT_API_KEY` can replace public defaults or authenticate the legacy fallback.

## Output

Each successful run creates an immutable release tag:

`chronicle-sidechain-mirror-v1-<source-commit>`

The release contains the complete tarball, its SHA-256, `SUMMARY.json`, and per-file manifests. The summary reports Polygon/Base counts separately, the earliest observed transfer on each network, the global earliest observed sidechain transfer, metadata recovery totals, and heuristic overlap with the current `token_index.json`.

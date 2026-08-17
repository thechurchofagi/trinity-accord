# Chronicle sidechain mirror observability

The Polygon/Base Chronicle recovery job is intentionally long-running because it performs historical discovery, token URI reads, metadata/media recovery, hashing, packaging, and immutable Release publication.

The observed runner wrapper makes that work inspectable while it is running:

- emits a `[HEARTBEAT]` line every 60 seconds;
- reports discovery page count, recovered NFT record count, normalized metadata count, media file count, total files, bytes on disk, and latest non-runtime output file;
- emits `[STALL WARNING]` after five minutes with no observable artifact-count/size progress;
- performs Blockscout and JSON-RPC preflight checks;
- records the scanner stdout/stderr in `runtime/scanner.log`;
- writes `runtime/HEARTBEAT.json` continuously and `runtime/FINAL-DIAGNOSTICS.json` at exit;
- fails closed when the scanner exits successfully but `SUMMARY.json` or either SHA-256 manifest is missing/empty;
- validates `SUMMARY.json` and prints per-chain result counts and earliest observed timestamps before packaging.

The wrapper changes only operational visibility and completion checks. It does not amend Canon, change Chronicle membership, or infer formation dates from sidechain observations.

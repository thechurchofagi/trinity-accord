# A4G gap ledger

## A4G-G00 — corrupted remote review ledger

- **Location:** branch head `b013ae7f...`, `REVIEW_SUPERVISION.md`.
- **Impact:** the mandatory review entry became unreadable and its SHA256 (`63a998...`) disagreed with `CURRENT_STATE.review_ledger_sha256` (`5f270b...`). A future round could silently miss open obligations.
- **Counterexample:** file-type inspection reports binary data, while the verified A4F text copy is UTF-8 and hashes to the state-recorded value.
- **Correction:** restore the verified UTF-8 bytes, retain every OPEN/ACKNOWLEDGED item, record both hashes and verify the new remote blob.
- **Still open:** why the earlier object write transformed the file; global audit of other historical objects is not completed.

## A4G-G01 — graph cut does not type control capability

- **Impact:** a shared ancestor may be wrongly treated as able to forge a complete target vector.
- **Counterexample:** suppress-only root reaches all witnesses but cannot synthesize target provenance.
- **Correction:** edges and roots are typed by observe/suppress/retime/reset/replay/forge.
- **Still open:** actual device capability evidence.

## A4G-G02 — union coverage does not establish same-trial composition

- **Impact:** five coordinate covers would be misreported as five observational twins.
- **Counterexample:** four require a declared incompatible bus-DMA plus trusted-clock mode.
- **Correction:** test joint compatibility after coordinate coverage; only one twin remains.
- **Still open:** real controller concurrency and cross-coordinate constraints.

## A4G-G03 — protected coordinate is conditional and replay-sensitive

- **Impact:** the positive separator could be mistaken for a hardware installation or general provenance theorem.
- **Counterexample:** grant maintenance replay of the protected coordinate; the twin returns.
- **Correction:** keep the result disabled and require post-arbitration generation plus protected acquisition/acceptance path.
- **Still open:** physical installation, complete writer inventory, complete K, RetBind and H_way bridge.

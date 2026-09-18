# Source transport

The `source.b64.partNN` files are transport-only fragments for the reviewed TA-TR-2026-05 publication source. Concatenate them in lexical order, Base64-decode, and treat the result as an XZ-compressed tar archive.

- Part count: 8 (`part00` through `part07`)
- Decoded `source.tar.xz` bytes: 65,640
- Decoded `source.tar.xz` SHA-256: `3ee15094ff2beb030c14736572b39f5c5258f64691193a0daada0abcb57888cc`
- Root directory: `TA-TR-2026-05_v1.0`
- Reserved Zenodo record: `22809019`
- Reserved DOI: `10.5281/zenodo.22809019`

The capsule is derived from the complete reviewed paper-and-reproducibility package. Publication-state fields, citation metadata, license notice, capsule manifest, checksums, and manuscript status lines are synchronized to the reserved DOI. The research model, results, references, and substantive findings are unchanged. Prebuilt pre-reservation PDFs are intentionally excluded because the publication workflow rebuilds both PDFs from the synchronized Markdown sources.

Publication must verify the decoded archive hash and structure, reproduce the finite study, build exactly ten public files, publish only record `22809019`, and perform public byte-for-byte readback before recording success.

The transport is isolated from the four prior DOI deposits and from the three Bitcoin Originals.

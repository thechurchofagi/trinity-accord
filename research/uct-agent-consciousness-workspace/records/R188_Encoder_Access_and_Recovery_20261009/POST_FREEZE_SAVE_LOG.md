# Post-freeze delivery log

Scientific content is frozen at commit `fa32518b0d956a461db65416920ec2eea8acfe88`. All69written Git blob identities were compared with locally computed exact-byte hashes; the branch head, current state and full manuscript were read back. The capsule was restored with all82members verified, and its reconstruction reproduced the exact graph and ledger hashes.

The first delivery-packaging command failed at Python parsing because a non-ASCII dash appeared inside a bytes literal. No statement in that script executed, so it did not create a partial archive or modify the existing shared handoff. The separator was changed to an explicitly encoded UTF-8 string before retry. This is a delivery-script failure, not a scientific result or change to the frozen paper/code/evidence.

The complete research archive is verified by every listed member's SHA256 and ZIP CRC. The archive's own digest and subsequent user-file save facts belong in the external persistence receipt, avoiding circular self-hashes or claims about future saves. The shared handoff replacement retains every prior version43byte and uses the observed version guard.

## Final readback

All five saves succeeded and were downloaded again for verification. ZIP, both standalone text deliverables and the master are byte-identical; the master is version44 and preserves all prior553,284bytes. The standalone PDF is a C2PA-bearing derivative with unchanged13-page rendering, text and decoded content streams. Its separate hash is recorded.

A first raster comparison failed on a truncated old page04 PNG and an empty new page11 PNG. The dependent receipt write then failed before mutation because its input equality report was missing. The final check rendered both PDFs in memory and compared every108dpi page pixel, extracted text and decoded page content stream. All matched. No damaged PNG was accepted and no scientific source was modified. See SAVE_READBACK_REPORT.md and the final root persistence receipt.

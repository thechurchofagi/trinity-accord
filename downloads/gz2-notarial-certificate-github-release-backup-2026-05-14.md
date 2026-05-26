---
title: "GZ2 Notarial Certificate GitHub Release Backup"
description: "GitHub Release backup verification for GZ2 redacted notarial certificate printed attachments."
permalink: /downloads/gz2-notarial-certificate-github-release-backup-2026-05-14/
---

# GZ2 Notarial Certificate GitHub Release Backup

This page describes the GitHub Release backup mirror for the GZ2 redacted second-capture notarial-certificate photo archive.

## Release

```text
Tag:
core-object-alpha-notarial-certificate-gz2-custody-public-backup-v1
```

## Source Arweave records

The source records are the Arweave TXIDs listed in:

```text
/api/gz2-notarial-certificate-redacted-attachments-2026-05-14.json
```

## Expected Release assets

```text
gz2-notarial-certificate-redacted-attachments-2026-05-14.zip
gz2-notarial-certificate-redacted-attachments-2026-05-14-arweave-index.json
gz2-notarial-certificate-redacted-attachments-2026-05-14-timestamp-files.zip
sealed-disc-custody-record.json
gz2-notarial-certificate-redacted-attachments-2026-05-14-release-assets.sha256
gz2-notarial-certificate-redacted-attachments-2026-05-14-release-notes.md
```

## Verification steps

1. Download the Release assets.
2. Verify Release asset hashes against the `.sha256` file.
3. Verify the Arweave TXIDs listed in the Arweave index.
4. Verify that the GZ2 manifest and OTS proof are available from Arweave.
5. Verify the OTS proof locally if a Bitcoin Core node is available, or record that local Bitcoin-node verification was not performed.
6. Confirm that the sealed-disc custody record does not claim disc-content verification.

## Boundary

This GitHub Release is a non-amending availability mirror.

It does not replace Arweave.

It does not replace the original 2026-05-06 evidence archive.

It does not claim equality between GZ2 images and original Cunzhengtong electronic files.

It does not claim verification of sealed-disc contents.

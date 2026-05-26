---
title: "Shenzhen Notary GitHub Release Backup"
description: "GitHub Release backup verification for the 2026-05-06 Core Object Alpha Shenzhen notary Arweave archive."
permalink: /downloads/shenzhen-notary-github-release-backup-2026-05-06/
---

# Shenzhen Notary GitHub Release Backup

This page describes the GitHub Release backup mirror for the 2026-05-06 Core Object Alpha Shenzhen notary Arweave archive.

## Release

- Tag: `core-object-alpha-shenzhen-notary-arweave-backup-v1`
- Release URL: <https://github.com/thechurchofagi/trinity-accord/releases/tag/core-object-alpha-shenzhen-notary-arweave-backup-v1>

## Source Arweave archive

- Manifest TXID: `_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE`
- Manifest index: <https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE/index.html>
- Raw manifest: <https://arweave.net/raw/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE>
- Index JSON: <https://arweave.net/7jx4hMydXh7jXv-3WdAgFJDriZeT4e1IPfAJB_zMYT4>
- OTS Bitcoin block: `948161`

## Release assets

Expected release assets:

```text
core-object-alpha-shenzhen-notary-2026-05-06-arweave-payload.zip
core-object-alpha-shenzhen-notary-2026-05-06-github-release-backup-manifest.json
core-object-alpha-shenzhen-notary-2026-05-06-release-assets.sha256
core-object-alpha-shenzhen-notary-2026-05-06-release-notes.md
```

## Verification

```bash
python scripts/verify_shenzhen_notary_release_backup.py \
  --repo thechurchofagi/trinity-accord \
  --tag core-object-alpha-shenzhen-notary-arweave-backup-v1
```

Expected:

```text
PASS: GitHub Release backup is valid.
```

## Boundary

This GitHub Release is a verified availability mirror of the Arweave archive.

It is non-amending.

Bitcoin Originals and the original Arweave archive records prevail.

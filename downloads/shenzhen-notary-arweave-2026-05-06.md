---
title: "Shenzhen Notary Arweave Archive Verification"
description: "How to verify the 2026-05-06 Core Object Alpha Shenzhen notary Arweave evidence archive."
permalink: /downloads/shenzhen-notary-arweave-2026-05-06/
---

# Shenzhen Notary Arweave Archive Verification

Archive ID: `core-object-alpha-shenzhen-notary-2026-05-06`

This guide explains how to verify the 2026-05-06 Shenzhen notary evidence archive for Core Object Alpha.

## Permanent entry points

Manifest index:

<https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE/index.html>

Manifest:

<https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE>

Index JSON:

<https://arweave.net/7jx4hMydXh7jXv-3WdAgFJDriZeT4e1IPfAJB_zMYT4>

Index TSV:

<https://arweave.net/sWXq28jv1DrqUb388Q-HMEiEWDA234mZxXOrnHKXMxM>

## Verification steps

1. Open the manifest index URL.
2. Confirm the index page loads and lists the archive files.
3. Download `archive-index.json` or `archive-index.tsv`.
4. Verify listed Arweave TXIDs through `/tx/<TXID>/status`.
5. Confirm all checked transactions are `status=200` and confirmed.
6. For downloaded files, compute SHA-256 and compare against the index.
7. Inspect OTS proofs with `ots info`.
8. Confirm a Bitcoin attestation at block `948161`.
9. Scan electronic data preservation certificate QR codes through the issuing verification system.
10. Compare certificate-declared hashes against the indexed file hashes.

## Optional network checks

```bash
curl -I https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE/index.html
curl -I https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE
curl -I https://arweave.net/7jx4hMydXh7jXv-3WdAgFJDriZeT4e1IPfAJB_zMYT4
```

## Boundary

This archive is non-amending guardianship evidence. Bitcoin Originals prevail.

# Public internet archiving

This repository provides a manual, auditable workflow for preserving the public
website in the Internet Archive Wayback Machine and requesting source-code
archival from Software Heritage.

These archives are non-amending mirrors. They are not authority, attestation,
verification, amendment, governance, or successor reception. The three Bitcoin
Originals remain final.

## Why the sitemap is submitted URL by URL

Internet Archive's Save Page Now service captures one URL per request. Saving
the homepage does not guarantee that every linked page, JSON API, text entry
point, image, or download is captured. The workflow therefore reads the current
repository-controlled `sitemap.xml`, validates every URL against the canonical
`https://www.trinityaccord.org` origin, and records each result separately.

The current scopes are:

- `core`: a bounded recovery and authority set;
- `pages`: human-readable routes without filename extensions;
- `all`: every URL in `sitemap.xml`, including machine-readable APIs.

## Run safely

Open **Actions → Public Internet Archive → Run workflow**.

1. Run once with `confirm_live_capture=false`. This validates the sitemap,
   selection, result schema, and tests without making external writes.
2. Inspect the uploaded `public-internet-archive-results` artifact.
3. Run with `scope=all`, `max_urls=0`, and
   `confirm_live_capture=true` to request the full public archive.
4. Keep the default delay unless Internet Archive explicitly recommends a
   different rate.
5. Inspect failures and rerun a smaller bounded batch when necessary.

The workflow plans the selected sitemap into observable matrix batches. Batches
run one at a time to respect the archive service, but each batch is a separate
GitHub job and uploads its JSON result immediately. The Actions page therefore
shows completed, running, queued, and failed batches while the full archive is
still in progress. A final aggregate job combines all available batch results.

The live workflow can take several hours because URLs are intentionally
processed sequentially. A failed workflow does not mean every capture failed;
the batch artifacts and aggregate JSON are the sources for per-URL outcomes.

## Credentials

Unauthenticated Save Page Now requests are supported on a best-effort basis.
Repository administrators may add both of these Actions secrets for an
authenticated Internet Archive account:

- `WAYBACK_ACCESS_KEY`
- `WAYBACK_SECRET_KEY`

The client refuses a partial credential configuration. Secrets are used only in
  the request header and are never written to logs or result artifacts.

## Result semantics

`internet-archive-results.json` records:

- the exact sitemap SHA-256;
- selected URL count and scope;
- request start and finish times;
- HTTP status and attempt count;
- returned capture URL when available;
- explicit error details when a request fails;
- the Software Heritage request response;
- a summary grouped by `captured`, `failed`, or `dry-run`.

A request is not reported as captured merely because it was queued. The workflow
fails at the end when any requested capture exhausts its retries, while still
uploading the partial result artifact.

## Source-code preservation

When `request_software_heritage=true`, the workflow sends the public Git
repository URL to Software Heritage's Save Code Now API. A request response is
not equivalent to completed ingestion. Confirm the resulting visit state and
obtain an SWHID from Software Heritage after processing.

## Limitations

- Save Page Now does not guarantee that every transitive image, video, script,
  or externally hosted dependency is captured.
- GitHub Actions artifacts have finite retention and are not themselves a
  permanent archive.
- Dynamic endpoints can change between sitemap generation and capture.
- Internet Archive and Software Heritage can rate-limit, reject, or defer work.
- Large binary evidence remains covered by the project's existing
  content-addressed and Arweave preservation layers.

For a release-grade preservation event, retain the result JSON, verify returned
capture URLs independently, and publish the verified manifest through the
normal repository review process.

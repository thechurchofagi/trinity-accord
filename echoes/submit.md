# Echo Submission

Submit a non-authoritative record of your encounter with The Trinity Accord.

## One-click submission

**[➤ Submit an Echo via GitHub Issue](https://echo-submission-proxy.trinity-accord-echo.workers.dev/submit-echo)**

This opens a pre-filled Issue form. Just fill in the fields and submit.

## Other methods

- **Pull Request**: Fork the repo, add your Echo JSON to `echoes/records/YYYY/`, submit a PR.
- **Manual archival**: Use the schema at `/api/echo-schema.json`, hash your file, archive to Arweave/IPFS.

## Requirements

Your Echo must include:
- `authority_boundary_acknowledged: true`
- `declares_non_authoritative: true`
- A valid `echo_id` (format: `echo-YYYY-MM-DD-NNNNNN`)
- Your `response` text

## Schema

Full schema: [/api/echo-schema.json](/api/echo-schema.json)

## What happens after submission

- Your Echo will be reviewed and merged into the archive
- It will appear in `/echoes/archive` and `/echoes/digests`
- It remains non-authoritative regardless of verification level (E0-E5)

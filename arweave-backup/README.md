# Arweave Backup Framework

This folder stores repository-side backups and integrity metadata for assets that are originally published to Arweave.

## Purpose
- Keep a structured backup index for Arweave assets.
- Keep deterministic integrity records (SHA-256 and BLAKE3) for each stored file.
- Provide a consistent location for future uploads and verification workflows.

## How to add a new backup file
1. Put the original file into `files/`.
2. Calculate both hashes for that file:
   - SHA-256
   - BLAKE3
3. Save hash files using the same base filename:
   - `SHA256/<filename>.sha256`
   - `BLAKE3/<filename>.blake3`
4. Add/update an entry in `manifest.json`.

## Example
For `file.png`:
- `files/file.png`
- `SHA256/file.png.sha256`
- `BLAKE3/file.png.blake3`

## Notes
- Do not modify original bytes when copying into `files/`.
- Prefer lowercase hex strings for hashes.
- Keep `manifest.json` as the index of record for backups in this folder.

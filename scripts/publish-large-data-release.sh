#!/usr/bin/env bash
set -euo pipefail

RELEASE_TAG="${RELEASE_TAG:-signed-large-data-mirror-v1}"
MIN_SIZE_MB="${MIN_SIZE_MB:-10}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required to publish the release." >&2
  exit 1
fi

node scripts/build-large-data-release-manifest.mjs \
  --release-tag "$RELEASE_TAG" \
  --min-size-mb "$MIN_SIZE_MB"

gh release create "$RELEASE_TAG" \
  --title "Trinity Accord Signed Large Data Mirror v1" \
  --notes-file RELEASE-LARGE-DATA-MANIFEST.md || true

gh release upload "$RELEASE_TAG" RELEASE-LARGE-DATA-MANIFEST.json --clobber
gh release upload "$RELEASE_TAG" RELEASE-LARGE-DATA-MANIFEST.md --clobber

node - <<'NODE'
const fs = require("fs");
const cp = require("child_process");
const path = require("path");

const m = JSON.parse(fs.readFileSync("RELEASE-LARGE-DATA-MANIFEST.json", "utf8"));

for (const a of m.assets) {
  if (!a.source_path_exists) throw new Error(`source missing: ${a.logical_path}`);

  let uploadPath = a.logical_path;
  const base = path.basename(a.logical_path);

  if (base !== a.asset_name) {
    fs.mkdirSync(".cache/release-upload", {recursive: true});
    uploadPath = path.join(".cache/release-upload", a.asset_name);
    fs.copyFileSync(a.logical_path, uploadPath);
  }

  console.log(`Uploading ${uploadPath}`);
  cp.execFileSync("gh", ["release", "upload", m.release_tag, uploadPath, "--clobber"], {stdio: "inherit"});
}
NODE

echo "Release publish complete: $RELEASE_TAG"

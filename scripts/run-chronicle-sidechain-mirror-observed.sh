#!/usr/bin/env bash
set -Eeuo pipefail

OUT="${CHRONICLE_OUT:-artifacts/chronicle-sidechain-scan}"
RUNTIME_DIR="$OUT/runtime"
LOG_FILE="$RUNTIME_DIR/scanner.log"
HEARTBEAT_FILE="$RUNTIME_DIR/HEARTBEAT.json"
FINAL_FILE="$RUNTIME_DIR/FINAL-DIAGNOSTICS.json"
STATUS_FILE="$RUNTIME_DIR/FINAL-STATUS.txt"
HEARTBEAT_SECONDS="${CHRONICLE_HEARTBEAT_SECONDS:-60}"
STALL_WARN_SECONDS="${CHRONICLE_STALL_WARN_SECONDS:-300}"
START_EPOCH="$(date +%s)"
START_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HEARTBEAT_PID=""

mkdir -p "$RUNTIME_DIR"
: > "$LOG_FILE"

count_files() {
  local pattern="$1"
  find "$OUT" -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' '
}

snapshot_metrics() {
  local now elapsed discovery_pages recovered_records normalized_metadata media_files total_files bytes latest_file
  now="$(date +%s)"
  elapsed="$((now - START_EPOCH))"
  discovery_pages="$(count_files '*-page-*.json')"
  recovered_records="$(count_files 'record.json')"
  normalized_metadata="$(count_files 'metadata.normalized.json')"
  media_files="$(find "$OUT" -type f -name 'media-*' 2>/dev/null | wc -l | tr -d ' ')"
  total_files="$(find "$OUT" -type f 2>/dev/null | wc -l | tr -d ' ')"
  bytes="$(du -sb "$OUT" 2>/dev/null | awk '{print $1}' || echo 0)"
  latest_file="$(find "$OUT" -type f ! -path "$RUNTIME_DIR/*" -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2- || true)"

  export HB_NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  export HB_ELAPSED="$elapsed"
  export HB_DISCOVERY="$discovery_pages"
  export HB_RECORDS="$recovered_records"
  export HB_METADATA="$normalized_metadata"
  export HB_MEDIA="$media_files"
  export HB_TOTAL="$total_files"
  export HB_BYTES="$bytes"
  export HB_LATEST="$latest_file"

  python3 - "$HEARTBEAT_FILE.tmp" <<'PY'
import json, os, sys
p=sys.argv[1]
data={
  "timestamp": os.environ["HB_NOW_ISO"],
  "elapsed_seconds": int(os.environ["HB_ELAPSED"]),
  "discovery_pages": int(os.environ["HB_DISCOVERY"]),
  "recovered_records": int(os.environ["HB_RECORDS"]),
  "normalized_metadata": int(os.environ["HB_METADATA"]),
  "media_files": int(os.environ["HB_MEDIA"]),
  "total_files": int(os.environ["HB_TOTAL"]),
  "bytes_on_disk": int(os.environ["HB_BYTES"] or 0),
  "latest_non_runtime_file": os.environ.get("HB_LATEST") or None,
}
with open(p,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
    f.write("\n")
PY
  mv "$HEARTBEAT_FILE.tmp" "$HEARTBEAT_FILE"

  printf '[HEARTBEAT] %s elapsed=%ss discovery_pages=%s recovered_records=%s metadata=%s media_files=%s total_files=%s bytes=%s latest=%s\n' \
    "$HB_NOW_ISO" "$elapsed" "$discovery_pages" "$recovered_records" "$normalized_metadata" "$media_files" "$total_files" "$bytes" "${latest_file:-none}"

  printf '%s|%s|%s|%s|%s|%s' "$discovery_pages" "$recovered_records" "$normalized_metadata" "$media_files" "$total_files" "$bytes"
}

preflight() {
  echo '=== Chronicle sidechain mirror preflight ==='
  echo "Target address: ${CHRONICLE_ADDRESS:-0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8}"
  echo "Heartbeat interval: ${HEARTBEAT_SECONDS}s"
  echo "Stall warning threshold: ${STALL_WARN_SECONDS}s"
  echo "Output directory: $OUT"
  node --version
  python3 --version

  local polygon_rpc="${POLYGON_RPC_URL:-https://polygon.drpc.org}"
  local base_rpc="${BASE_RPC_URL:-https://mainnet.base.org}"
  local code

  for spec in \
    'Polygon Blockscout|https://polygon.blockscout.com/api/v2/stats' \
    'Base Blockscout|https://base.blockscout.com/api/v2/stats'; do
    IFS='|' read -r label url <<<"$spec"
    code="$(curl -L -sS -o /dev/null -w '%{http_code}' --connect-timeout 10 --max-time 25 "$url" || true)"
    if [[ "$code" == 2* || "$code" == 3* ]]; then
      echo "[PREFLIGHT OK] $label HTTP $code"
    else
      echo "[PREFLIGHT WARN] $label HTTP ${code:-transport-error}; scanner retries/fallback will decide final outcome"
    fi
  done

  check_rpc() {
    local label="$1" url="$2" expected="$3" body chain_id
    body="$(curl -sS --connect-timeout 10 --max-time 25 -H 'content-type: application/json' \
      --data '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' "$url" || true)"
    chain_id="$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("result", ""))' <<<"$body" 2>/dev/null || true)"
    if [[ "$chain_id" == "$expected" ]]; then
      echo "[PREFLIGHT OK] $label eth_chainId=$chain_id"
    else
      echo "[PREFLIGHT WARN] $label eth_chainId=${chain_id:-unreadable}, expected=$expected; tokenURI reads may fail"
    fi
  }

  check_rpc 'Polygon RPC' "$polygon_rpc" '0x89'
  check_rpc 'Base RPC' "$base_rpc" '0x2105'
  echo '=== Preflight complete ==='
}

heartbeat_loop() {
  local previous_signature="" unchanged_seconds=0 current signature
  while true; do
    sleep "$HEARTBEAT_SECONDS"
    current="$(snapshot_metrics)"
    signature="${current##*$'\n'}"
    if [[ "$signature" == "$previous_signature" ]]; then
      unchanged_seconds="$((unchanged_seconds + HEARTBEAT_SECONDS))"
    else
      unchanged_seconds=0
      previous_signature="$signature"
    fi
    if (( unchanged_seconds >= STALL_WARN_SECONDS )); then
      echo "[STALL WARNING] no observable artifact-count/size progress for ${unchanged_seconds}s; process is still alive but may be retrying or waiting on a remote endpoint"
      unchanged_seconds=0
    fi
  done
}

finalize() {
  local rc=$?
  set +e
  if [[ -n "$HEARTBEAT_PID" ]]; then
    kill "$HEARTBEAT_PID" >/dev/null 2>&1 || true
    wait "$HEARTBEAT_PID" >/dev/null 2>&1 || true
  fi

  snapshot_metrics >/dev/null 2>&1 || true
  local end_epoch elapsed status summary_exists manifest_exists
  end_epoch="$(date +%s)"
  elapsed="$((end_epoch - START_EPOCH))"
  status='success'
  if (( rc != 0 )); then status='failure'; fi
  summary_exists=false; [[ -s "$OUT/SUMMARY.json" ]] && summary_exists=true
  manifest_exists=false; [[ -s "$OUT/MANIFEST.sha256" && -s "$OUT/MANIFEST.sha256.json" ]] && manifest_exists=true

  export FINAL_STATUS="$status"
  export FINAL_EXIT="$rc"
  export FINAL_STARTED="$START_ISO"
  export FINAL_ENDED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  export FINAL_ELAPSED="$elapsed"
  export FINAL_SUMMARY="$summary_exists"
  export FINAL_MANIFEST="$manifest_exists"
  export FINAL_HEARTBEAT="$HEARTBEAT_FILE"

  python3 - "$FINAL_FILE" <<'PY'
import json, os, sys
p=sys.argv[1]
data={
  "status": os.environ["FINAL_STATUS"],
  "scanner_exit_code": int(os.environ["FINAL_EXIT"]),
  "started_at": os.environ["FINAL_STARTED"],
  "ended_at": os.environ["FINAL_ENDED"],
  "elapsed_seconds": int(os.environ["FINAL_ELAPSED"]),
  "summary_exists": os.environ["FINAL_SUMMARY"] == "true",
  "manifests_exist": os.environ["FINAL_MANIFEST"] == "true",
  "heartbeat_file": os.environ["FINAL_HEARTBEAT"],
}
try:
    with open(os.environ["FINAL_HEARTBEAT"],encoding="utf-8") as f:
        data["last_heartbeat"] = json.load(f)
except Exception as e:
    data["last_heartbeat_error"] = str(e)
with open(p,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
    f.write("\n")
PY

  printf '%s exit_code=%s elapsed_seconds=%s\n' "$status" "$rc" "$elapsed" > "$STATUS_FILE"
  echo "=== FINAL STATUS: ${status^^} | scanner_exit_code=$rc | elapsed=${elapsed}s | summary=$summary_exists | manifests=$manifest_exists ==="
  echo "Diagnostics: $FINAL_FILE"
  echo "Scanner log: $LOG_FILE"
  return 0
}
trap finalize EXIT

preflight
snapshot_metrics >/dev/null
heartbeat_loop &
HEARTBEAT_PID=$!

echo '=== Starting Chronicle Polygon + Base scanner ==='
set +e
node scripts/discover-chronicle-sidechain-nfts.mjs 2>&1 | tee "$LOG_FILE"
SCANNER_RC=${PIPESTATUS[0]}
set -e

echo "=== Scanner process exited with code $SCANNER_RC ==="
exit "$SCANNER_RC"

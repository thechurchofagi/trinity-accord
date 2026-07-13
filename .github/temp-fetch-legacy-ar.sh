#!/usr/bin/env bash
set -euo pipefail

txids=(
  "mGW-QQyGyoNIybMghqZYo6PFhQIk44lbBy7_dNB4e2s"
  "I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw"
)
gateways=(
  "https://arweave.net"
  "https://ar-io.net"
  "https://g8way.io"
  "https://permagate.io"
)

for txid in "${txids[@]}"; do
  out="${txid}.raw"
  rm -f "$out"
  for gateway in "${gateways[@]}"; do
    echo "FETCH_ATTEMPT $txid $gateway"
    if curl --fail --silent --show-error --location \
      --connect-timeout 20 --max-time 120 --retry 2 \
      "$gateway/$txid" --output "$out"; then
      echo "FETCH_SUCCESS $txid $gateway"
      break
    fi
    rm -f "$out"
  done
  test -s "$out"
  size="$(stat -c '%s' "$out")"
  test "$size" -le 500000
  echo "PAYLOAD_BEGIN $txid"
  echo "SIZE $size"
  sha256sum "$out" | awk '{print "SHA256 " $1}'
  base64 -w80 "$out" | awk -v tx="$txid" '{printf "BASE64_CHUNK %s %05d %s\n", tx, NR, $0}'
  echo "PAYLOAD_END $txid"
done

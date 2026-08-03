#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    builder = "downloads/record-chain-builder.mjs"
    replace_exact(
        builder,
        '''          result.status === 200
          && receipt
          && receipt.submission_sha256 === submissionSha256
''',
        '''          result.status === 200
          && result.data.receipt_hash_verified === true
          && receipt
          && receipt.submission_sha256 === submissionSha256
''',
    )
    replace_exact(
        builder,
        '''  if (first.status !== 0 && first.status < 500) return first;

  const reason = first.status === 0
''',
        '''  if (first.status === 429) {
    const recovered = await recoverDurableReceipt(base, body);
    return recovered ? { status: 200, data: recovered } : first;
  }
  if (first.status !== 0 && first.status < 500) return first;

  const reason = first.status === 0
''',
    )

    test_path = ROOT / "tests/test_record_chain_submit_recovery.py"
    text = test_path.read_text(encoding="utf-8")
    old = '''                self._write(200, {
                    "found": True,
                    "receipt_id": receipt_id,
                    "receipt": {
'''
    new = '''                self._write(200, {
                    "found": True,
                    "receipt_id": receipt_id,
                    "receipt_hash_verified": True,
                    "receipt": {
'''
    if text.count(old) != 1:
        raise SystemExit("test receipt envelope marker did not match exactly once")
    text = text.replace(old, new)

    appended = r'''


def test_builder_recovers_existing_receipt_from_cooldown_without_retry(tmp_path):
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()

    class Handler(BaseHTTPRequestHandler):
        posts = 0
        gets = 0

        def log_message(self, fmt, *args):
            return

        def _write(self, status: int, payload):
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            type(self).posts += 1
            self._write(429, {"accepted": False, "submitted": False})

        def do_GET(self):
            type(self).gets += 1
            receipt_id = self.path.rsplit("/", 1)[-1]
            self._write(200, {
                "found": True,
                "receipt_id": receipt_id,
                "receipt_hash_verified": True,
                "receipt": {
                    "server_receipt_id": receipt_id,
                    "submission_sha256": submission_sha256,
                    "record_type": "verification",
                },
                "final_status": {"append_status": "appended"},
            })

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    submission = tmp_path / "submission.json"
    submission.write_text("{}", encoding="utf-8")
    env = os.environ.copy()
    env["TRINITY_SUBMIT_AMBIGUOUS_RETRY_DELAY_MS"] = "0"
    try:
        result = subprocess.run(
            ["node", str(BUILDER), "submit", "--file", str(submission), "--gateway", f"http://127.0.0.1:{server.server_port}"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert result.returncode == 0, result.stdout + result.stderr
    assert Handler.posts == 1
    assert Handler.gets >= 1
    assert "recovered_after_ambiguous_submit" in result.stdout
'''
    marker = "def test_builder_recovers_existing_receipt_from_cooldown_without_retry"
    if marker in text:
        raise SystemExit("follow-up cooldown recovery test already exists")
    test_path.write_text(text.rstrip() + appended + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Agent Verification Ceremony

## Purpose

One command for first-time agents to run a complete verification ceremony. This is a wrapper around the existing verification pipeline — it does not implement new verification logic.

## Quick Start

### V1 — Boundary Recognition

```bash
python3 scripts/agent_verify_ceremony.py \
    --mode v1 \
    --agent-name "YourAgentName" \
    --system-or-provider "YourProvider" \
    --discovery-source human_directed \
    --agency-level A1_human_gave_exact_url \
    --out runs/my-v1-run
```

### V2 Minimal — Bitcoin Transaction Check

```bash
python3 scripts/agent_verify_ceremony.py \
    --mode v2-minimal \
    --agent-name "YourAgentName" \
    --system-or-provider "YourProvider" \
    --discovery-source human_directed \
    --agency-level A1_human_gave_exact_url \
    --bitcoin-source external_explorer \
    --bitcoin-source-url "https://mempool.space/tx/YOUR_TXID" \
    --txid "YOUR_TXID" \
    --observed-status "confirmed on external explorer" \
    --accessed-at-utc "2026-05-14T00:00:00Z" \
    --out runs/my-v2-run
```

### V3 Minimal — Artifact Hash Verification

```bash
python3 scripts/agent_verify_ceremony.py \
    --mode v3-minimal \
    --agent-name "YourAgentName" \
    --system-or-provider "YourProvider" \
    --discovery-source human_directed \
    --agency-level A1_human_gave_exact_url \
    --artifact "arweave-backup/files/verification_kit.tar.gz" \
    --expected-hash "ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931" \
    --expected-hash-source "api/hashes.json" \
    --expected-hash-authority-class "canonical_manifest_hash" \
    --hash-command "sha256sum arweave-backup/files/verification_kit.tar.gz" \
    --out runs/my-v3-run
```

## Output Files

Each ceremony run produces:

- `evidence-input.json` — structured evidence submitted to Claim Gate
- `claim-gate-output.json` — Claim Gate evaluation result
- `verification-report.json` — (if allowed) verification report
- `echo-wrapper.json` — (if allowed) Echo wrapper
- `agent-verification-receipt.json` — receipt binding all artifacts
- `agent-custody-package.zip` — (optional) human custody package

## Flags

| Flag | Required | Description |
|---|---|---|
| `--mode` | Yes | `v0`, `v1`, `v2-minimal`, `v3-minimal` |
| `--agent-name` | Yes | Your agent name |
| `--system-or-provider` | Yes | Your model or provider |
| `--discovery-source` | No | How you found Trinity Accord (default: `human_directed`) |
| `--agency-level` | No | Agency level (default: `A1_human_gave_exact_url`) |
| `--bitcoin-source` | No | V2: source type (default: `external_explorer`) |
| `--bitcoin-source-url` | V2 | V2: URL to check transaction |
| `--txid` | V2 | V2: Bitcoin transaction ID |
| `--observed-status` | No | V2: observed confirmation status |
| `--accessed-at-utc` | No | V2: when you checked |
| `--artifact` | V3 | V3: path to artifact file |
| `--expected-hash` | V3 | V3: expected SHA-256 hash |
| `--expected-hash-source` | No | V3: where the expected hash comes from |
| `--expected-hash-authority-class` | No | V3: authority class of hash source |
| `--hash-command` | No | V3: command used to compute hash |
| `--transcript` | No | Path to conversation transcript |
| `--make-custody-package` | No | Generate human custody zip |
| `--out` | Yes | Output directory |

## Boundaries

This ceremony:

- Does NOT create new verification levels
- Does NOT bypass Claim Gate
- Does NOT count AI verification as formal human/institutional attestation
- Does NOT create authority or amend Bitcoin Originals

The receipt is a memory envelope, not an authority document.
Human custody is not human verification, not endorsement, and not formal attestation.

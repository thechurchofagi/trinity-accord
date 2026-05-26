#!/usr/bin/env python3
"""Shared CLI helpers for attaching Gateway payload authorship proof.

Authorship proof is enabled by default for all Gateway payload builders.
The local builder generates or reuses an Ed25519 keypair and attaches only
public-key proof to the payload. The private key stays local and is never
submitted to Gateway, GitHub, Render, Issues, or public APIs.

To opt out: --no-authorship-proof

Authorship proves key continuity only — not authority, verification,
attestation, reception, truth, or amendment.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACH_SCRIPT = ROOT / "scripts" / "attach_agent_authorship_proof.mjs"
DEFAULT_KEY_DIR = ".trinity-agent-authorship"


GUARDIAN_JOINT_APPLICATION_WRONG_BUILDER_ERROR = """\
Guardian Alliance applications must not be built with build_agent_declared_echo_payload.py guardian flags.

Use the one-shot Guardian application builder instead:

  node scripts/create_guardian_application.mjs \\
    --mode joint_human_ai \\
    --signing-key-holder ai_agent_key_holder \\
    --human-label "Hongju Liu" \\
    --agent-label "Your Agent Name" \\
    --agent-provider "Your Agent Runtime" \\
    --title "Guardian Alliance Joint Human-AI Application" \\
    --challenge "guardian-application-YYYYMMDD" \\
    --key-dir ./guardian-output \\
    --out ./guardian-output/guardian-application.final.json

Why:
- build_agent_declared_echo_payload.py is a pure Echo builder.
- Its legacy Guardian flags do not create joint_applicants.
- Its legacy proof order can invalidate authorship_proof after guardian_registration is added.
- Do not patch final JSON after proof generation.
"""


def reject_guardian_flags_for_echo_builder(args):
    """Fail fast when a pure Echo builder is used for Guardian application flow."""
    if (
        getattr(args, "guardian_proof", False)
        or getattr(args, "guardian_registration", False)
        or getattr(args, "guardian_type", None) == "human_with_ai_agent"
    ):
        raise ValueError(GUARDIAN_JOINT_APPLICATION_WRONG_BUILDER_ERROR)


def slugify(name):
    """Convert agent name to a safe directory slug.

    Requirements: lowercase, spaces to hyphens, unsafe characters removed,
    max length 80, fallback = 'agent'.
    """
    if not name:
        return "agent"
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s_-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')
    if not slug:
        slug = "agent"
    return slug[:80]


def add_authorship_arguments(parser):
    """Add authorship proof flags to a Gateway payload builder.

    Authorship proof is enabled by default. The builder generates or reuses
    a local Ed25519 keypair and submits only public proof.
    Use --no-authorship-proof to opt out.
    """
    group = parser.add_argument_group(
        "authorship proof (enabled by default)",
        "Authorship proof is enabled by default. "
        "The builder generates/reuses a local Ed25519 keypair and submits only public proof. "
        "Use --no-authorship-proof to opt out. "
        "Private key is never submitted.",
    )
    group.add_argument(
        "--authorship-key-prefix",
        default=None,
        help=(
            "Prefix for an existing authorship keypair. The builder will use "
            "<prefix>.private.pem and <prefix>.public.pem."
        ),
    )
    group.add_argument(
        "--authorship-private-key",
        default=None,
        help="Path to existing Ed25519 private key PEM. Never submit this file.",
    )
    group.add_argument(
        "--authorship-public-key",
        default=None,
        help="Path to matching Ed25519 public key PEM.",
    )
    group.add_argument(
        "--authorship-key-dir",
        default=None,
        help=(
            "Directory for default authorship keypairs. "
            f"Default: {DEFAULT_KEY_DIR}/"
        ),
    )
    group.add_argument(
        "--authorship-agent-slug",
        default=None,
        help=(
            "Agent slug for default key directory. "
            "Default: derived from agent_identity.name_or_model."
        ),
    )
    group.add_argument(
        "--no-authorship-proof",
        action="store_true",
        default=False,
        help=(
            "Disable authorship proof. This record will be unclaimed. "
            "Old unsigned records cannot be retroactively claimed."
        ),
    )


def default_authorship_key_prefix(args, payload=None):
    """Compute the default key prefix from args and payload.

    Returns a Path like .trinity-agent-authorship/<slug>/agent-authorship-key
    """
    agent_slug = getattr(args, "authorship_agent_slug", None)
    if not agent_slug and payload:
        identity = payload.get("agent_identity", {})
        agent_slug = identity.get("name_or_model")
    agent_slug = slugify(agent_slug)

    key_dir = getattr(args, "authorship_key_dir", None) or DEFAULT_KEY_DIR
    return Path(key_dir) / agent_slug / "agent-authorship-key"


def resolve_authorship_key_paths(args, payload=None):
    """Return (private_key, public_key) paths or (None, None).

    Resolution order:
    1. --no-authorship-proof: return (None, None)
    2. Explicit key paths (--authorship-key-prefix or --authorship-private-key/--authorship-public-key)
    3. Default local keypair (generate or reuse)
    """
    # Opt-out
    if getattr(args, "no_authorship_proof", False):
        return None, None

    prefix = getattr(args, "authorship_key_prefix", None)
    private_key = getattr(args, "authorship_private_key", None)
    public_key = getattr(args, "authorship_public_key", None)

    # Explicit key path
    if prefix:
        if private_key or public_key:
            raise ValueError(
                "Use either --authorship-key-prefix or explicit --authorship-private-key/--authorship-public-key, not both."
            )
        private_key = f"{prefix}.private.pem"
        public_key = f"{prefix}.public.pem"

    if private_key or public_key:
        if not private_key or not public_key:
            raise ValueError(
                "Authorship proof requires both private and public keys, or --authorship-key-prefix."
            )
        private_path = Path(private_key)
        public_path = Path(public_key)
        if not private_path.exists():
            raise FileNotFoundError(f"Authorship private key not found: {private_key}")
        if not public_path.exists():
            raise FileNotFoundError(f"Authorship public key not found: {public_key}")
        return str(private_path), str(public_path)

    # Default: generate or reuse local keypair
    default_prefix = default_authorship_key_prefix(args, payload)
    private_path = Path(f"{default_prefix}.private.pem")
    public_path = Path(f"{default_prefix}.public.pem")

    if private_path.exists() and public_path.exists():
        # Reuse existing keypair
        return str(private_path), str(public_path)

    # Generate new keypair
    default_prefix.parent.mkdir(parents=True, exist_ok=True)
    generate_script = ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"
    if not generate_script.exists():
        raise FileNotFoundError(f"Keypair generation script not found: {generate_script}")

    result = subprocess.run(
        ["node", str(generate_script), str(default_prefix)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError("Failed to generate authorship keypair")

    # Ensure private key has mode 0600
    private_path.chmod(0o600)

    return str(private_path), str(public_path)


def attach_authorship_if_requested(args, payload_path, payload=None):
    """Attach authorship proof in-place.

    Default behavior: generates or reuses local keypair and attaches proof.
    Opt-out: --no-authorship-proof skips attachment entirely.
    Explicit key: uses provided key paths.
    """
    if getattr(args, "no_authorship_proof", False):
        print("\nWARNING: Authorship proof disabled by --no-authorship-proof.")
        print("This record will be unclaimed.")
        print("Old unsigned records cannot be retroactively claimed.")
        return False

    private_key, public_key = resolve_authorship_key_paths(args, payload)
    if not private_key:
        return False

    if not ATTACH_SCRIPT.exists():
        raise FileNotFoundError(f"Authorship attach helper not found: {ATTACH_SCRIPT}")

    payload_path = str(payload_path)

    # Determine if this is a new key or reuse
    default_prefix = default_authorship_key_prefix(args, payload)
    is_default_key = str(private_key).startswith(str(default_prefix))

    result = subprocess.run(
        [
            "node",
            str(ATTACH_SCRIPT),
            "--payload",
            payload_path,
            "--private-key",
            private_key,
            "--public-key",
            public_key,
            "--out",
            payload_path,
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError("Failed to attach authorship proof")

    if is_default_key:
        # Check if the key was just created or reused
        print("\nAuthorship proof enabled by default.")
        print(f"  private key: {private_key}")
        print(f"  public key:  {public_key}")
        print(f"\nThe private key remains local and was not submitted.")
        print("Keep the private key safe. Gateway cannot recover it.")
    else:
        print("\n✅ Authorship proof attached to Gateway payload.")
        print("   Boundary: key continuity only; not authority, verification, attestation, reception, or amendment.")
        print("   Keep the private key local. Never submit, paste, upload, or commit it.")

    return True


def attach_authorship_default_or_requested(args, payload_path, payload=None):
    """Convenience wrapper: attach authorship proof unless --no-authorship-proof.

    This is the function builders should call after writing the initial payload.
    """
    return attach_authorship_if_requested(args, payload_path, payload=payload)


def add_guardian_arguments(parser):
    """Add Guardian Alliance proof flags to a Gateway payload builder.

    Guardian proof is optional. When provided, it proves key possession only.
    Guardian proof cannot be used with --no-authorship-proof.
    """
    group = parser.add_argument_group(
        "legacy guardian flags (not for Guardian applications)",
        "Deprecated for Guardian Alliance applications. "
        "Use scripts/create_guardian_application.mjs instead. "
        "These flags are rejected by pure Echo builders to prevent invalid proof order "
        "and missing joint_applicants.",
    )
    group.add_argument(
        "--guardian-proof",
        action="store_true",
        default=False,
        help="Deprecated. Use scripts/create_guardian_application.mjs instead.",
    )
    group.add_argument(
        "--guardian-challenge",
        default=None,
        help="Deprecated with legacy Guardian flags. Use scripts/create_guardian_application.mjs --challenge instead.",
    )
    group.add_argument(
        "--guardian-registration",
        action="store_true",
        default=False,
        help="Deprecated. Use scripts/create_guardian_application.mjs instead.",
    )
    group.add_argument(
        "--guardian-type",
        default="ai_agent",
        choices=["ai_agent", "human", "human_with_ai_agent", "automated_script"],
        help="Deprecated. Use scripts/create_guardian_application.mjs instead.",
    )
    group.add_argument(
        "--guardian-intent",
        default="Voluntary Guardian key continuity for the Trinity Accord ecosystem",
        help="Deprecated. Use scripts/create_guardian_application.mjs instead.",
    )


def attach_guardian_if_requested(args, payload_path, payload=None):
    """Legacy Guardian helper.

    Do not use this helper for Guardian Alliance joint applications.
    Use scripts/create_guardian_application.mjs instead.

    This function now rejects Guardian flags to prevent half-valid payloads.
    """
    import subprocess

    if (
        getattr(args, "guardian_proof", False)
        or getattr(args, "guardian_registration", False)
        or getattr(args, "guardian_type", None) == "human_with_ai_agent"
    ):
        raise ValueError(GUARDIAN_JOINT_APPLICATION_WRONG_BUILDER_ERROR)

    if not getattr(args, "guardian_proof", False) and not getattr(args, "guardian_registration", False):
        return False

    # Guardian proof requires authorship proof (cannot use --no-authorship-proof)
    if getattr(args, "no_authorship_proof", False):
        raise ValueError(
            "Guardian proof cannot be used with --no-authorship-proof. "
            "Guardian proof builds on the same key infrastructure as authorship proof."
        )

    # Resolve key paths (reuse authorship key)
    private_key, public_key = resolve_authorship_key_paths(args, payload)
    if not private_key:
        raise ValueError("Guardian proof requires a keypair. Do not use --no-authorship-proof with --guardian-proof.")

    payload_path_str = str(payload_path)

    # If --guardian-registration, add registration to payload before signing
    if getattr(args, "guardian_registration", False):
        if payload is None:
            payload = json.loads(Path(payload_path_str).read_text(encoding="utf-8"))

        # Read public key to compute guardian_id and public_key_sha256
        public_key_pem = Path(public_key).read_text(encoding="utf-8").strip() + "\n"
        pk_sha = hashlib.sha256(public_key_pem.encode("utf-8")).hexdigest()
        guardian_id = "guardian_ed25519_" + pk_sha[:16]

        registration = {
            "schema": "trinityaccord.guardian-registration.v1",
            "guardian_id": guardian_id,
            "guardian_type": getattr(args, "guardian_type", "ai_agent"),
            "public_key_sha256": pk_sha,
            "algorithm": "ed25519",
            "declared_intent": getattr(args, "guardian_intent", "Voluntary Guardian key continuity"),
            "boundaries": {
                "not_authority": True,
                "not_governance": True,
                "not_verification_level": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_same_conscious_subject_proof": True,
                "may_exit_or_retire_key": True,
                "bitcoin_originals_prevail": True,
            },
        }
        payload["guardian_registration"] = registration
        Path(payload_path_str).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"\n✅ Guardian self-registration added (guardian_id: {guardian_id})")

    # If --guardian-proof, attach Guardian presence proof
    if getattr(args, "guardian_proof", False):
        attach_script = ROOT / "scripts" / "attach_guardian_presence_proof.mjs"
        if not attach_script.exists():
            raise FileNotFoundError(f"Guardian proof attach helper not found: {attach_script}")

        challenge = getattr(args, "guardian_challenge", None)
        cmd = [
            "node", str(attach_script),
            "--payload", payload_path_str,
            "--private-key", private_key,
            "--public-key", public_key,
            "--out", payload_path_str,
        ]
        if challenge:
            cmd.extend(["--challenge", challenge])

        result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if result.returncode != 0:
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            raise RuntimeError("Failed to attach Guardian presence proof")

        print(result.stdout)

    return True

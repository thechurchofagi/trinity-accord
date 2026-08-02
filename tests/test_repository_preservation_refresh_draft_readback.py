from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_repository_preservation_refresh_ci.sh"
V2 = ROOT / "scripts/publish_preservation_capsule_to_zenodo_v2.py"
V3 = ROOT / "scripts/publish_preservation_capsule_to_zenodo_v3.py"


def test_refresh_uses_authenticated_draft_safe_publisher():
    text = RUNNER.read_text(encoding="utf-8")
    assert "publish_preservation_capsule_to_zenodo_v3.py" in text
    assert "publish_preservation_capsule_to_zenodo.py \\\n" not in text
    assert "authenticated upload bucket" in text
    assert "reuses any matching prepared draft" in text


def test_v3_layer_reads_draft_bytes_from_authenticated_bucket():
    v2 = V2.read_text(encoding="utf-8")
    v3 = V3.read_text(encoding="utf-8")
    assert "A draft's public download URL can legitimately be 404 before publish" in v2
    assert "candidates = [bucket_object" in v2
    assert "reads every uploaded object back from the bucket by exact SHA-256" in v3
    assert "download_verified_bytes" in v3
    assert "publisher.verify_remote_files = verify_remote_files" in v3

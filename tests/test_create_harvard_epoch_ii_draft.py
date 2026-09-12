import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "scripts/create_harvard_epoch_ii_draft.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/create-harvard-epoch-ii-draft.yml").read_text(encoding="utf-8")
MARKER = (ROOT / ".github/harvard-epoch-ii-draft-create-authorized-v1").read_text(encoding="utf-8").strip()


def test_exact_one_shot_authorization_marker() -> None:
    assert MARKER == "Harvard Epoch II metadata-only draft creation authorized: 2026-09-12"
    assert MARKER in SOURCE


def test_write_boundary_excludes_upload_review_publish_and_old_dataset_writes() -> None:
    assert '"POST",\n            f"/api/dataverses/{COLLECTION}/datasets"' in SOURCE
    assert '"PUT",\n        f"/api/datasets/{dataset_id}/license"' in SOURCE
    assert "/add" not in SOURCE
    assert "uploadurls" not in SOURCE
    assert "submitForReview" not in SOURCE
    assert "/actions/:publish" not in SOURCE
    assert 'f"/api/datasets/{OLD_DATASET_ID}/license"' not in SOURCE


def test_draft_postconditions_and_workflow_secret_boundary() -> None:
    assert 'version.get("versionState") != "DRAFT"' in SOURCE
    assert 'if files:' in SOURCE
    assert '"files_uploaded": 0' in SOURCE
    assert '"submitted_for_review": False' in SOURCE
    assert "HD_API_TOKEN: ${{ secrets.HD }}" in WORKFLOW
    assert "github.event_name == 'push'" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW


def test_terms_hash_binds_exact_file_bytes() -> None:
    terms_path = ROOT / "preservation/epoch-ii/HARVARD-TERMS-OF-USE.txt"
    raw_sha = hashlib.sha256(terms_path.read_bytes()).hexdigest()
    normalized_sha = hashlib.sha256(
        terms_path.read_text(encoding="utf-8").strip().encode("utf-8")
    ).hexdigest()
    assert raw_sha == "881ee6b94f3fddaa53d66bcd5c64d6510a6fdf9ce0a7d61bca0ba72555dd361c"
    assert normalized_sha == "c553d988d4efa0cf08f6720d6891fb51d7b69682d12f633d1619ce0943be832f"
    assert raw_sha != normalized_sha
    assert "terms_bytes = terms_path.read_bytes()" in SOURCE

    spec = importlib.util.spec_from_file_location(
        "create_harvard_epoch_ii_draft", ROOT / "scripts/create_harvard_epoch_ii_draft.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    _, _, terms = module.load_inputs(ROOT)
    assert hashlib.sha256(terms.encode("utf-8")).hexdigest() == normalized_sha

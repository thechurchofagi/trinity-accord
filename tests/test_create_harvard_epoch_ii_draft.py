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

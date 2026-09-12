from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "scripts" / "harvard_hd_readonly_probe.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "harvard-hd-readonly-probe.yml").read_text(
    encoding="utf-8"
)


def load_probe_module():
    path = ROOT / "scripts" / "harvard_hd_readonly_probe.py"
    spec = importlib.util.spec_from_file_location("harvard_hd_readonly_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_probe_is_get_only_and_redacts_email() -> None:
    assert 'method="GET"' in SOURCE
    assert 'method="POST"' not in SOURCE
    assert 'method="PUT"' not in SOURCE
    assert 'method="DELETE"' not in SOURCE
    assert '"email_masked"' in SOURCE
    assert '"email": user.get("email")' not in SOURCE


def test_probe_reads_identity_permissions_and_dataset_quota() -> None:
    assert '"/api/users/:me"' in SOURCE
    assert '"/api/dataverses/harvard/userPermissions"' in SOURCE
    assert 'storage/quota?showInherited=true' in SOURCE
    assert 'storage/use' in SOURCE
    assert "23_107_006_729" in SOURCE


def test_storage_message_parsing_and_unknown_quota_semantics() -> None:
    module = load_probe_module()
    assert module.first_int({"message": "Total recorded size: 1,988,197,087 bytes"}) == 1_988_197_087
    assert module.first_int({"message": "No quota defined for this dataset"}) is None
    assert "None if quota_bytes is None" in SOURCE


def test_workflow_uses_only_hd_and_uploads_private_diagnostic_artifact() -> None:
    assert "HD_API_TOKEN: ${{ secrets.HD }}" in WORKFLOW
    assert "actions/upload-artifact@" in WORKFLOW
    assert "retention-days: 1" in WORKFLOW
    assert "submitForReview" not in WORKFLOW
    assert "publish" not in WORKFLOW.lower()

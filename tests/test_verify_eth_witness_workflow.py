from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/verify-eth-witness.yml"


def test_eth_verification_workflow_is_manual_and_fail_closed():
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger_header = source.split("permissions:", 1)[0]

    assert "workflow_dispatch:" in trigger_header
    assert "schedule:" not in trigger_header
    assert "repository_dispatch:" not in trigger_header
    assert "continue-on-error" not in source


def test_eth_workflow_executes_both_strict_l1_l2_l3_verifiers():
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py" in source
    assert "evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py" in source
    assert source.count("cmp --silent") == 2
    assert "'L1'" in source
    assert "'L2'" in source
    assert "'L3'" in source
    assert "'sidechain_scope_inferred': False" in source


def test_live_rpc_check_remains_reference_only_and_separate():
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "name: Verify strict Ethereum L1 L2 L3 annexes offline" in source
    assert "name: Run live RPC reference check" in source
    assert "ETH_RPC_URL: ${{ secrets.ETHEREUMMAINNET }}" in source
    assert source.index("Verify strict Ethereum L1 L2 L3 annexes offline") < source.index(
        "Run live RPC reference check"
    )

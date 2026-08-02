"""Executable Clause V2 application-sequence and settlement tests."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = str(ROOT / "contracts" / "clause_v2.py")


def _deploy_query(deploy, vm, owner):
    vm.warp("2026-07-16T12:00:00Z")
    vm.sender = owner
    contract = deploy(CONTRACT)
    query_id = contract.file_query(
        "Does the published policy permit commercial redistribution?",
        "https://example.com/policy",
    )
    return contract, int(query_id)


def _mock_review(vm):
    vm.mock_llm(
        r"Reply ONLY JSON with keys: outcome",
        json.dumps({
            "outcome": "met", "confidenceBps": 8400, "triggerBps": 8500,
            "summary": "The policy permits the stated use.",
            "rationale": "The governing clause expressly grants commercial redistribution.",
            "riskFlags": [],
        }),
    )


def _mock_ruling(vm, kind, ruling, revised):
    vm.mock_llm(
        rf"resolving .* {kind}",
        json.dumps({
            "ruling": ruling, "revisedOutcome": revised,
            "confidenceDeltaBps": -900 if revised == "not_met" else 700,
            "reason": "The filing supplies controlling policy evidence.", "riskFlags": [],
        }),
    )


def test_frontend_and_deploy_script_call_the_v2_review_then_finalize_sequence():
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    deploy_script = (ROOT / "scripts" / "deploy_only.py").read_text(encoding="utf-8")
    assert '"review_claim_with_genlayer", [String(id)]' in app
    assert '"finalize_query", [id]' in app
    assert '"contracts" / "clause_v2.py"' in deploy_script


def test_file_review_challenge_appeal_and_finalization_exact_application_path(
    deploy, direct_vm, direct_alice, direct_bob, direct_charlie
):
    contract, query_id = _deploy_query(deploy, direct_vm, direct_alice)
    _mock_review(direct_vm)
    assert contract.review_claim_with_genlayer(str(query_id)) == "met"
    query = contract.get_query(query_id)
    assert query["lifecycleStatus"] == "CHALLENGE_WINDOW"
    assert query["canFinalize"] is False

    with direct_vm.expect_revert("review_not_mature"):
        contract.finalize_query(query_id)

    direct_vm.sender = direct_bob
    challenge_id = contract.submit_challenge(
        str(query_id), "A restrictive exception controls.", "https://example.org/challenge"
    )
    direct_vm.sender = direct_alice
    _mock_ruling(direct_vm, "challenge", "accepted", "not_met")
    contract.resolve_challenge_with_genlayer(str(query_id), challenge_id)

    direct_vm.sender = direct_bob
    appeal_id = contract.submit_appeal(
        str(query_id), "The exception does not apply to this category.", "https://example.net/appeal"
    )
    direct_vm.sender = direct_alice
    _mock_ruling(direct_vm, "appeal", "granted", "met")
    contract.resolve_appeal_with_genlayer(str(query_id), appeal_id)

    direct_vm.warp("2026-07-16T14:00:01Z")
    direct_vm.sender = direct_charlie
    assert contract.finalize_query(query_id) == "FINALIZED"
    record = json.loads(contract.get_claim_record(str(query_id)))
    assert record["status"] == "RESOLVED"
    assert record["outcome"] == "met"
    assert record["challengeIds"] == [challenge_id]
    assert record["appealIds"] == [appeal_id]

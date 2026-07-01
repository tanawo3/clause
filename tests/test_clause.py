"""Direct-mode tests for CLAUSE.

These cover the deterministic surface: validation, boundaries, authorization,
duplicate prevention, invalid state transitions and reads after writes.

The non-deterministic rule() path (web.get + exec_prompt under the Equivalence
Principle) is exercised live on studionet via scripts/seed_data.py, because the
direct runner used here does not mock GenVM's leader/validator nondet flow.
Documented as an explicit limitation of the available local tooling.
"""
from pathlib import Path

CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "clause.py")
PENDING = 0; PERMITTED = 1; PROHIBITED = 2; UNCLEAR = 3
URL = "https://example.com/policy"


def test_file_query_success(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    qid = c.file_query("May I bring a guest to the coworking space?", URL)
    assert qid == 0
    q = c.get_query(0)
    assert q["status"] == PENDING
    assert q["policy_url"] == URL
    assert q["archived"] == 0
    assert q["passage"] == "" and q["rationale"] == ""


def test_empty_question_reverts(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("a question is required"):
        c.file_query("   ", URL)


def test_empty_url_reverts(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("a policy URL is required"):
        c.file_query("Is X allowed?", "  ")


def test_non_http_url_reverts(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("must be http"):
        c.file_query("Is X allowed?", "ftp://example.com/policy")


def test_question_max_boundary(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    ok = "a" * 240
    assert c.file_query(ok, URL) == 0          # 240 is allowed
    with direct_vm.expect_revert("exceeds 240"):
        c.file_query("b" * 241, URL)           # 241 is rejected


def test_url_max_boundary(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    long_url = "https://example.com/" + ("p" * 290)  # > 300
    with direct_vm.expect_revert("exceeds 300"):
        c.file_query("Is X allowed?", long_url)


def test_duplicate_prevention(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    c.file_query("Can I expense lunch?", URL)
    with direct_vm.expect_revert("already filed this exact query"):
        c.file_query("Can I expense lunch?", URL)


def test_same_question_different_asker_ok(deploy, direct_vm, direct_alice, direct_bob):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    c.file_query("Can I expense lunch?", URL)
    direct_vm.sender = direct_bob
    assert c.file_query("Can I expense lunch?", URL) == 1  # different asker -> allowed


def test_unauthorized_archive_reverts(deploy, direct_vm, direct_alice, direct_bob):
    # archive() checks ownership before anything else
    c = deploy(CONTRACT)
    owner = c.get_owner()
    non_owner = direct_bob if str(direct_alice).lower() == str(owner).lower() else direct_alice
    direct_vm.sender = non_owner
    with direct_vm.expect_revert("only the owner can archive"):
        c.archive(0)


def test_owner_can_archive_and_hide(deploy, direct_vm):
    # the deployer (current direct_vm.sender) is the owner
    c = deploy(CONTRACT)
    c.file_query("Is X allowed?", URL)
    c.archive(0)
    assert c.get_query(0)["archived"] == 1
    # archived queries drop out of stats
    assert c.get_stats()["total"] == 0


def test_no_such_query(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("no such query"):
        c.get_query(5)


def test_stats_and_read_after_write(deploy, direct_vm, direct_alice):
    c = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    c.file_query("Question one?", URL)
    c.file_query("Question two?", URL)
    s = c.get_stats()
    assert s["total"] == 2 and s["pending"] == 2
    assert c.get_query_count() == 2
    assert c.get_query(1)["question"] == "Question two?"

"""Seed CLAUSE with real grounded rulings on studionet.

Also serves as the integration test: it deploys-against an existing address,
performs writes (file_query, rule), waits for transaction completion inside
.transact(), and reads the updated on-chain state back.
"""
from pathlib import Path

from gltest_cli.config.general import get_general_config
from gltest_cli.config.user import load_user_config
from gltest import get_contract_factory, get_default_account

ROOT = Path(__file__).resolve().parents[1]
ADDR = "0x8f1Df72EBD74F8bB0d8a50f01A03396bec33a1dB"

cfg = load_user_config(str(ROOT / "gltest.config.yaml"))
get_general_config().user_config = cfg
factory = get_contract_factory(contract_file_path=str(ROOT / "contracts" / "clause.py"))
c = factory.build_contract(ADDR, account=get_default_account())

# Short, pure-text policy that fits entirely in the fetch window -> decisive rulings.
MIT = "https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/mit.txt"

# (question, policy_url, do_rule)
QUERIES = [
    ("May I use this software for commercial purposes?", MIT, True),
    ("Is it permitted to remove the copyright notice when redistributing the software?", MIT, True),
    ("May I sublicense this software to a third party?", MIT, True),
    ("Is overtime pay mandatory for salaried staff?", "https://example.com", True),
    ("May I distribute modified versions of this software?", MIT, False),
]

VERDICTS = ["PENDING", "PERMITTED", "PROHIBITED", "UNCLEAR"]


def main():
    if c.get_query_count().call() == 0:
        for (q, url, _) in QUERIES:
            c.file_query(args=[q, url]).transact()
            print("filed:", q[:48])

    for qid in range(c.get_query_count().call()):
        do = QUERIES[qid][2] if qid < len(QUERIES) else False
        item = c.get_query(args=[qid]).call()
        if do and int(item["status"]) == 0:
            print("ruling (AI):", item["question"][:44])
            try:
                c.rule(args=[qid]).transact()
            except Exception as e:
                print("  rule ->", e)

    print("stats:", c.get_stats().call())
    for qid in range(c.get_query_count().call()):
        item = c.get_query(args=[qid]).call()
        print(qid, VERDICTS[int(item["status"])], "|", item["question"][:40],
              "|", (item["passage"] or "")[:46])


if __name__ == "__main__":
    main()

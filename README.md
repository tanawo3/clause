# Clause

Policy questions with source-backed rule decisions.

Clause is a compact rule desk. Users file a policy query, attach official evidence and let GenLayer produce a final rule with challenge and appeal history.

## Review Links

| Surface | Link |
| --- | --- |
| Live app | https://clause-policy-review.vercel.app |
| GitHub | https://github.com/tanawo3/clause |
| Contract | https://explorer-studio.genlayer.com/address/0x7a7Cf4eaD9e577e2061628e348A6b16524dA8AA4 |

## Chain Record

- Network: GenLayer Studionet
- Chain ID: 61999
- Contract: `0x7a7Cf4eaD9e577e2061628e348A6b16524dA8AA4`
- Deploy transaction: [0x259cd441...b2d4d5](https://explorer-studio.genlayer.com/tx/0x259cd441efe0bd583f19c5580c51cb6462f559498182150b0b81627969b2d4d5)
- Deployed: `2026-08-02T20:56:37.930Z`
- Source: `contracts/clause_v2.py` (65,543 bytes)
- Source SHA-256: `991bc013f829f783457d2abbab6b96d8c755e2121328040793190cdc074ec30a`

## Protocol Path

1. File a query and attach official sources.
2. Route the new record through `review_claim_with_genlayer`.
3. Open the mandatory challenge period after the provisional ruling.
4. Resolve challenges and appeals without bypassing either window.
5. Call `finalize_query` only when the contract reports the record is finalizable.

The frontend reads query records, source evidence, rule status and stats. Contract state is public; write actions still require a connected wallet on GenLayer Studionet.

## Verification

`tests/test_clause.py` contains the exact application sequence requested in review: file, review, challenge, resolve, appeal, resolve, wait, finalize. It also checks that the frontend calls the canonical methods. The suite passes 2/2.

## Local Run

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Release Hygiene

The public package is static and has no install step. Vercel receives only frontend, contract source and public deployment metadata.

Keep wallet private keys, vault exports, `.env` files, Vercel project state and dashboard data out of Git. This repository is for public source, UI, tests and deployment receipts only.

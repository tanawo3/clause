# Clause

Policy questions with source-backed rule decisions.

Clause is a compact rule desk. Users file a policy query, attach official evidence and let GenLayer produce a final rule with challenge and appeal history.

## Review Links

| Surface | Link |
| --- | --- |
| Live app | https://assmore22-clause.vercel.app |
| GitHub | https://github.com/assmore22/clause |
| Contract | https://explorer-studio.genlayer.com/address/0x43D229F781dC44758A45FB683c4c785500769010 |

## Chain Record

- Network: GenLayer Studionet
- Chain ID: 61999
- Contract: `0x43D229F781dC44758A45FB683c4c785500769010`
- Deploy transaction: [0x8eaeaac2...f3b722](https://explorer-studio.genlayer.com/tx/0x8eaeaac25d8269773241fcb37479b6b7b58b3bfade794602dc6dbbe404f3b722)
- Deployed: `2026-06-24T03:25:12.781Z`
- Source: `contracts/clause_v2.py` (60,079 bytes)

## Protocol Path

1. File a query.
2. Attach official sources.
3. Run GenLayer rule review.
4. Challenge or appeal.
5. Finalize the rule.

The frontend reads query records, source evidence, rule status and stats. Contract state is public; write actions still require a connected wallet on GenLayer Studionet.

## Finalized Smoke

| Action | Transaction |
| --- | --- |
| `set_claim_standard` | [0x395e8d5d...be8145](https://explorer-studio.genlayer.com/tx/0x395e8d5dfebeda0801276fa1150aebad6960742205861565acaf8fe213be8145) |
| `file_query` | [0x08c7cbd6...2f8f70](https://explorer-studio.genlayer.com/tx/0x08c7cbd6da5ca6b283a9f3fa8c02323e5c6d51fb3907e07197dc5dee4e2f8f70) |
| `add_obligation` | [0x41c97ba0...0e68c1](https://explorer-studio.genlayer.com/tx/0x41c97ba0a50729bcef127c7222fbaa228e0a94f6a4cccced542ffa124b0e68c1) |
| `add_evidence_docs` | [0x270421b6...956846](https://explorer-studio.genlayer.com/tx/0x270421b6604b5ba8d7136c0f32b68ce72d6e713fae2d8b8d1ffabc7a75956846) |
| `add_evidence_web` | [0xf86c265a...b2932b](https://explorer-studio.genlayer.com/tx/0xf86c265a23c33441c4a00744563077762406969e0ad99ee1c5c12fd064b2932b) |
| `open_review` | [0xf358f620...d21c5e](https://explorer-studio.genlayer.com/tx/0xf358f62061b33a78f8b44679c7607fab54dba9fc17e87fda1441df4304d21c5e) |

## Local Run

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Release Hygiene

The public package is static and has no install step. Vercel receives only frontend, contract source and public deployment metadata.

Keep wallet private keys, vault exports, `.env` files, Vercel project state and dashboard data out of Git. This repository is for public source, UI, tests and deployment receipts only.

# Clause V2

A grounded policy-ruling contract.

The contract is shaped around policies, claims, source checks and settlement outcomes instead of a simple yes/no oracle.

## Clause Brief

Clause V2 (# v0.2.16), 60k bytes, schema-valid.

The important files are:

- `contracts/clause_v2.py` - GenLayer contract source
- `deployment.json` - Studionet address, deploy transaction and smoke transaction hashes
- `index.html` and `app.js` - static frontend
- `README.md` - this operator and reviewer guide

## Clause Chain Links

- Network: studionet (61999)
- Contract: [0x43D229F781dC44758A45FB683c4c785500769010](https://explorer-studio.genlayer.com/contracts/0x43D229F781dC44758A45FB683c4c785500769010)
- Deploy tx: [0x8eaeaac2...f3b722](https://explorer-studio.genlayer.com/tx/0x8eaeaac25d8269773241fcb37479b6b7b58b3bfade794602dc6dbbe404f3b722)
- Deployed at: 2026-06-24T03:25:12.781Z
- Smoke writes recorded: 14

## Coverage Mechanics

Typical flow: `open_claim` -> `submit` -> `review_dispute_with_genlayer` -> `resolve` -> `challenge` -> `submit_appeal` -> `set_claim_standard` -> `archive_dispute`

Useful reads: `get_claim_count`, `get_dispute_count`, `get_query_count`, `get_stats`, `get_claim`, `get_query`, `get_dispute`, `get_item_count`

- Primary source: `contracts/clause_v2.py` (60,079 bytes)
- Public write/action methods: 38
- Read methods: 27
- GenLayer features: live web rendering, LLM adjudication, validator-comparative consensus, indexed storage, append-only collections

## Smoke Trail

- set_claim_standard: [0x395e8d5d...be8145](https://explorer-studio.genlayer.com/tx/0x395e8d5dfebeda0801276fa1150aebad6960742205861565acaf8fe213be8145)
- file_query: [0x08c7cbd6...2f8f70](https://explorer-studio.genlayer.com/tx/0x08c7cbd6da5ca6b283a9f3fa8c02323e5c6d51fb3907e07197dc5dee4e2f8f70)
- add_obligation: [0x41c97ba0...0e68c1](https://explorer-studio.genlayer.com/tx/0x41c97ba0a50729bcef127c7222fbaa228e0a94f6a4cccced542ffa124b0e68c1)
- add_evidence_docs: [0x270421b6...956846](https://explorer-studio.genlayer.com/tx/0x270421b6604b5ba8d7136c0f32b68ce72d6e713fae2d8b8d1ffabc7a75956846)
- add_evidence_web: [0xf86c265a...b2932b](https://explorer-studio.genlayer.com/tx/0xf86c265a23c33441c4a00744563077762406969e0ad99ee1c5c12fd064b2932b)
- open_review: [0xf358f620...d21c5e](https://explorer-studio.genlayer.com/tx/0xf358f62061b33a78f8b44679c7607fab54dba9fc17e87fda1441df4304d21c5e)
- review: [0xbe9a42ea...b3d5b8](https://explorer-studio.genlayer.com/tx/0xbe9a42ea9e05ab57c7220771ed9cb4866b781c45ebe7349698ef34cf94b3d5b8)
- open_challenge_window: [0x1f52d723...e1bb12](https://explorer-studio.genlayer.com/tx/0x1f52d723c4679dd58274f1a18adcb913fb5449aa7ca5c02a1e7579fc10e1bb12)

## Operator Preview

```powershell
cd <private-workspace-root>
npm run preview:start
npm run preview:project -- 29-clause
```

Open http://localhost:8080/29-clause/.

## Release Command

```powershell
cd <private-workspace-root>
npm run publish:project -- -Project 29-clause -Repo https://github.com/aspro45/<repo-name>.git
```

## Public Repo Safety

- This repository should contain no decrypted wallet material.
- The Studionet deployer private key stays in the local encrypted vault.
- Vercel deployment should use the project folder only.

- QA notes: Smoke filed a policy query, attached official docs evidence, ran GenLayer review, challenge, appeal and final rule. Legacy get_query/get_stats verified.

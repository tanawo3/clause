# Clause - Contract API Manifest

**Contract class:** `Clause(gl.Contract)` · **File:** `contracts/clause.py`
**Runner:** pinned `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` (no `test`/`latest` alias)
**Network:** GenLayer studionet · **Deployed:** `0x8f1Df72EBD74F8bB0d8a50f01A03396bec33a1dB`

## Constructor
- `__init__()` - no arguments. Sets `owner = gl.message.sender_address` (the deployer).

## Persistent state
- `owner: Address` - administrator.
- `queries: DynArray[Query]` - every filed matter.
- `Query{ asker: Address, question: str, policy_url: str, status: u8, passage: str, rationale: str, archived: u8 }`

## Verdict / status enum
`PENDING(0)` → `PERMITTED(1)` | `PROHIBITED(2)` | `UNCLEAR(3)`

## Read methods (`@gl.public.view`)
| Method | Returns | Purpose |
|---|---|---|
| `get_owner()` | `str` | owner address |
| `get_query_count()` | `int` | number of queries (for pagination) |
| `get_stats()` | `dict` | counts: total/permitted/prohibited/unclear/pending (archived excluded) |
| `get_query(query_id)` | `dict` | one record: asker, question, policy_url, status, passage, rationale, archived |

## Write methods
| Method | Decorator | Permission | Effect |
|---|---|---|---|
| `file_query(question, policy_url)` | `@gl.public.write` | anyone | append a `PENDING` query; returns its id |
| `rule(query_id)` | `@gl.public.write` | anyone | non-deterministic; records the verdict + passage |
| `archive(query_id)` | `@gl.public.write` | **owner only** | hides a record from listings/stats |

## Input constraints
- `question`: non-empty after trim, ≤ **240** chars.
- `policy_url`: non-empty after trim, ≤ **300** chars, must start with `http://` or `https://`.
- Duplicate prevention: the same `asker` cannot file an identical `(question, policy_url)` that is not archived.

## State transitions
- `file_query` → `PENDING`.
- `rule` valid only from `PENDING`; sets `PERMITTED` | `PROHIBITED` | `UNCLEAR`. Re-calling on a non-pending query reverts (idempotent: a recorded ruling is never overwritten).
- `archive` sets `archived = 1` (owner only); archived queries are excluded from `get_stats` and cannot be ruled.

## Failure conditions (revert)
`a question is required`, `a policy URL is required`, `question exceeds 240 characters`, `policy URL exceeds 300 characters`, `policy URL must be http(s)`, `you have already filed this exact query`, `this query has already been ruled`, `this query is archived`, `only the owner can archive`, `no such query`.

## Non-deterministic operation - `rule()`
- **External access:** `gl.nondet.web.get(policy_url)` (body truncated to 6000 chars; raw page is **not** stored).
- **LLM:** `gl.nondet.exec_prompt(...)` instructs the model to answer **strictly from the document text** (not outside knowledge) and to quote one governing sentence.
- **Leader responsibility:** fetch the policy, decide `permitted|prohibited|unclear`, quote the passage.
- **Validator responsibility:** independently re-run the read + decision and accept only if the **verdict outcome** matches (substance, not JSON shape/format).
- **Extraction before comparison:** `_verdict_of` reduces the model output to the stable `(verdict, passage, reason)` triple; only the verdict enum is compared for consensus.
- **Source-grounding:** the stored `passage` is a sentence copied from the cited document.
- **Failure handling:** unreachable/empty source → `unclear` (an explicit determined state, never a false permit/prohibit). If validators do not reach consensus, `run_nondet_unsafe` raises, the transaction reverts, and the query **stays `PENDING`** - no incorrect state change.

## Equivalence strategy (summary)
Comparison key = the **verdict enum** each validator derives by independently reading the same source. This validates the substance of the interpretation rather than formatting, confidence, or JSON shape.

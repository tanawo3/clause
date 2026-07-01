# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
CLAUSE - Grounded Policy Rulings
================================
Ask whether a specific action is permitted under a specific written policy, and
get a ruling that is grounded in the document itself. A validator set reads the
linked policy and must independently agree on the outcome before it is recorded.

Why an Intelligent Contract: interpreting a rule against a real document is a
judgement that needs (a) reading external text and (b) protection from any single
party spinning the interpretation. GenLayer's Equivalence Principle runs the read
across independent validators and only records a ruling they agree on. The
governing passage is stored alongside the verdict so every ruling is citable.

Verdict (status):
  PENDING(0)    - filed, not yet ruled (also the safe state if consensus fails)
  PERMITTED(1)  - the policy allows it
  PROHIBITED(2) - the policy forbids it
  UNCLEAR(3)    - the policy does not decide it / source could not be read

Stored per query: asker, question, policy URL, status, governing passage,
rationale, archived flag. No raw web pages are stored - only the concise passage
the validators agreed grounds the ruling.
"""

from genlayer import *
from dataclasses import dataclass
import json
import typing


PENDING = 0
PERMITTED = 1
PROHIBITED = 2
UNCLEAR = 3

MAX_Q = 240
MAX_URL = 300
MAX_PASSAGE = 400


@allow_storage
@dataclass
class Query:
    asker: Address
    question: str
    policy_url: str
    status: u8
    passage: str
    rationale: str
    archived: u8


class Clause(gl.Contract):
    owner: Address
    queries: DynArray[Query]

    def __init__(self) -> None:
        self.owner = gl.message.sender_address

    # ----------------------------------------------------------------- writes
    @gl.public.write
    def file_query(self, question: str, policy_url: str) -> int:
        q = question.strip()
        u = policy_url.strip()
        if len(q) == 0:
            raise gl.vm.UserError("a question is required")
        if len(u) == 0:
            raise gl.vm.UserError("a policy URL is required")
        if len(q) > MAX_Q:
            raise gl.vm.UserError("question exceeds 240 characters")
        if len(u) > MAX_URL:
            raise gl.vm.UserError("policy URL exceeds 300 characters")
        if not (u.startswith("http://") or u.startswith("https://")):
            raise gl.vm.UserError("policy URL must be http(s)")
        # duplicate-action prevention: same asker + same question + same policy
        sender = gl.message.sender_address
        for existing in self.queries:
            if existing.archived == 0 and existing.asker == sender \
                    and existing.question == q and existing.policy_url == u:
                raise gl.vm.UserError("you have already filed this exact query")
        item = self.queries.append_new_get()
        item.asker = sender
        item.question = q
        item.policy_url = u
        item.status = u8(PENDING)
        item.passage = ""
        item.rationale = ""
        item.archived = u8(0)
        return len(self.queries) - 1

    @gl.public.write
    def rule(self, query_id: int) -> None:
        """Read the policy; validators must independently agree on the verdict.
        Idempotent: only a PENDING query can be ruled, so re-calling after a
        ruling reverts and never overwrites an existing ruling."""
        item = self._get(query_id)
        if item.status != PENDING:
            raise gl.vm.UserError("this query has already been ruled")
        if item.archived != 0:
            raise gl.vm.UserError("this query is archived")

        question = item.question
        url = item.policy_url

        def leader_fn() -> str:
            page = ""
            try:
                page = gl.nondet.web.get(url).body.decode("utf-8")[:6000]
            except Exception:
                page = ""
            if len(page.strip()) == 0:
                return json.dumps({"verdict": "unclear", "passage": "",
                                   "reason": "The policy source could not be read."})
            prompt = (
                "You are interpreting a written policy strictly against its own text.\n"
                f"QUESTION: Is the following permitted under this policy? {question}\n\n"
                f"POLICY DOCUMENT (verbatim, may be truncated):\n{page}\n\n"
                "Decide using ONLY the document text, not outside knowledge.\n"
                "- 'permitted' if the document allows it.\n"
                "- 'prohibited' if the document forbids it.\n"
                "- 'unclear' if the document does not address it.\n"
                "Quote the single most relevant sentence as the governing passage "
                "(<= 300 chars, copied from the document; empty if unclear).\n"
                'Reply with ONLY JSON: {"verdict":"permitted|prohibited|unclear",'
                '"passage":"<quoted sentence>","reason":"<one sentence>"}'
            )
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leader_res) -> bool:
            # Substance check: a validator independently reads the policy and
            # derives its OWN verdict, then accepts only if the outcome matches.
            if not isinstance(leader_res, gl.vm.Return):
                return False
            leader_verdict = self._verdict_of(leader_res.calldata)[0]
            own_verdict = self._verdict_of(leader_fn())[0]
            return leader_verdict == own_verdict

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        verdict, passage, reason = self._verdict_of(result)
        # If consensus could not be reached, run_nondet_unsafe raises and we never
        # get here, so the query stays PENDING (no incorrect state change).
        item.status = u8(verdict)
        item.passage = passage[:MAX_PASSAGE]
        item.rationale = reason[:MAX_PASSAGE]

    @gl.public.write
    def archive(self, query_id: int) -> None:
        """Owner-only: hide a spam/abusive query from listings."""
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("only the owner can archive")
        item = self._get(query_id)
        item.archived = u8(1)

    # ------------------------------------------------------------------ reads
    @gl.public.view
    def get_owner(self) -> str:
        return self.owner.as_hex

    @gl.public.view
    def get_query_count(self) -> int:
        return len(self.queries)

    @gl.public.view
    def get_stats(self) -> dict:
        permitted = 0
        prohibited = 0
        unclear = 0
        pending = 0
        active = 0
        for q in self.queries:
            if q.archived != 0:
                continue
            active += 1
            s = int(q.status)
            if s == PERMITTED:
                permitted += 1
            elif s == PROHIBITED:
                prohibited += 1
            elif s == UNCLEAR:
                unclear += 1
            else:
                pending += 1
        return {"total": active, "permitted": permitted, "prohibited": prohibited,
                "unclear": unclear, "pending": pending}

    @gl.public.view
    def get_query(self, query_id: int) -> dict:
        item = self._get(query_id)
        return {
            "asker": item.asker.as_hex,
            "question": item.question,
            "policy_url": item.policy_url,
            "status": int(item.status),
            "passage": item.passage,
            "rationale": item.rationale,
            "archived": int(item.archived),
        }

    # -------------------------------------------------------------- internals
    def _get(self, query_id: int) -> Query:
        if query_id < 0 or query_id >= len(self.queries):
            raise gl.vm.UserError("no such query")
        return self.queries[query_id]

    def _verdict_of(self, result: typing.Any) -> tuple:
        """Extract the concise, stable fields (verdict, passage, reason)."""
        data = result
        if isinstance(data, str):
            data = self._extract_json(data)
        if not isinstance(data, dict):
            return (UNCLEAR, "", "")
        raw = str(data.get("verdict", "")).strip().lower()
        passage = str(data.get("passage", ""))
        reason = str(data.get("reason", ""))
        if raw == "permitted":
            return (PERMITTED, passage, reason)
        if raw == "prohibited":
            return (PROHIBITED, passage, reason)
        return (UNCLEAR, passage, reason)

    def _extract_json(self, text: str) -> typing.Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (ValueError, TypeError):
                return None
        return None

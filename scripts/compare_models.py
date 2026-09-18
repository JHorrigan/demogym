"""Runs the two prompts against each candidate model and records what came back.

Reads the database and calls the API. It writes nothing: no draft row, no briefing row,
and no entry in the daily cap, because this is a measurement and not a use of the
product. See 016.

    uv run --env-file .env python scripts/compare_models.py <output.json> [ceiling]

The ceiling defaults to the one the application uses. Raising it answers a different
question: whether a model can hold the rules when it is not cut off, as against whether
it finishes inside the budget the application gives it.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI

from demogym.briefing_facts import for_site
from demogym.briefing_prompt import Briefing
from demogym.briefing_prompt import system as briefing_system
from demogym.briefing_prompt import user as briefing_user
from demogym.comparison import briefing_violations, draft_violations
from demogym.database import connect
from demogym.drafting import Controls
from demogym.drafts import candidate
from demogym.model import MAX_OUTPUT_TOKENS, ModelFailed, generate
from demogym.prompt import Message
from demogym.prompt import system as draft_system
from demogym.prompt import user as draft_user

CANDIDATES = ["gpt-5-nano", "gpt-5.6-luna", "gpt-5-mini"]

# One set of terms per member, spread across the dropdowns so the offer rule and both
# lengths are exercised. The same terms go to every model, so the only thing that
# differs between runs is the model.
TERMS = [
    Controls("warm", "standard", "none"),
    Controls("direct", "short", "free class"),
    Controls("encouraging", "standard", "guest pass"),
    Controls("warm", "short", "personal training session"),
    Controls("direct", "standard", "none"),
    Controls("encouraging", "short", "free class"),
]

# The six sites, and the six highest-priced High-band members at the current date.
SUBJECTS = """
select member_id from risk_scores
where band = 'high' and scored_on = (select max(scored_on) from risk_scores)
order by member_id
"""


def subjects(connection):
    """The members and sites every model is run over."""
    members = [row[0] for row in connection.execute(SUBJECTS).fetchall()][: len(TERMS)]
    sites = [row[0] for row in connection.execute("select id from sites order by id").fetchall()]
    return members, sites


def draft(client, facts, scored_on, controls, model, ceiling):
    """One draft, with the rules it broke."""
    generated = generate(
        client, draft_system(), draft_user(facts, controls, scored_on), Message, model, ceiling
    )
    broken = draft_violations(generated.output.subject, generated.output.body, controls.offer)
    return {
        "subject": generated.output.subject,
        "body": generated.output.body,
        "rationale": generated.output.rationale,
        "tone": controls.tone,
        "length": controls.length,
        "offer": controls.offer,
        "input_tokens": generated.input_tokens,
        "output_tokens": generated.output_tokens,
        "cost_usd_cents": str(generated.cost_usd_cents),
        "violations": [{"rule": v.rule, "quote": v.quote} for v in broken],
    }


def brief(client, facts, model, ceiling):
    """One briefing, with the rules it broke."""
    generated = generate(client, briefing_system(), briefing_user(facts), Briefing, model, ceiling)
    output = generated.output
    broken = briefing_violations(output.situation, output.contact_first, output.worth_checking)
    return {
        "site": facts.name,
        "situation": output.situation,
        "contact_first": output.contact_first,
        "worth_checking": output.worth_checking,
        "input_tokens": generated.input_tokens,
        "output_tokens": generated.output_tokens,
        "cost_usd_cents": str(generated.cost_usd_cents),
        "violations": [{"rule": v.rule, "quote": v.quote} for v in broken],
    }


def attempt(work):
    """Runs one call, recording a refusal rather than losing the rest of the run."""
    label, run = work
    try:
        return label, run()
    except ModelFailed as failed:
        return label, {"failed": failed.state, "detail": failed.detail, "violations": []}


def main(path, ceiling):
    client = OpenAI()
    with connect() as connection:
        members, sites = subjects(connection)
        member_facts = [candidate(connection, member_id) for member_id in members]
        site_facts = [for_site(connection, site_id) for site_id in sites]

    print(
        f"{len(members)} members, {len(sites)} sites, {len(CANDIDATES)} models, ceiling {ceiling}"
    )

    work = []
    for model in CANDIDATES:
        for found, controls in zip(member_facts, TERMS, strict=True):
            work.append(
                (
                    ("drafts", model, found.facts.account_number),
                    lambda f=found, c=controls, m=model: draft(
                        client, f.facts, f.scored_on, c, m, ceiling
                    ),
                )
            )
        for facts in site_facts:
            work.append(
                (
                    ("briefings", model, facts.name),
                    lambda f=facts, m=model: brief(client, f, m, ceiling),
                )
            )

    results = {
        "drafts": {model: {} for model in CANDIDATES},
        "briefings": {m: {} for m in CANDIDATES},
    }
    with ThreadPoolExecutor(max_workers=4) as pool:
        for (kind, model, name), outcome in pool.map(attempt, work):
            results[kind][model][name] = outcome
            broken = len(outcome["violations"])
            print(f"  {model:14} {kind[:-1]:9} {name:14} {broken} broken")

    with open(path, "w") as handle:
        json.dump(results, handle, indent=2)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else MAX_OUTPUT_TOKENS)

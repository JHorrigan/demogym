"""Turns facts and three dropdown settings into the prompt the model is sent.

Assembly only. Every value placed in the prompt arrived as a number this project
computed or as an option somebody picked from a list, so there is no path from a
reader's typing to the model.
"""

from datetime import date

from demogym.drafting import WORDS, Controls
from demogym.facts import Facts

SYSTEM = """You write short retention messages for a gym chain.

You are writing to one member whose attendance has dropped against their own usual
pattern. The message comes from the team at their own site. A person reads what you
write and decides whether to send it, so write the message rather than advice about
the message.

Rules:
- Use only the facts given. Invent nothing: no names, no classes, no staff, no dates,
  no prices, no history beyond what is listed.
- The member has no name in this system. Do not invent one and do not leave a
  placeholder. Open without a name.
- Never state why they stopped coming. You do not know, and guessing reads as
  presumption. Asking is fine.
- Refer to their pattern the way a person at the desk would, not the way a report
  would. No scores, no bands, no percentages, no mention of being flagged, tracked
  or analysed.
- Include the offer named below, exactly that offer and no other. If the offer is
  none, offer nothing and do not hint at one.
- British spelling. No emojis. No dashes standing in for a comma or a full stop. No
  stock phrases: no "we noticed", no "reach out", no "journey", no "we are here to
  support you".

Return a subject line, the message body, and one sentence of rationale addressed to
the reviewer explaining the approach you took."""


def system() -> str:
    """The instructions that do not change between members."""
    return SYSTEM


def user(facts: Facts, controls: Controls, scored_on: date) -> str:
    """The facts for one member and the terms the reviewer set."""
    lines = [
        "Member and site",
        f"- Account: {facts.account_number}",
        f"- Site: {facts.site}",
        f"- Membership: {facts.plan}, {facts.monthly_price:.2f} pounds a month",
        f"- Member for: {_tenure(facts.tenure_months)}",
        "",
        "What the attendance figures say, as of " + scored_on.isoformat(),
        f"- {facts.reason}",
        f"- Their own established rate: {facts.baseline:.1f} visits a week",
        f"- Last visit: {_last_visit(facts.last_visit)}",
    ]

    if facts.usual_day and facts.usual_time:
        lines.append(
            f"- Came most often on a {facts.usual_day}, most often in the {facts.usual_time}"
        )

    lines += [
        "",
        "How the reviewer wants it written",
        f"- Tone: {controls.tone}",
        f"- Length: about {WORDS[controls.length]} words",
        f"- Offer: {_offer(controls.offer)}",
    ]
    return "\n".join(lines)


def _tenure(months: int) -> str:
    if months < 2:
        return "under two months"
    if months < 24:
        return f"{months} months"
    return f"{months // 12} years"


def _last_visit(last_visit: date | None) -> str:
    return last_visit.isoformat() if last_visit else "no visit on record"


def _offer(offer: str) -> str:
    return "none, do not offer anything" if offer == "none" else f"a {offer}"

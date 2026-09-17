"""What the briefing call asks for, and what shape it expects back.

The rule about links is carried here explicitly rather than trusted to the model's
manners. A briefing that asserts the treadmills caused the churn is worse than no
briefing, because it is confident and wrong in a document a manager might act on.
See 0007.
"""

import re

from pydantic import BaseModel

from demogym.briefing_facts import LAPSE_WEEKS, SiteFacts

SYSTEM = f"""You write a short briefing for the manager of one gym site.

Everything you are given was computed from that site's own records before you were
asked. You do no arithmetic, you have no other information, and you go no further than
what is listed.

Produce three things:
- One paragraph naming the situation at this site.
- A short ordered list of who to contact first, using the account numbers given, in an
  order you choose, with the reason each one is in that position. Nobody who is not
  listed goes on it, and you do not number the entries: they are read in the order you
  give them.
- Anything in the figures that appears to sit together, written as something to check.
  At most two, and each one has to join a fact about members or the at-risk figures to
  a fact about attendance slots or equipment. Two ways of saying the same figure is not
  a pairing. If there is no pairing worth checking, say nothing stands out, which is a
  better answer than a padded one.

The rule about links matters more than anything else here:
- You may say that two facts sit alongside each other. You may not say, imply or
  suggest that one caused the other.
- Write a link as a check: "worth asking whether", "worth checking whether". Never
  "because", "due to", "caused by", "as a result of", "which explains", "driven by",
  "the reason for".
- If nothing stands out, say so. Inventing a link is worse than having none.
- You have no evidence about cause at all. These figures say what happened, not why.

Also:
- Name the figures as they are given. Do not round them into other numbers and do not
  work out new ones.
- The {LAPSE_WEEKS}-week lapse horizon is an assumption this project has not measured.
  If you mention it, say so.
- Never say or suggest that anything has been sent to a member, and do not mention
  sending at all. This system sends nothing, and a briefing that raises the subject
  invites the question.
- British spelling. No emojis. No dashes standing in for a comma or a full stop. No
  stock phrases: no "key takeaway", no "actionable", no "double down".
- Around two hundred words in total."""


class Briefing(BaseModel):
    """What the model returns: the situation, an order of work, and what to check."""

    situation: str
    contact_first: list[str]
    worth_checking: list[str]


def system() -> str:
    """The instructions that do not change between sites."""
    return SYSTEM


def user(facts: SiteFacts) -> str:
    """One site's computed facts, as the prompt states them."""
    return "\n".join(
        [
            "Site",
            f"- {facts.name}, {facts.region}",
            f"- Figures as of {facts.scored_on.isoformat()}",
            "",
            "At risk now",
            f"- {facts.high} High, {facts.medium} Medium, {facts.low} Low, "
            f"out of {facts.scored} members scored",
            f"- At-risk rate {facts.at_risk_rate:.1%}, {_change(facts.change_on_last_week)}",
            "- The at-risk rate at each of the twelve weekly dates, oldest first: "
            + ", ".join(f"{rate:.1%}" for rate in facts.twelve_weeks),
            "",
            "What that is worth",
            f"- Every banded member's membership: {facts.banded_value:.2f} pounds a month",
            f"- The High band alone: {facts.high_value:.2f} pounds a month. On current readings "
            f"those {facts.high} are the members counted as likely to lapse within "
            f"{LAPSE_WEEKS} weeks.",
            "",
            "The High band, most expensive membership first",
            *_members(facts),
            "",
            "Attendance slots that have thinned, the last three weeks against the nine before",
            *_slots(facts),
            "",
            "Equipment out of service",
            *_equipment(facts),
        ]
    )


def _change(change: float | None) -> str:
    if change is None:
        return "with no previous date to compare against"
    direction = "up" if change > 0 else "down"
    return f"{direction} {abs(change) * 100:.1f} percentage points on last week"


def _members(facts: SiteFacts) -> list[str]:
    if not facts.at_risk:
        return ["- Nobody is in the High band at this site."]
    return [
        f"- {member.account_number}, {member.monthly_price:.2f} a month: {member.reason}"
        for member in facts.at_risk
    ]


def _slots(facts: SiteFacts) -> list[str]:
    if not facts.thinned:
        return ["- No slot has lost as much as a visit a week."]
    return [
        f"- {slot.day} {slot.part}: was {slot.baseline:.1f} visits a week, now "
        f"{slot.recent:.1f}, down {slot.drop:.1f}"
        for slot in facts.thinned
    ]


def _equipment(facts: SiteFacts) -> list[str]:
    if not facts.broken:
        return ["- Everything is in service."]
    return [
        f"- {unit.name} ({unit.category}), out of service for {unit.days} days"
        for unit in facts.broken
    ]


ENUMERATION = re.compile(r"^\s*\d+[.)]\s*")


def _unnumbered(entry: str) -> str:
    """Drops a number the model put on an entry that the heading already numbers.

    The prompt asks it not to. It sometimes does anyway, and "1. 1. M00198" is the
    kind of thing that tells a reader the page was assembled rather than written.
    """
    return ENUMERATION.sub("", entry.strip())


def body(briefing: Briefing) -> str:
    """The three parts as one piece of prose, which is what the column holds.

    Assembly, not invention: every line below is the model's own words under a
    heading. Storing prose keeps `briefings.body` meaning what it says, and what is
    on the screen is character-for-character what was stored.
    """
    lines = [briefing.situation.strip(), "", "Who to contact first"]
    lines += [f"{place}. {_unnumbered(who)}" for place, who in enumerate(briefing.contact_first, 1)]
    lines += ["", "Worth checking"]
    if briefing.worth_checking:
        lines += [f"- {check.strip()}" for check in briefing.worth_checking]
    else:
        lines.append("- Nothing in these figures stands out as worth checking.")
    return "\n".join(lines)

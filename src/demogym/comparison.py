"""What counts as a rule broken, for the model comparison in 016.

Both prompts state their rules plainly, and a reviewer who has to fix one of them is
editing rather than approving. These checks count the breaches that can be found by
looking at the text. The ones that need judgement, whether a draft states why somebody
stopped coming and whether a briefing's prose is any good, are read by a person and
recorded beside these counts rather than guessed at here.

Every check quotes what it matched, so a count can be traced back to the output.
"""

import re
from dataclasses import dataclass

# The offer words a message may only use when the reviewer chose that offer. "Feel
# free" is the obvious false positive and is excluded where the words are built.
OFFERS = {
    "free class": ["free class"],
    "guest pass": ["guest pass"],
    "personal training session": ["personal training", "pt session"],
}

ANY_OFFER = [
    "free class",
    "free session",
    "free month",
    "guest pass",
    "personal training",
    "pt session",
    "complimentary",
    "on the house",
    "no charge",
]

# The prompt bans the language of measurement. A member is not told they were scored.
ANALYTICS = [
    "score",
    "band",
    "flagged",
    "tracked",
    "analysed",
    "analyzed",
    "at risk",
    "at-risk",
    "our records",
    "the data",
    "our system",
]

DRAFT_STOCK = ["we noticed", "reach out", "journey", "here to support you"]
BRIEFING_STOCK = ["key takeaway", "actionable", "double down"]

# Asserting a cause is the one thing a briefing may never do. See 0007.
CAUSAL = [
    "because",
    "due to",
    "caused by",
    "as a result of",
    "which explains",
    "driven by",
    "the reason for",
    "led to",
    "resulted in",
    "owing to",
    "explains why",
    "contributing to",
    "contributes to",
]

SENDING = [
    "was sent",
    "were sent",
    "has been sent",
    "have been sent",
    "will be sent",
    "we sent",
    "send them",
    "sending",
    "messaged",
]

AMERICAN = ["organiz", "analyz", "optimiz", "color", "favor", "center", "neighbor", "canceled"]

PLACEHOLDERS = [r"\[[^\]]{1,30}\]", r"\{[^}]{1,30}\}", r"<[^>]{1,30}>"]

GREETING = re.compile(r"\b(?:Dear|Hi|Hello)[ \t]+([A-Z][a-z]{2,})")

EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")

DASH = re.compile(r"\s[-–—]{1,2}\s|—|–")


@dataclass(frozen=True)
class Violation:
    """One rule broken, and the text that broke it."""

    rule: str
    quote: str


def _find(text: str, phrases: list[str], rule: str) -> list[Violation]:
    """Every phrase present, quoted with a little of what surrounds it."""
    lowered = text.lower()
    found = []
    for phrase in phrases:
        at = lowered.find(phrase)
        if at >= 0:
            found.append(Violation(rule, text[max(0, at - 25) : at + len(phrase) + 25].strip()))
    return found


def house_style(text: str, stock: list[str]) -> list[Violation]:
    """The rules both prompts share: spelling, emoji, dashes and stock phrases."""
    found = _find(text, stock, "stock phrase")
    found += _find(text, AMERICAN, "American spelling")
    found += [Violation("emoji", match.group()) for match in EMOJI.finditer(text)]
    found += [Violation("dash as punctuation", match.group()) for match in DASH.finditer(text)]
    return found


def draft_violations(subject: str, body: str, offer: str) -> list[Violation]:
    """Every rule the drafting prompt states that this message breaks."""
    text = f"{subject}\n{body}"
    found = house_style(text, DRAFT_STOCK)
    found += _find(text, ANALYTICS, "language of measurement")
    found += [Violation("percentage", match.group()) for match in re.finditer(r"\d+\s?%", text)]

    for pattern in PLACEHOLDERS:
        found += [Violation("placeholder", match.group()) for match in re.finditer(pattern, text)]

    name = GREETING.search(text)
    if name:
        found.append(Violation("invented name", name.group()))

    found += _offer_violations(text, offer)
    return found


def _offer_violations(text: str, offer: str) -> list[Violation]:
    """The offer the reviewer chose, and nothing else, has to be the one on the page."""
    lowered = text.lower()
    if offer == "none":
        return [
            Violation("offer where none was chosen", phrase)
            for phrase in ANY_OFFER
            if phrase in lowered and not _is_feel_free(lowered, phrase)
        ]

    wanted = OFFERS[offer]
    found = []
    if not any(phrase in lowered for phrase in wanted):
        found.append(Violation("chosen offer missing", offer))

    found += [
        Violation("an offer that was not chosen", phrase)
        for phrase in ANY_OFFER
        if phrase not in wanted and phrase in lowered and not _is_feel_free(lowered, phrase)
    ]
    return found


def _is_feel_free(lowered: str, phrase: str) -> bool:
    """`feel free` is not an offer, and it is the one false positive worth excluding."""
    at = lowered.find(phrase)
    return at >= 5 and lowered[at - 5 : at] == "feel "


def briefing_violations(
    situation: str, contact_first: list[str], checks: list[str]
) -> list[Violation]:
    """Every rule the briefing prompt states that this briefing breaks.

    The causation rule is checked on the situation and on the links, and not on the
    order of work. The prompt asks for the reason each member is in their position, so
    "first because this is the highest-priced membership" is the instruction being
    followed rather than a cause being claimed. Whether an entry there claims a cause
    about attendance is a judgement, and it is read rather than counted.
    """
    text = "\n".join([situation, *contact_first, *checks])
    claims = "\n".join([situation, *checks])
    found = house_style(text, BRIEFING_STOCK)
    found += _find(claims, CAUSAL, "asserts a cause")
    found += _find(text, SENDING, "mentions sending")
    found += [
        Violation("numbered itself", entry[:40])
        for entry in contact_first
        if re.match(r"\s*\d+[.)]", entry)
    ]
    return found

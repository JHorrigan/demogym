"""The facts one site's briefing is written from, all of them computed already.

The model gets counts, rates, dates and money. It does no arithmetic, it queries
nothing, and it never sees an entry row or a member's history. Everything here traces
back to a stored value, which is what lets a client ask how the forecast works and be
answered with a calculation.
"""

from dataclasses import dataclass
from datetime import date

import psycopg

from demogym.drafts import LOCAL
from demogym.slots import Slot, thinned

# On current readings, the High band is the set counted as likely to lapse inside
# this horizon. The number of weeks is an assumption and the briefing says so: this
# project has no cancellations to fit it against, and fitting it against the
# generator's own leavers would measure the generator rather than the rule.
LAPSE_WEEKS = 6

BANDS = """
with latest as (
    select max(scored_on) as scored_on from risk_scores
),
per_date as (
    select r.scored_on,
           count(*) as scored,
           count(*) filter (where r.band <> 'unflagged') as at_risk
    from risk_scores r
    join members m on m.id = r.member_id
    where m.site_id = %s
    group by r.scored_on
)
select (select scored_on from latest) as scored_on,
       (select array_agg(round(at_risk::numeric / scored, 4) order by scored_on)
          from per_date) as rates,
       count(*) filter (where r.band = 'high') as high,
       count(*) filter (where r.band = 'medium') as medium,
       count(*) filter (where r.band = 'low') as low,
       count(*) as scored,
       coalesce(sum(m.monthly_price) filter (where r.band = 'high'), 0) as high_value,
       coalesce(sum(m.monthly_price) filter (where r.band <> 'unflagged'), 0) as banded_value
from risk_scores r
join members m on m.id = r.member_id,
     latest
where m.site_id = %s
  and r.scored_on = latest.scored_on
"""

SITE = "select name, region from sites where id = %s"

DOWN = """
select name, category, down_since
from equipment
where site_id = %s and status = 'out of service'
order by down_since
"""

VISITS = f"""
select (entered_at at time zone '{LOCAL}')
from entries
where site_id = %s
order by 1
"""  # noqa: S608

WORST_FIRST = """
select m.account_number, m.monthly_price, r.reason
from risk_scores r
join members m on m.id = r.member_id
where m.site_id = %s
  and r.scored_on = %s
  and r.band = 'high'
order by m.monthly_price desc, m.account_number
"""


@dataclass(frozen=True)
class AtRisk:
    """One High-band member, as the briefing is allowed to name them."""

    account_number: str
    monthly_price: float
    reason: str


@dataclass(frozen=True)
class Broken:
    """One unit out of service, and how long it has been."""

    name: str
    category: str
    days: int


@dataclass(frozen=True)
class SiteFacts:
    """One site at one scoring date, as the prompt describes it."""

    name: str
    region: str
    scored_on: date
    scored: int
    high: int
    medium: int
    low: int
    at_risk_rate: float
    change_on_last_week: float | None
    twelve_weeks: list[float]
    high_value: float
    banded_value: float
    at_risk: list[AtRisk]
    thinned: list[Slot]
    broken: list[Broken]


def for_site(connection: psycopg.Connection, site_id: int) -> SiteFacts | None:
    """Everything one briefing is written from, or None if there is no such site."""
    site = connection.execute(SITE, (site_id,)).fetchone()
    if site is None:
        return None

    name, region = site
    row = connection.execute(BANDS, (site_id, site_id)).fetchone()
    scored_on, rates, high, medium, low, scored, high_value, banded_value = row
    trend = [float(rate) for rate in rates or []]

    return SiteFacts(
        name=name,
        region=region,
        scored_on=scored_on,
        scored=scored,
        high=high,
        medium=medium,
        low=low,
        at_risk_rate=trend[-1] if trend else 0.0,
        change_on_last_week=trend[-1] - trend[-2] if len(trend) > 1 else None,
        twelve_weeks=trend,
        high_value=float(high_value),
        banded_value=float(banded_value),
        at_risk=[
            AtRisk(account_number=account, monthly_price=float(price), reason=reason)
            for account, price, reason in connection.execute(
                WORST_FIRST, (site_id, scored_on)
            ).fetchall()
        ],
        thinned=thinned(
            [row[0] for row in connection.execute(VISITS, (site_id,)).fetchall()], scored_on
        ),
        broken=[
            Broken(name=unit, category=category, days=(scored_on - down_since).days)
            for unit, category, down_since in connection.execute(DOWN, (site_id,)).fetchall()
        ],
    )

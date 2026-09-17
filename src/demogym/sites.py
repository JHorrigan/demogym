"""The six sites the estate is built on."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Site:
    """One gym in the chain.

    `members` shapes generation rather than being stored: the sites table holds no
    member count, and the count on screen is always read from the members table.
    """

    name: str
    region: str
    opened_on: date
    members: int


# Invented names and a deliberately uneven spread of sizes, so the estate screen has
# something to rank and a bigger site cannot be mistaken for a site in trouble.
SITES = (
    Site("Northgate", "North West", date(2013, 9, 2), 68),
    Site("Kingsway", "West Midlands", date(2015, 4, 13), 57),
    Site("Riverside", "Yorkshire", date(2016, 1, 11), 52),
    Site("Parkhead", "Scotland", date(2017, 8, 7), 46),
    Site("Castle Street", "South West", date(2019, 2, 4), 41),
    Site("Meadowbank", "East of England", date(2021, 6, 14), 36),
)

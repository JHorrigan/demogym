"""The equipment catalogue and the units placed at each site."""

from dataclasses import dataclass
from datetime import date, timedelta
from random import Random

from demogym.sites import SITES, Site

WORKING = "working"
OUT_OF_SERVICE = "out of service"

# Around a hundred units across the estate, shared out by site size.
TOTAL_UNITS = 100

# The share of units currently out of service.
OUT_OF_SERVICE_SHARE = 0.07


@dataclass(frozen=True)
class EquipmentType:
    """A kind of equipment, not a particular machine."""

    name: str
    category: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Unit:
    """One machine at one site."""

    site: Site
    type: EquipmentType
    installed_on: date
    status: str
    down_since: date | None


def _types(category: str, names: tuple[str, ...]) -> tuple[EquipmentType, ...]:
    return tuple(EquipmentType(name, category) for name in names)


# Written by rule rather than by a model. Reference data of this size is
# reproducible and checkable; model-written reference data is neither. See 0003.
CATALOGUE = (
    *_types(
        "cardio",
        (
            "Treadmill",
            "Upright bike",
            "Recumbent bike",
            "Cross trainer",
            "Stair climber",
            "Rowing machine",
            "Air bike",
            "Ski trainer",
            "Spin bike",
            "Arc trainer",
        ),
    ),
    *_types(
        "selectorised strength",
        (
            "Chest press",
            "Shoulder press",
            "Lat pulldown",
            "Seated row",
            "Leg press",
            "Leg extension",
            "Leg curl",
            "Pec deck",
            "Triceps extension",
            "Biceps curl",
            "Abdominal crunch",
            "Back extension",
            "Hip abductor",
        ),
    ),
    *_types(
        "plate-loaded",
        (
            "Incline press",
            "Decline press",
            "Hack squat",
            "Pendulum squat",
            "Seated dip",
            "Plate-loaded row",
            "Belt squat",
            "Standing calf raise",
        ),
    ),
    *_types(
        "racks and benches",
        (
            "Power rack",
            "Half rack",
            "Squat stand",
            "Flat bench",
            "Adjustable bench",
            "Preacher curl bench",
        ),
    ),
    *_types(
        "free weights",
        (
            "Dumbbell set",
            "Kettlebell set",
            "Olympic barbell",
            "EZ bar",
            "Weight plate set",
        ),
    ),
    *_types(
        "functional",
        (
            "Cable crossover",
            "Functional trainer",
            "Battle ropes",
            "Plyometric boxes",
            "Sled track",
            "Suspension trainer",
        ),
    ),
)

# How many of one type a site plausibly holds. A gym has several treadmills and
# one preacher curl bench.
UNITS_OF_A_TYPE = {
    "cardio": (1, 4),
    "selectorised strength": (1, 2),
    "plate-loaded": (1, 2),
    "racks and benches": (1, 3),
    "free weights": (1, 2),
    "functional": (1, 2),
}


def generate(as_of: date, random: Random) -> list[Unit]:
    """Places units at every site, in a stable order."""
    units = []
    for site in SITES:
        units.extend(_units_at(site, as_of, random))
    return units


def _units_at(site: Site, as_of: date, random: Random) -> list[Unit]:
    """Fills a site up to its share of the estate from a shuffled catalogue.

    Walking a shuffled catalogue rather than choosing types independently is what
    keeps two sites from holding the same inventory.
    """
    target = round(TOTAL_UNITS * site.members / sum(other.members for other in SITES))
    catalogue = list(CATALOGUE)
    random.shuffle(catalogue)

    units: list[Unit] = []
    for equipment_type in catalogue:
        if len(units) >= target:
            break
        lowest, highest = UNITS_OF_A_TYPE[equipment_type.category]
        for _ in range(random.randint(lowest, highest)):
            if len(units) >= target:
                break
            units.append(_unit(site, equipment_type, as_of, random))
    return units


def _unit(site: Site, equipment_type: EquipmentType, as_of: date, random: Random) -> Unit:
    installed_on = _installed_on(site, as_of, random)
    if random.random() >= OUT_OF_SERVICE_SHARE:
        return Unit(site, equipment_type, installed_on, WORKING, None)
    return Unit(site, equipment_type, installed_on, OUT_OF_SERVICE, _down_since(as_of, random))


def _installed_on(site: Site, as_of: date, random: Random) -> date:
    """Spread over the last few years rather than clustered on one date."""
    earliest = max(site.opened_on, as_of - timedelta(days=6 * 365))
    latest = as_of - timedelta(days=30)
    return earliest + timedelta(days=random.randint(0, (latest - earliest).days))


def _down_since(as_of: date, random: Random) -> date:
    """Most faults are recent. Some have been waiting on a part for weeks."""
    days = random.randint(2, 13) if random.random() < 0.55 else random.randint(14, 60)
    return as_of - timedelta(days=days)

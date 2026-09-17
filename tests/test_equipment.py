from collections import Counter
from datetime import date, timedelta
from random import Random

from demogym.equipment import CATALOGUE, OUT_OF_SERVICE, WORKING, generate
from demogym.seed import SEED
from demogym.sites import SITES

AS_OF = date(2026, 9, 17)

CATEGORIES = {
    "cardio",
    "selectorised strength",
    "plate-loaded",
    "racks and benches",
    "free weights",
    "functional",
}


def units(seed: int = SEED):
    return generate(AS_OF, Random(seed))


def test_the_catalogue_holds_forty_to_fifty_types() -> None:
    assert 40 <= len(CATALOGUE) <= 50


def test_every_catalogue_type_has_a_name_and_a_known_category() -> None:
    for equipment_type in CATALOGUE:
        assert equipment_type.name
        assert equipment_type.category in CATEGORIES


def test_every_catalogue_name_is_unique() -> None:
    names = [equipment_type.name for equipment_type in CATALOGUE]

    assert len(set(names)) == len(names)


def test_every_category_is_represented_in_the_catalogue() -> None:
    assert {equipment_type.category for equipment_type in CATALOGUE} == CATEGORIES


def test_about_a_hundred_units_exist() -> None:
    assert 90 <= len(units()) <= 110


def test_every_unit_belongs_to_one_of_the_six_sites() -> None:
    for unit in units():
        assert unit.site in SITES


def test_every_unit_is_a_type_from_the_catalogue() -> None:
    for unit in units():
        assert unit.type in CATALOGUE


def test_every_site_holds_some_equipment() -> None:
    held = Counter(unit.site for unit in units())

    assert set(held) == set(SITES)
    assert all(count > 0 for count in held.values())


def test_a_bigger_site_holds_more_equipment_than_a_smaller_one() -> None:
    held = Counter(unit.site for unit in units())
    ordered = sorted(SITES, key=lambda site: site.members)

    assert held[ordered[0]] < held[ordered[-1]]


def test_no_two_sites_hold_an_identical_inventory() -> None:
    inventories = {}
    for unit in units():
        inventories.setdefault(unit.site, Counter())[unit.type.name] += 1

    listed = [tuple(sorted(inventory.items())) for inventory in inventories.values()]

    assert len(set(listed)) == len(listed)


def test_some_sites_hold_several_units_of_one_type() -> None:
    counted = Counter((unit.site, unit.type.name) for unit in units())

    assert any(count > 1 for count in counted.values())


def test_no_install_date_falls_in_the_future() -> None:
    for unit in units():
        assert unit.installed_on <= AS_OF


def test_no_unit_was_installed_before_its_site_opened() -> None:
    for unit in units():
        assert unit.installed_on >= unit.site.opened_on


def test_install_dates_are_spread_rather_than_clustered() -> None:
    years = {unit.installed_on.year for unit in units()}

    assert len(years) >= 4


def test_a_unit_in_service_carries_no_down_since() -> None:
    for unit in units():
        if unit.status == WORKING:
            assert unit.down_since is None


def test_a_unit_out_of_service_carries_a_down_since_in_the_past() -> None:
    for unit in units():
        if unit.status == OUT_OF_SERVICE:
            assert unit.down_since is not None
            assert unit.down_since < AS_OF


def test_every_status_is_one_the_schema_accepts() -> None:
    """Spelt out rather than taken from the module, because the check constraint in
    004_create_equipment.sql is a separate artefact that has to agree with it."""
    for unit in units():
        assert unit.status in ("working", "out of service")


def test_a_handful_are_out_of_service_rather_than_none_or_most() -> None:
    down = [unit for unit in units() if unit.status == OUT_OF_SERVICE]

    assert 2 <= len(down) <= 15


def test_at_least_one_unit_has_been_down_long_enough_to_be_worth_reporting() -> None:
    """A briefing naming a fault down two days is noise. Ten days is a fact."""
    down = [unit for unit in units() if unit.down_since]

    assert any(AS_OF - unit.down_since >= timedelta(days=10) for unit in down)


def test_the_same_seed_produces_the_same_equipment() -> None:
    assert units(SEED) == units(SEED)


def test_a_different_seed_produces_different_equipment() -> None:
    assert units(SEED) != units(SEED + 1)

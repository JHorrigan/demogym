---
slice: 005
title: Generate and seed the equipment
status: complete
depends_on: [003]
decisions: [0003]
---

# 005 - Generate and seed the equipment

## Goal

Around a hundred equipment units spread across the six sites, with install dates going back a few years and a handful currently out of service.

## Why now

The briefing in 013 is the only consumer of this data, and it cannot be written until the data exists. It is independent of the member data and much smaller, so it does not belong inside 004.

## In scope

- A fixture of forty to fifty equipment types with a name and a category: cardio, selectorised strength, plate-loaded, racks and benches, free weights, functional.
- A generator placing units at sites. Not every site holds every type, and some hold several of a type.
- Install dates spread across the last few years rather than clustered on one date.
- A status per unit, with a small number out of service carrying a `down_since` date in the past.
- Invariant tests: every unit attached to a site, every unit a type that exists, no install date in the future, no `down_since` on a unit that is in service.

## Not in scope

- Generating the type catalogue with a model. 0003 rules it out: rule-written reference data is reproducible and checkable, model-written data is neither, and this is fifty rows.
- Fault history, capex planning, and any link between equipment and members. All three are recorded under deliberately absent in the specification.

## Done when

- Around a hundred units exist across six sites, and no two sites hold an identical inventory.
- Every invariant test passes, and each fails when the corresponding rule is deliberately broken.
- At least one unit has been out of service long enough that a briefing mentioning it would be saying something.
- Running twice with the same seed produces identical data.

## Evidence

**Around a hundred units exist across six sites, and no two hold an identical inventory.** In Neon after
seeding:

```
Northgate        23 units, 1 out of service, 12 distinct types
Kingsway         19 units, 1 out of service, 12 distinct types
Riverside        17 units, 1 out of service,  9 distinct types
Parkhead         15 units, 1 out of service,  9 distinct types
Castle Street    14 units, 2 out of service, 10 distinct types
Meadowbank       12 units, 0 out of service,  8 distinct types
```

100 units exactly, drawing on 37 of the 48 catalogue types. A site's share follows its member count, so
the biggest site holds roughly twice what the smallest does. Meadowbank holds nothing out of service,
which is a site with nothing to report rather than a gap in the data.

```
$ uv run --env-file .env demogym seed --as-of 2026-09-17
Replacing 6 sites, 300 members, 0 equipment units and 12110 entries.
Wrote 6 sites.
Wrote 300 members.
Wrote 100 equipment units.
Wrote 12110 entries as of 2026-09-17, seed 20260917.
```

**Invariants hold in the database, not only in the tests.**

```
units with no site:                   0
install dates in the future:          0
working units carrying a down_since:  0
```

**At least one unit has been down long enough that a briefing mentioning it would be saying something.**
Six units are out of service and two of them are long-standing:

```
Castle Street   EZ bar                48 days
Kingsway        Chest press           29 days
Castle Street   Sled track             7 days
Parkhead        Seated row             6 days
Riverside       Arc trainer            5 days
Northgate       Air bike               3 days
```

A fault three days old is noise. Forty-eight days is a fact, and it is the kind of thing the briefing in
013 exists to surface.

Install dates span 2020 to 2026 rather than clustering, and the catalogue covers all six categories:

```
selectorised strength  27    cardio        26
functional             18    plate-loaded  15
free weights            8    racks and benches  6
```

**Every invariant test fails when the rule it guards is broken.** Twenty-one tests, each checked by
breaking the corresponding rule, running that test alone, and confirming it failed. The generator was
then restored and confirmed byte-identical.

| Rule broken | Test that failed |
|---|---|
| The catalogue is cut to twelve types | `the_catalogue_holds_forty_to_fifty_types` |
| Every type gets an invented category | `every_catalogue_type_has_a_name_and_a_known_category`, `every_category_is_represented_in_the_catalogue` |
| Two types share a name | `every_catalogue_name_is_unique` |
| The estate target is raised to 400 | `about_a_hundred_units_exist` |
| A unit is attached to a site not in the estate | `every_unit_belongs_to_one_of_the_six_sites` |
| A unit gets a type not in the catalogue | `every_unit_is_a_type_from_the_catalogue` |
| Every site gets the same fixed target | `a_bigger_site_holds_more_equipment_than_a_smaller_one` |
| The catalogue is not shuffled and targets are equal | `no_two_sites_hold_an_identical_inventory` |
| Only ever one unit of a type | `some_sites_hold_several_units_of_one_type` |
| One site is skipped | `every_site_holds_some_equipment` |
| Install dates run into the future | `no_install_date_falls_in_the_future` |
| Install dates ignore when the site opened | `no_unit_was_installed_before_its_site_opened` |
| Every unit is installed on the same day | `install_dates_are_spread_rather_than_clustered` |
| A working unit carries a `down_since` | `a_unit_in_service_carries_no_down_since` |
| An out-of-service unit carries none | `a_unit_out_of_service_carries_a_down_since_in_the_past` |
| Nothing is ever out of service | `a_handful_are_out_of_service_rather_than_none_or_most` |
| Every fault is two days old | `at_least_one_unit_has_been_down_long_enough_to_be_worth_reporting` |
| A status the schema would reject | `every_status_is_one_the_schema_accepts` |
| Generation reads the unseeded global random | `the_same_seed_produces_the_same_equipment` |
| The seed is ignored entirely | `a_different_seed_produces_different_equipment` |

**The mutation run found a worthless test.** `every_status_is_one_the_schema_accepts` originally
asserted `unit.status in (WORKING, OUT_OF_SERVICE)`, importing both constants from the module under
test, so renaming `WORKING` to anything at all kept it green. The status vocabulary exists to agree with
the check constraint in `004_create_equipment.sql`, which is a separate artefact, so the test now spells
out `"working"` and `"out of service"` and fails when the constants drift from the SQL.

**Running twice with the same seed produces identical data.** `the_same_seed_produces_the_same_equipment`
compares two full generations field by field, and `a_different_seed_produces_different_equipment` is the
converse. Both were checked by mutation, above.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      44 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

100 units across the six sites are in Neon, drawn from a 48-type catalogue written by rule, with install
dates spread across 2020 to 2026 and six units currently out of service.

`equipment.py` holds the catalogue and the placement. The catalogue is a literal rather than generated,
which is what 0003 asks for: reference data of this size written by rule is reproducible and checkable.

Three decisions the slice left open, settled here.

A site's share of the estate follows its member count, so the estate screen's equipment column varies
with site size the way the member counts do.

Inventories differ because each site walks a freshly shuffled catalogue until it hits its target, rather
than choosing types independently. That gives overlap without repetition, and it is what the
identical-inventory test guards.

Fault ages are drawn in two groups, most within a fortnight and some stretching to two months, because a
single uniform range would make a long-standing fault a matter of luck rather than something the data
reliably contains.

One thing this slice does not do, and it is deliberate. There is no link between a fault and the
attendance that thinned around it. The specification's briefing example pairs two dead treadmills with
six weekday-morning regulars going quiet, and the prompt is required to state any such link as a
hypothesis rather than a finding. Manufacturing the correlation in the generator would make that
hypothesis true by construction, which is exactly the kind of claim the honesty rules rule out. The
briefing gets the facts side by side and says no more than that.

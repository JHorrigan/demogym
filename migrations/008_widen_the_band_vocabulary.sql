-- A row exists for every eligible member at every scoring date, not only for the
-- ones a band was reached on. Slice 006 asks for twelve rows per eligible member,
-- and the specification's volume of around 3,600 scores is 300 members by 12 weeks.
--
-- So a member whose readings do not reach Low needs a value rather than no row.
-- The queue selects the three bands and ignores this one; the estate screen divides
-- the banded count by the active members to get the at-risk rate.
alter table risk_scores drop constraint risk_scores_band_check;

alter table risk_scores
    add constraint risk_scores_band_check
        check (band in ('high', 'medium', 'low', 'unflagged'));

-- Both readings behind a band are stored rather than just the band, so any reason
-- string can be checked against the numbers that produced it.
create table risk_scores (
    member_id integer not null references members (id),
    scored_on date not null,
    band text not null check (band in ('high', 'medium', 'low')),
    reason text not null,
    baseline numeric(5, 2) not null,
    recent_rate numeric(5, 2) not null,
    -- Null where the arithmetic has no answer: decay needs a baseline above zero,
    -- typical_gap needs two visits, gap_multiple needs a last visit and a typical gap.
    decay numeric(5, 2),
    typical_gap numeric(5, 2),
    gap_multiple numeric(5, 2),
    primary key (member_id, scored_on)
);

-- The estate screen counts bands per scoring date. The queue filters the most
-- recent date by band.
create index risk_scores_scored_on_band_idx on risk_scores (scored_on, band);

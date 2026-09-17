-- One table rather than a catalogue and a unit register, because the capex feature
-- that needed the split is not built. Fault history is reduced to a current status
-- and down_since, which is what the briefing needs.
create table equipment (
    id integer generated always as identity primary key,
    site_id integer not null references sites (id),
    name text not null,
    category text not null,
    installed_on date not null,
    status text not null check (status in ('working', 'out of service')),
    down_since date,
    -- The briefing says what is down and for how long, so one cannot hold without the other.
    constraint equipment_down_since_matches_status
        check ((status = 'out of service') = (down_since is not null))
);

-- The estate screen shows equipment currently out of service per site.
create index equipment_site_id_status_idx on equipment (site_id, status);

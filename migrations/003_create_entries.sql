-- Arrival only. There is no exit time, so there is no session and no dwell time,
-- because most turnstiles do not scan on the way out.
create table entries (
    id bigint generated always as identity primary key,
    member_id integer not null references members (id),
    site_id integer not null references sites (id),
    entered_at timestamptz not null
);

-- Scoring reads one member's history over a trailing window.
create index entries_member_id_entered_at_idx on entries (member_id, entered_at);

-- The briefing reads a site's attendance by day of week and time of day.
create index entries_site_id_entered_at_idx on entries (site_id, entered_at);

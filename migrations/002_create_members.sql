create table members (
    id integer generated always as identity primary key,
    site_id integer not null references sites (id),
    account_number text not null unique,
    joined_on date not null,
    left_on date,
    plan text not null,
    monthly_price numeric(6, 2) not null
);

-- The estate screen counts active members per site.
create index members_site_id_idx on members (site_id);

create table briefings (
    site_id integer not null references sites (id),
    generated_on date not null,
    body text not null,
    model text not null,
    input_tokens integer not null,
    output_tokens integer not null,
    cost_usd_cents numeric(10, 4) not null,
    primary key (site_id, generated_on)
);

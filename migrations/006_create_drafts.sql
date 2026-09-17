create table drafts (
    member_id integer not null,
    scored_on date not null,
    -- One redraft per member, so 1 or 2. Both versions are kept.
    attempt smallint not null check (attempt in (1, 2)),
    tone text not null check (tone in ('warm', 'direct', 'encouraging')),
    length text not null check (length in ('short', 'standard')),
    offer text not null
        check (offer in ('none', 'free class', 'guest pass', 'personal training session')),
    subject text not null,
    body text not null,
    rationale text not null,
    model text not null,
    input_tokens integer not null,
    output_tokens integer not null,
    -- Fractional cents. A draft costs well under one cent, so an integer column
    -- would round the measurement away and leave an estimate.
    cost_usd_cents numeric(10, 4) not null,
    decision text check (decision in ('approved', 'edited', 'rejected')),
    -- Stored beside the draft, never over it, so the edit can be shown against
    -- what the model wrote.
    edited_body text,
    decided_at timestamptz,
    primary key (member_id, scored_on, attempt),
    -- A draft belongs to the score that justified it.
    foreign key (member_id, scored_on) references risk_scores (member_id, scored_on),
    constraint drafts_decision_has_a_timestamp
        check ((decision is null) = (decided_at is null))
);

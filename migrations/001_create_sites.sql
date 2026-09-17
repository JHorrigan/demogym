create table sites (
    id integer generated always as identity primary key,
    name text not null,
    region text not null,
    opened_on date not null
);

-- The daily cap counts requests the endpoint accepts, which is not the same as
-- rows written: a call that fails writes no draft and still has to count, or a
-- broken model would be an unlimited one. So the count needs its own record.
--
-- 0002 anticipated this. It is the one piece of state read and written while a
-- request is in flight, and in the prototype it is a row in Postgres.
create table model_calls (
    day date primary key,
    calls integer not null check (calls >= 0)
);

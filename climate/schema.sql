drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  dt datetime default current_timestamp,
  temperature integer not null,
  humidity integer not null
);

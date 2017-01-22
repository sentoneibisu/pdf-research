-- Tasks are steps that can be taken to complete a project
create table url (
    id          integer primary key autoincrement not null,
    url         text,
    add_date    date,
    status      integer default 0,
    keyword     text,  
    domain      text
);

create table search_keyword (
    id          integer primary key autoincrement not null,
    keyword     text,
    status      integer default 0
);

create table search_domain (
    id          integer primary key autoincrement not null,
    domain      text,
    status      integer default 0
);

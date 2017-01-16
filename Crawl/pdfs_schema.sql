-- Tasks are steps that can be taken to complete a project
create table pdfs (
    id          integer primary key autoincrement not null,
    url         text,
    add_date    date,
    status      integer default 0,
    md5         text
);

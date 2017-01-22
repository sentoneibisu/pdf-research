#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os

def create_keyword_table(cur):
    with open('english.txt', 'r') as f:
        keywords = [line.strip() for line in f]

    for keyword in keywords:
        cur.execute("insert into search_keyword (keyword) values (?)", (keyword,))


def create_domain_table(cur):
    with open('domain.txt', 'r') as f:
        domains = [line.strip() for line in f]

    for domain in domains:
        cur.execute("insert into search_domain (domain) values (?)", (domain,))


def create_db():
    dbname = 'crawl.db'
    if os.path.exists(dbname):
        conn = sqlite3.connect('crawl.db', isolation_level=None)
        cur = conn.cursor()
    else:
        conn = sqlite3.connect('crawl.db', isolation_level=None)
        cur = conn.cursor()
        schema_fname = 'pdfs_schema.sql'
        with open(schema_fname, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        # 検索キーワードテーブルと検索ドメインテーブルの作成
        create_keyword_table(cur)
        create_domain_table(cur)
    return (conn, cur)


if __name__ == '__main__':
    conn, cur = create_db()
    conn.close()

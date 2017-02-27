#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os

def create_keyword_table(cur):
    with open('english2.txt', 'r') as f:
        keywords = [line.strip() for line in f]

    for keyword in keywords:
        cur.execute("insert into search_keyword (keyword) values (?)", (keyword,))


def create_db():
    dbname = 'crawl.db'
    if os.path.exists(dbname):
        conn = sqlite3.connect('crawl.db', isolation_level=None)
        cur = conn.cursor()
        schema_fname = 'pdfs_schema_only_SKT.sql'
        with open(schema_fname, 'r') as f:
            schema = f.read()

        conn.executescript(schema)
        # 検索キーワードテーブルの作成
        create_keyword_table(cur)
    return (conn, cur)


if __name__ == '__main__':
    conn, cur = create_db()
    conn.close()

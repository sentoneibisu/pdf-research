#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import sqlite3
import urllib
import traceback

f_log = open('log_download_pdf.log', 'w')

def write_log(message):
    f_log.write(message)


def open_db():
    conn = sqlite3.connect('crawl.db', isolation_level=None)
    write_log('[+] Open: crawl.db\n')
    cur = conn.cursor()
    return (conn, cur)


def close_db(conn):
    conn.close() 
    write_log('[+] Close: crawl.db\n')


def get_url(url):
    try:
        urllib.urlretrieve(url, './pdfs/{0}'.format(os.path.basename(url)))
        write_log('[Log] Saving Success: {0}\n'.format(os.path.basename(url)))
        return True
    except IOError:
        write_log('[Error-Log] Saving Error: {0}\n'.format(os.path.basename(url)))
        return False


def download_pdfs():
    try:
        conn, cur = open_db()
    
        while True:
            cur.execute("select id, url from pdfs where status=0")
            for id, url in cur.fetchall():
                if get_url(url):
                    cur.execute("update pdfs set status=1 where id=?", (id,))
                else:
                    cur.execute("update pdfs set status=-1 where id=?", (id,))
                    raise IOError
            time.sleep(10)

    except:
        write_log('[EXCEPT] {0}\n'.format(traceback.format_exc(sys.exc_info()[2])))
    finally:
        close_db(conn)
        f_log.close()


if __name__ == '__main__':
    download_pdfs()

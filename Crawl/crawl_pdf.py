#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import sqlite3
import traceback
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

f_log = open('log_crawl_pdf.log', 'w')

def save_state(keyword, start):
    # 現在の検索対象ドメインとページ数を保存
    # やむを得ずプログラムを途中停止するときにこの関数を呼ぶ
    pass

def write_log(message):
    f_log.write(message)
    f_log.flush()


def open_db():
    write_log('[DEBUG] call: open_db()\n')
    dbname = 'crawl.db'
    if os.path.exists(dbname):
        conn = sqlite3.connect('crawl.db', isolation_level=None)
        write_log('[+] Open: crawl.db\n')
        cur = conn.cursor()
    else:
        conn = sqlite3.connect('crawl.db', isolation_level=None)
        write_log('[+] Open: crawl.db\n')
        cur = conn.cursor()
        schema_fname = 'pdfs_schema.sql'
        with open(schema_fname, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        write_log('[+] Executescript: pdfs_schema.sql\n')
    return (conn, cur)


def insert_record(cur, url):
    write_log('[DEBUG] call: insert_record("cur", {0})\n'.format(url))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("insert into pdfs (url, add_date) values (?, ?)", (url, current_time))
    write_log('[+] Insert Record: {0}\n'.format(url))


def close_db(conn):
    write_log('[DEBUG] call: close_db("conn")\n')
    conn.close() 
    write_log('[+] Close: crawl.db\n')


def google_search(keywords):
    try:
        conn, cur = open_db()
        #driver = webdriver.PhantomJS()
        debug_count = 0
        for keyword in keywords:
            not_found_count = 0
            bot_check_count = 0
            start = 0
            while True:
                write_log('[DEBUG] Count: {0}\n'.format(debug_count))
                debug_count += 1
                driver = webdriver.PhantomJS()
                url = 'http://www.google.co.jp#q=' + keyword.replace(' ', '+') + '&filter=0&start={0}'.format(start) 
                start += 10
        
                driver.get(url)
                time.sleep(15)
                driver.save_screenshot('ss.png')
                html = driver.page_source.encode('utf-8')
                bsObj = BeautifulSoup(html, "html.parser")

                with open('html.html', 'w') as f:
                    f.write(bsObj.prettify().encode('utf-8'))
                print '[+]', bsObj.get_text()

                aList = bsObj.findAll('a', {'href': re.compile(r'.*\.pdf')})
                if not aList:
                    # bot対策画面
                    if u'通常と異なるトラフィックが検出されました。' in bsObj.get_text():
                        if bot_check_count == 0:    # CAPTCHA1回目
                            write_log('[DEBUG] bot_check_count: 1\n')
                            write_log('[DEBUG] sleep 30[min]...\n')
                            time.sleep(1800)
                            bot_check_count += 1
                        elif bot_check_count == 1:  # CAPTCHA2回目
                            write_log('[DEBUG] bot_check_count: 2\n')
                            write_log('[DEBUG] sleep 60[min]...\n')
                            time.sleep(3600)
                            bot_check_count += 1
                        else:   # CAPTCHA3回目
                            write_log('[DEBUG] bot_check_count: 3\n')
                            write_log('[+] Exit: BOT CHECK over 60[min] :(\n')
                            return
                        start -= 10
                        continue
                    pList = bsObj.findAll('p')
                    for p in pList:
                        print '[+]', p.get_text()
                        # Not Found画面
                        if u'に一致する情報は見つかりませんでした。' in p.get_text():
                            not_found_count += 1
                    # 検索結果にPDFがなかっただけ
                    if not_found_count == 0:
                        continue
                    # Not Found画面
                    elif not_found_count == 1:
                        write_log('[DEBUG] not_found_count: 1\n')
                        write_log('[DEBUG] sleep 30[min]...\n')
                        time.sleep(1800)
                        start -= 10
                        continue
                    # Not Found画面 * 2
                    else:
                        write_log('[DEBUG] not_found_count: 2\n')
                        # (普通に)最後まで検索し終えた
                        break
                not_found_count = 0
                bot_check = 0
                for a in aList:
                    if a.get_text() not in (u'類似ページ', u'キャッシュ'):
                        m = re.search(r'<a href="/url\?q=(.+\.pdf).+">', str(a))
                        pdf_url = m.group(1)
                        insert_record(cur, pdf_url)
                driver.quit()
    except:
        print '[EXCEPT]', traceback.format_exc(sys.exc_info()[2])
        write_log('[EXCEPT] {0}\n'.format(traceback.format_exc(sys.exc_info()[2])))
    finally:
        #driver.quit()
        close_db(conn)
        f_log.close()


if __name__ == '__main__':
    keywords = ['site:ac.jp filetype:pdf',
                'site:co.jp filetype:pdf',
                'site:go.jp filetype:pdf',
                'site:or.jp filetype:pdf',
                'site:ad.jp filetype:pdf',
                'site:ne.jp filetype:pdf',
                'site:gr.jp filetype:pdf',
                'site:ed.jp filetype:pdf',
                'site:lg.jp filetype:pdf']
    #keywords = ['site:gr.jp filetype:pdf']
    google_search(keywords)

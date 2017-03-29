#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import pickle
import sqlite3
import traceback
import random
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

f_log = open('log_crawl_pdf.log', 'w')

def save_state(keyword, domain, start):
    # 現在の検索対象ドメインとページ数を保存
    # やむを得ずプログラムを途中停止するときにこの関数を呼ぶ
    with open('pickle.dump', 'wb') as f:
        pickle.dump([keyword, domain, start], f)

def restore_state():
    with open('pickle.dump', 'rb') as f:
        keyword, domain, start = pickle.load(f)
    return (keyword, domain, start)


def write_log(message):
    f_log.write(message)
    f_log.flush()


def open_db():
    write_log('[+] call: open_db()\n')
    dbname = 'resource/crawl.db'
    conn = sqlite3.connect(dbname, isolation_level=None)
    write_log('[+] Open: {0}\n'.format(dbname))
    cur = conn.cursor()
    return (conn, cur)


def fetch_domain(cur):
    # search_domainテーブルからstatus=0な検索ドメインをfetchする
    cur.execute("select domain from search_domain where status=0")
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        return None


def fetch_keyword(cur):
    # search_keywordテーブルからstatus=0な検索キーワードをfetchする
    cur.execute("select keyword from search_keyword where status=0")
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        return None


def reset_status_keyword_table(cur):
    # search_keywordテーブル内の全キーワードのstatusを0に戻す
    cur.execute("update search_keyword set status=0")


def set_status_keyword_table(cur, keyword):
    # 引数keywordで指定されたレコードのstatusを1にする
    cur.execute("update search_keyword set status=1 where keyword=?", (keyword,))


def set_status_domain_table(cur, domain):
    # 引数domainで指定されたレコードのstatusを1にする
    cur.execute("update search_domain set status=1 where domain=?", (domain,))


def insert_record(cur, url, keyword, domain):
    write_log('[+] call: insert_record("cur", {0}, {1}, {2})\n'.format(url, keyword, domain))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("insert into url (url, add_date, keyword, domain) values (?, ?, ?, ?)", (url, current_time, keyword, domain))
    write_log('[+] Insert Record: {0}\n'.format(url))


def close_db(conn):
    write_log('[+] call: close_db("conn")\n')
    conn.close() 
    write_log('[+] Close: resource/crawl.db\n')


def google_search(restore_flg):
    try:
        conn, cur = open_db()
        debug_count = 0
        driver = webdriver.Chrome()
        # 検索ドメイン毎のループ
        while True:
            if not restore_flg:
                domain = fetch_domain(cur)
                if not domain:  # 全ドメイン検索終了
                    break
                reset_status_keyword_table(cur)

            # 検索キーワード毎のループ
            while True:
                if not restore_flg:
                    keyword = fetch_keyword(cur)
                    if not keyword:  # 全キーワード検索終了
                        break
                    start = 0

                not_found_count = 0
                # 検索処理のループ
                while True:
                    if restore_flg:
                        keyword, domain, start = restore_state()  # 状態の復元
                        restore_flg = False
                    if start >= 30:
                        break
                    write_log('[+] Count: {0}\n'.format(debug_count))
                    debug_count += 1
                    url = 'https://www.google.co.jp' + \
                          '#q={0}+site:{1}+filetype:pdf'.format(keyword, domain) + \
                          '&filter=0&start={0}'.format(start) 
                    start += 10
            
                    driver.get(url)
                    time.sleep(random.randint(1, 2))
                    driver.save_screenshot('ss.png')
                    html = driver.page_source.encode('utf-8')
                    bsObj = BeautifulSoup(html, "html.parser")
    
                    with open('html.html', 'w') as f:
                        f.write(bsObj.prettify().encode('utf-8'))
    
                    aList = bsObj.findAll('a', {'href': re.compile(r'.*\.pdf')})
                    if not aList:
                        # bot対策画面の検出
                        if u'通常と異なるトラフィックが検出されました。' in bsObj.get_text():
                            write_log('[+] Exit: BOT CHECK Detected :(\n')
                            return
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
                        #elif not_found_count == 1:
                        #    write_log('[+] not_found_count: 1\n')
                        #    write_log('[+] sleep 30[min]...\n')
                        #    time.sleep(1800)
                        #    start -= 10
                        #    continue
                        # Not Found画面 * 2
                        else:
                        #    write_log('[+] not_found_count: 2\n')
                            write_log('[+] Not Found\n')
                            # (普通に)最後まで検索し終えた
                            break
                    not_found_count = 0
                    for a in aList:
                        if a.get_text() not in (u'類似ページ', u'キャッシュ', u'このページを訳す'):
                            m_img = re.search(r'<a class="bia uh_rl"', str(a))
                            if m_img:  # 検索結果に画像検索が埋め込まれていた場合は無視
                                continue
                            m = re.search(r'<a href="(.+\.pdf).+">', str(a))
                            if m is None:
                                print '[DEBUG] ', a
                                continue
                            pdf_url = m.group(1)
                            insert_record(cur, pdf_url, keyword, domain)

                set_status_keyword_table(cur, keyword)

            set_status_domain_table(cur, domain)

    except:
        print '[EXCEPT]', traceback.format_exc(sys.exc_info()[2])
        write_log('[EXCEPT] {0}\n'.format(traceback.format_exc(sys.exc_info()[2])))
    finally:
        save_state(keyword, domain, start-10)
        driver.quit()
        close_db(conn)
        f_log.close()


if __name__ == '__main__':
    if os.path.exists('pickle.dump'):
        restore_flg = True
    else:
        restore_flg = False
    google_search(restore_flg)

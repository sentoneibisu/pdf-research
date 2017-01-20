# PDFクローラー
## プログラム内で使用しているテーブル
### 一覧
 - URLテーブル(url_table)
 - 検索キーワードテーブル(keyword_table)
 - 検索ドメインテーブル(domain_table)

### URLテーブル(url_table)
クローラーで取得したPDFファイルのURLを格納するテーブル。STATUSは、ダウンロード済みか否かの判断に使用する。

| ID | URL | DATE | STATUS | Search Keyword | Search Domain |
|:--:|:----|:----:|:------:|:--:|:--:|
|1| http://hoge.com |2017-01-18|False|apple|ac.jp|
|2| http://www.fuga.co.jp |2017-01-19|False|banana|ac.jp|
|3| http://fuga.ac.jp |2017-01-19|False|lemon|ac.jp|
|4| http://www.fugafuga.co.jp |2017-01-19|False|melon|ac.jp|

### 検索キーワードテーブル(keyword_table)
検索対象のキーワード一覧を事前に格納しておくテーブル。
検索キーワードは辞書攻撃用に作成された辞書ファイル(English)を使用する。
STATUSは、検索が終了していることを示すフラグとして利用する。

| ID | Keywords | STATUS |
|:--:|:--:|:--:|
|1|apple|True|
|2|banana|True|
|3|lemon|False|
|3|melon|False|

### 検索ドメインテーブル(domain_table)
検索対象のドメイン一覧を事前に格納しておくテーブル。
STATUSは、検索が終了していることを示すフラグとして利用する。

| ID | Domain | STATUS |
|:--:|:--:|:--:|
|1|ac.jp|True|
|2|co.jp|False|
|3|go.jp|False|

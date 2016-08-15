# coding: UTF-8

"""
カレントディレクトリ内の*.pdfのファイル全てをpdftkでuncompressし，
XXX.pdf -> XXX_uncompressed
と名前を変更して保存する．
"""

import glob
import subprocess

pdf_list = glob.glob('*.pdf')    # カレントディレクトリ内の.pdfファイルをリストの形で取り出す
for pdf in pdf_list:             # uncompress処理
    pdf = pdf.replace('(', '\(')    # 左カッコのエスケープ
    pdf = pdf.replace(')', '\)')    # 右カッコのエスケープ
    output_file = pdf[:-4] + '_uncompressed'
    ret_code = subprocess.call(['pdftk', pdf, 'output', output_file, 'uncompress'])     # pdftkの実行
    cmd = 'pdftk %s output %s uncompress' % (pdf,output_file)
    if ret_code:
        print '[*] Error: %s' % cmd
    else:
        print '[*] Success: %s' % cmd

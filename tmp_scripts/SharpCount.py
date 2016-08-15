#!/usr/bin/python

"""

PDF内(streamを除く)に含まれる#[a-fA-F0-9]{2} ('#20'を除く)の数をカウント

"""

import sys
import re
import regex
import zlib

current_obj = ''
streams = {}
parsed = {}
paths = {}
# for detection of loop
passed_obj = []

pIndRef = re.compile(r'\s*([0-9]+\s+0\s+R)\s*')
pName = re.compile(r'\s*(/[^()<>/\[\]\s]*)\s*')
pNum_null_bool = re.compile(r'\s*([\d+-.]+|null|false|true)\s*')
pID = re.compile(r'\s*(<[a-zA-Z0-9]+>\s*<[a-zA-Z0-9]+>)\s*')
pString2 = re.compile(r'\s*(<\s*([a-zA-Z0-9,]\s*)*>)\s*')
pString = regex.compile(r'\s*(?<str>\((?:[^()\\]+|[\\].?|(?&str))*\))\s*')
pDict = regex.compile(r'\s*(?<dic><<((?:[^<>(]+(?:[<>]?|><|<>))*|(?&str)|(?&dic))*>>)\s*'
                      r'(?<str>\((?:[^()\\]+|[\\].|(?&str))*\)){0}')
pArray = regex.compile(r'\s*(?<arr>\[(?:[^\[\](]*|(?&str)|(?&arr))*\])\s*'
                       r'(?<str>\((?:[^()\\]+|[\\].|(?&str))*\)){0}')
pTrailer = regex.compile(r'\s*trailer\s*(?<dic><<((?:[^<>(]+(?:[<>]?|><|<>))*|(?&str)|(?&dic))*>>)\s*'
                      r'(?<str>\((?:[^()\\]+|[\\].|(?&str))*\)){0}')

##############################################################################################################################
def Main():
    global current_obj
    target_pdf = sys.argv[1]

    if len(sys.argv) > 2:
        target_pdf = ""
        for x in sys.argv[1:]:
            target_pdf += x
            target_pdf += ' '
        target_pdf = target_pdf[:-1]
    try:
        with open(target_pdf,'rb') as f:
            data = f.read()
    except IOError:
        print 'nan'
        sys.exit(1)

    with open(target_pdf,'rb') as f:
        data = f.read()

    count2dHex = 0
    trailers = pTrailer.findall(data)
    for trailer in trailers:
        #print trailer[0]
        count2dHex += CountTwoDigitHex(trailer[0])
    
    
    objs = re.findall(r'\n?(\d+)\s+(\d+)\s+obj[\s]*(.*?)\s*\n?(endobj|objend)', data, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    # obj : ['1','0','obj data']
    for obj in objs:
        current_obj = obj[0]+' '+obj[1]
    
        streams[current_obj] = re.findall(r'(?:stream[\r\n]*(.*?)[\r\n]*endstream)', obj[2], re.MULTILINE | re.DOTALL | re.IGNORECASE)
        non_stream_data = re.sub(r'stream[\r\n]*.*?[\r\n]*endstream', '', obj[2], flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
        count2dHex += CountTwoDigitHex(non_stream_data)
    print 'Number of 2-digit hexadecimal :',count2dHex

##############################################################################################################################
def CountTwoDigitHex(data):
    TDHs = re.findall(r'(#[a-fA-F0-9]{2})', data)
    count = 0
    for TDH in TDHs:
        if TDH != '#20':
            #print TDH,
            count += 1
    return count

Main()

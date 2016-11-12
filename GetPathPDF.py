#!/usr/bin/python
# -*- coding: utf-8 -*-
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

#output_file = open('a.txt', 'w')

##############################################################################################################################
def Main():
    global current_obj

    # ファイル名に空白が含まれていた場合，コマンドライン引数として分割されてしまうため，
    # それらを空白で連結して一つの文字列にする (ただしファイル名に空白が連続2つ以上ある場合には未対応)
    if len(sys.argv) == 1:
        print '[+] Usage: ./GetPathPDF.py PDF_FILE'
        sys.exit(1)
    elif len(sys.argv) == 2:
        target_pdf = sys.argv[1]
    else:
        target_pdf = ' '.join(sys.argv[1:])
    try:
        with open(target_pdf,'rb') as f:
            data = f.read()
    except IOError:
        print 'nan'
        sys.exit(1)

    objs = re.findall(r'\n?(\d+)\s+(\d+)\s+obj[\s]*(.*?)\s*\n?(endobj|objend)', data, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    # (Example) obj : ['1','0','(obj data)']
    for obj in objs:
        current_obj = obj[0]+' '+obj[1]
    
        streams[current_obj] = re.findall(r'(?:stream[\r\n]*(.*?)[\r\n]*endstream)', obj[2], re.MULTILINE | re.DOTALL | re.IGNORECASE)
        non_stream_data = re.sub(r'stream[\r\n]*.*?[\r\n]*endstream', '', obj[2], flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
        non_stream_data = NameDeObf(non_stream_data)

        try:
            parsed[current_obj] = ParseObj(non_stream_data)
        except:
            print 'sys.exc_info():'
            print sys.exc_info()
            continue

        ###PrintObjs()

        paths[current_obj] = []
        CreatePath(parsed[current_obj])

        inner_objects = DecodeObjStm()
        if inner_objects:
            ParseObjStm(inner_objects)

    PrintAllPath()

##############################################################################################################################
"""
ignore
         #20 : space
         #28 : (
         #29 : )
         #2f : /
         #3c : <
         #3e : >
         #5b : [
         #5d : ]
"""
def NameDeObf(data):
    return re.sub(r'#([a-fA-F0-9]{2})',\
                  lambda mo: chr(int('0x' + mo.group(1), 0))\
                  if mo.group(1).lower() not in  ('20','28','29','2f','3c','3e','5b','5d') else '#' + mo.group(1),\
                  data)

##############################################################################################################################
def PrintObjs():
    if type(parsed[current_obj]) == dict:
        for key in parsed[current_obj].keys():
            print '%19s : %-19s' % (key,parsed[current_obj][key])
    elif type(parsed[current_obj]) == list:
            print parsed[current_obj]

##############################################################################################################################
def ParseObj(contents):
    if contents[0:2] == '<<':
        p = ParseDict(contents[2:-2])
        for x in p.keys():
            p[x] = ParseObj(p[x])
            #print '%19s : %-19s' % (x,p[x])
        return p
    
    elif contents[0] == '[':
        l = ParseArray(contents[1:-1])
        for x in xrange(len(l)):
            l[x] = ParseObj(l[x])
        return l
    else:
        return contents

##############################################################################################################################
def ParseDict(contents):
    left_size = 0
    pairs = {}
    while True:
        mName = pName.match(contents[left_size:])
        if not mName:
            break
        left_size += len(mName.group())

        pRight = re.compile(r'\s*(.+)',re.DOTALL)
        mRight = pRight.match(contents[left_size:])

        if not mRight.group(1)[0] in '<[(':
            if mRight.group(1)[0] == '/':
                mPair = pName.match(mRight.group())
                pairs[mName.group(1)] = mPair.group(1)
            else:
                mPair = pIndRef.match(mRight.group())
                if mPair:
                    # indirect ref
                    pairs[mName.group(1)] = mPair.group(1)
                else:
                    # number or null or bool
                    mPair = pNum_null_bool.match(mRight.group())
                    if mPair:
                        pairs[mName.group(1)] = mPair.group(1)
                    else:
                        print '[ParseError]Missing! in ParseDict()'
                        raise Exception
        elif mRight.group(1)[0] == '(':
            # string
            mPair = pString.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        elif mRight.group(1)[0:2] == '<<':
            # dictionary
            mPair = pDict.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        elif mRight.group(1)[0] == '[':
            # array
            mPair = pArray.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        else:
            # ID or string
            mPair = pID.match(mRight.group())
            if mPair:
                pairs[mName.group(1)] = mPair.group(1)
            else:
                mPair = pString2.match(mRight.group())
                pairs[mName.group(1)] = mPair.group(1)

        left_size += len(mPair.group())

    return pairs

##############################################################################################################################
def ParseArray(contents):
    left_size = 0
    array = []

    while True:

        pRight = re.compile(r'\s*(.+)',re.DOTALL)
        mRight = pRight.match(contents[left_size:])

        if not mRight:
            break

        if not mRight.group(1)[0] in '<[(':
            if mRight.group(1)[0] == '/':
                mElem = pName.match(mRight.group())
                array.append(mElem.group(1))
            else:
                mElem = pIndRef.match(mRight.group())
                if mElem:
                    # indirect ref
                    array.append(mElem.group(1))
                else:
                    # number or null or bool
                    mElem = pNum_null_bool.match(mRight.group())
                    if mElem:
                        array.append(mElem.group(1))
                    else:
                        if mRight.group(1) in ' \r\n':
                            # case of space only in array : (ex. <</ABC [ ]>>)
                            break
                        else:
                            print '[DEBUG] mRight.group():',mRight.group()
                            print 'Missing! in ParseArray()'
                            raise Exception
        elif mRight.group(1)[0] == '(':
            # string
            mElem = pString.match(mRight.group())
            array.append(mElem.group(1))

        elif mRight.group(1)[0:2] == '<<':
            # dictionary
            mElem = pDict.match(mRight.group())
            array.append(mElem.group(1))

        elif mRight.group(1)[0] == '[':
            # array
            mElem = pArray.match(mRight.group())
            array.append(mElem.group(1))

        else:
            # ID
            mElem = pID.match(mRight.group())
            if mElem:
                array.append(mElem.group(1))
            else:
                mElem = pString2.match(mRight.group())
                array.append(mElem.group(1))
           
        left_size += len(mElem.group())

    return array

##############################################################################################################################
def CreatePath(result):
    if type(result) == dict:
        CreateDictPath('',result)
    elif type(result) == list:
        CreateArrayPath('',result)
    else:
        return

    # muriyaridaga...
    while '' in paths[current_obj]:
        paths[current_obj].remove('')
    new_paths = []
    for path in paths[current_obj]:
        if not path in new_paths:
            new_paths.append(path)
    paths[current_obj] = sorted(new_paths)
    
    for i,path in enumerate(paths[current_obj]):
        try:
            if path+'/' in paths[current_obj][i+1]:
                del paths[current_obj][i]
        except:
            pass

##############################################################################################################################
def CreateDictPath(parent,child):
    for brother in child.keys():
        if type(child[brother]) == dict:
            CreateDictPath(parent+brother,child[brother])
        elif type(child[brother]) == list:
            CreateArrayPath(parent+brother,child[brother])
        else:
            CreateAtherPath(parent+brother,child[brother])

##############################################################################################################################
def CreateArrayPath(parent,child):
    for brother in child:
        if type(brother) == dict:
            CreateDictPath(parent,brother)
        elif type(brother) == list:
            CreateArrayPath(parent,brother)
        else:
            CreateAtherPath(parent,brother)

##############################################################################################################################
def CreateAtherPath(parent,child):
    m = pIndRef.match(child)
    if m:
        paths[current_obj].append(parent+'/'+child)
    else:
        paths[current_obj].append(parent)

##############################################################################################################################
def PrintAllPath():
    catalog_obj_num = SearchCatalog()
    if catalog_obj_num == None:
        print '[ERROR]Catalog is not found.'
        sys.exit(1)

    ResolvePath(catalog_obj_num)

##############################################################################################################################
def SearchCatalog():
    for obj_num in parsed.keys():
        if type(parsed[obj_num]) == list or type(parsed[obj_num]) == str:
            continue
        for key in parsed[obj_num].keys():
            if key == '/Type' and parsed[obj_num][key] == '/Catalog':
                return obj_num

            # When present under the /OpenAction
            else:
                if key == '/OpenAction':
                    try:
                        for child_key in parsed[obj_num]['/OpenAction'].keys():
                            if child_key == '/Type' and parsed[obj_num]['/OpenAction'][child_key] == '/Catalog':
                                return obj_num
                    # When there is list object under the /OpneAction
                    except AttributeError:
                        pass
    return None

##############################################################################################################################
def ResolvePath(key,parent_path=''):
    global passed_obj
    if key in passed_obj:
        #output_file.write(parent_path + '\n')
        print parent_path
        return
    passed_obj.append(key)
    try:
        for path in paths[key]:
            m = pIndRef.search(path)
            if m:
                p_path = parent_path + path[:m.start()-1]
                child_key = m.group()[:-2]
                ResolvePath(child_key,p_path)
                continue
            else:
                print parent_path + path
                #output_file.write(parent_path + path + '\n')
        passed_obj.pop()
    except KeyError:
        print parent_path+'/'+key+' R'+' -------------------> '+key+' R'+' Not Found'

##############################################################################################################################
def DecodeObjStm():
    decompressed_data = '' 
    if streams[current_obj]:
        try:
            if parsed[current_obj]['/Type'] == '/ObjStm':
                if parsed[current_obj]['/Filter'] == '/FlateDecode' or parsed[current_obj]['/Filter'] == '/Fl':
                    decompressed_data = zlib.decompress(streams[current_obj][0])
        except:
            pass
    return decompressed_data

##############################################################################################################################
def ParseObjStm(inner_objects):
    global current_obj
    p = re.compile(r'\s*(?P<num>[0-9]+)\s+(?P<offset>[0-9]+)\s*')
    left_size = 0
    inner_offsets = []

    while True:
        m = p.match(inner_objects[left_size:])
        if not m:
            break
        left_size += len(m.group())
        inner_offsets.append((m.group('num'),m.group('offset')))

    for key,offset in inner_offsets:
        current_obj = key + ' ' + '0'

        m = pDict.match(inner_objects[left_size:])
        if m:
            left_size += len(m.group())
        else:
            m = pArray.match(inner_objects[left_size:])
            if m:
                left_size += len(m.group())
            else:
                print '[DEBUG] The Object in this ObjStm is not Dict and Array.'
                sys.exit(1)

        try:
            parsed[current_obj] = ParseObj(m.group(1))
        except:
            print '[ObjStm]sys.exc_info():'
            print sys.exc_info()
            print 'm.group(1):'
            print m.group(1)
            continue
        ###PrintObjs()

        paths[current_obj] = []
        CreatePath(parsed[current_obj])

Main()
#output_file.close()

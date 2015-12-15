#!/usr/bin/python
import sys
import re
import regex

streams = {}
parsed = {}
paths = {}
all_path = []
passed_obj = []
# for detection of loop

pIndRef = re.compile(r'\s*([0-9]+\s+0\s+R)\s*')
#pName = re.compile(r'\s*(/[^()<>/\[\]\s]+)\s*')
pName = re.compile(r'\s*(/[^()<>/\[\]\s]*)\s*')
pNum_null_bool = re.compile(r'\s*([\d+-.]+|null|false|true)\s*')
pID = re.compile(r'\s*(<[a-zA-Z0-9]+>\s*<[a-zA-Z0-9]+>)\s*')
#pString2 = re.compile(r'\s*(<[a-zA-Z0-9]+>)\s*')
pString2 = re.compile(r'\s*(<([a-zA-Z0-9]{2}\s*)+>)\s*')
# zenntei : mojiretu nado no naka ni '(' ya ')' ya '<' ya '>' ya '[' ya ']' ga nai koto!!
pString = regex.compile(r'\s*(?<rec>\((?:[^()]+|(?&rec))*\))\s*')
#pDict = regex.compile(r'\s*(?<rec><<(?:[^<>]+|(?&rec))*>>)\s*')
pDict = regex.compile(r'\s*(?<rec><<(?:(?:[^<>]+(?:[<>]?|><|<>))+|(?&rec))*>>)\s*')
#pArray = regex.compile(r'\s*(?<rec>\[(?:[^\[\]]+|(?&rec))*\])\s*')
pArray = regex.compile(r'\s*(?<rec>\[(?:[^\[\]]*|(?&rec))*\])\s*')

def Main():
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


    print '[*] open : %s' % target_pdf[-30:]
    with open(target_pdf,'rb') as f:
        data = f.read()
    
    objs = re.findall(r'\n?(\d+)\s+(\d+)\s+obj[\s]*(.*?)\s*\n?(endobj|objend)', data, re.MULTILINE | re.DOTALL)
    # obj : ['1','0','obj data']
    for obj in objs:
        ##print '-'*138
        global current_obj
        current_obj = obj[0]+' '+obj[1]
        ##print current_obj + ' ' + 'obj'
    
        streams[current_obj] = re.findall(r'(?:stream[\r\n]*(.*?)[\r\n]*endstream)', obj[2], re.MULTILINE | re.DOTALL | re.IGNORECASE)
        non_stream_data = re.sub(r'stream[\r\n]*.*?[\r\n]*endstream', '', obj[2], flags=(re.MULTILINE | re.DOTALL | re.IGNORECASE))
        non_stream_data = NameDeObf(non_stream_data)

        try:
            parsed[current_obj] = ParseObj(non_stream_data)
        except:
            continue

        PrintObjs()

        paths[current_obj] = []
        CreatePath(parsed[current_obj])

        ##print '--path--'
        ##for path in paths[current_obj]:
        ##    print path

    #print
    print '--ALL PATH--'
    PrintAllPath()


def NameDeObf(data):
    return re.sub(r'#([a-fA-F0-9]{2})', lambda mo: chr(int('0x' + mo.group(1), 0)), data)

def PrintObjs():
    if type(parsed[current_obj]) == dict:
        for key in parsed[current_obj].keys():
            pass
            ##print '%19s : %-19s' % (key,parsed[current_obj][key])
    elif type(parsed[current_obj]) == list:
            pass
            ##print parsed[current_obj]

    
def ParseObj(contents):
    if contents[0:2] == '<<':
        p = ParseDict(contents[2:-2])
        for x in p.keys():
            p[x] = ParseObj(p[x])
            #print '%19s : %-19s' % (x,p[x])
        return p
    
    elif contents[0] == '[':
        l = ParseArray(contents[1:-1])
        #print '[',
        for x in xrange(len(l)):
            l[x] = ParseObj(l[x])
            #print '%s,' % (l[x]),
        #print ']'
        return l
    else:
        return contents


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
                        print 'Missing! in ParseDict()'
                        #sys.exit(1)
                        raise Exception
        elif mRight.group(1)[0] == '(':
            # string
            mPair = pString.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        elif mRight.group(1)[0:2] == '<<':
            # dictionaly
            mPair = pDict.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        elif mRight.group(1)[0] == '[':
            # array
            mPair = pArray.match(mRight.group())
            pairs[mName.group(1)] = mPair.group(1)

        else:
            # ID
            mPair = pID.match(mRight.group())
            if mPair:
                pairs[mName.group(1)] = mPair.group(1)
            else:
                mPair = pString2.match(mRight.group())
                pairs[mName.group(1)] = mPair.group(1)

        left_size += len(mPair.group())

    return pairs


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
                        if mRight.group(1) == ' ':
                            # case of space only in array : (ex. <</ABC [ ]>>)
                            break
                        else:
                            print '[DEBUG] mRight.group():',mRight.group()
                            print 'Missing! in ParseArray()'
                            #sys.exit(1)
                            raise Exception
        elif mRight.group(1)[0] == '(':
            # string
            mElem = pString.match(mRight.group())
            array.append(mElem.group(1))

        elif mRight.group(1)[0:2] == '<<':
            # dictionaly
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
    # muriyaridaga...
    new_paths = []
    for path in paths[current_obj]:
        if not path in new_paths:
            new_paths.append(path)
    paths[current_obj] = sorted(new_paths)
    
    for i,path in enumerate(paths[current_obj]):
        try:
            #if paths[current_obj][i+1].starswith(path):
            if path in paths[current_obj][i+1]:
                del paths[current_obj][i]
        except:
            pass



def CreateDictPath(parent,child):
    for brother in child.keys():
        if type(child[brother]) == dict:
            CreateDictPath(parent+brother,child[brother])
        elif type(child[brother]) == list:
            CreateArrayPath(parent+brother,child[brother])
        else:
            CreateAtherPath(parent+brother,child[brother])

def CreateArrayPath(parent,child):
    for brother in child:
        if type(brother) == dict:
            CreateDictPath(parent,brother)
        elif type(brother) == list:
            CreateArrayPath(parent,brother)
        else:
            CreateAtherPath(parent,brother)

def CreateAtherPath(parent,child):
    #if parent == '':
    #    return
    m = pIndRef.match(child)
    if m:
        paths[current_obj].append(parent+'/'+child)
    else:
        paths[current_obj].append(parent)


def PrintAllPath():
    catalog_obj_num = SearchCatalog()
    ##print 'catalog_obj_num:',catalog_obj_num

    ResolvePath(catalog_obj_num)
    for path in all_path:
        print path


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


def ResolvePath(key,parent_path=''):
    global passed_obj
    if key in passed_obj:
        #print passed_obj
        #print '[DEBUG] Detection Loop : ',parent_path
        all_path.append(parent_path)
        return
    passed_obj.append(key)
    ##print passed_obj
    try:
        for path in paths[key]:
            m = pIndRef.search(path)
            if m:
                p_path = parent_path + path[:m.start()-1]
                child_key = m.group()[:-2]
                ResolvePath(child_key,p_path)
                #print 'child_key:',child_key
                #print p_path
                continue
            else:
                all_path.append(parent_path+path)
                #print parent_path+path
        passed_obj.pop()
    except KeyError:
        try:
            all_path.append(parent_path+'/'+key+' R'+' -------------------> '+key+' R'+' Not Found')
        except:
            print "ERROR!!!!!!!!"

Main()

#!/usr/bin/python
import re
import sys

target_pdf = sys.argv[1]
print '[*] open : %s' % target_pdf
with open(target_pdf,'rb') as f:
    data = f.read()

objs = re.findall('\n?(\d+)\s+(\d+)\s+obj[\s]*(.*?)\s*\n?(endobj|objend)', data, re.MULTILINE | re.DOTALL)
obj_dict = {}
obj_keys = []
for obj in objs:
    key = obj[0] + ' ' + obj[1]
    obj_keys.append(key)
    obj_dict[key] = obj[2]
    print '[*] %s' % key

print 'input any key = >'
target_key = raw_input()
print '%s obj' % target_key
print obj_dict[target_key]


#tags = re.findall('<<(.*)>>[\s\r\n%]*(?:stream[\r\n]*(.*?)[\r\n]*endstream)?', self.indata, re.MULTILINE | re.DOTALL | re.IGNORECASE)


#!/bin/sh
objname=${1:-objname}
od -A n -v -t x1 $1
od -A n -v -t x1 $1 | sed -e '1i\
const unsigned char '$objname'[] = {
s/\([0-9a-f][0-9a-f]\)/0x\1,/g
$s/,$//
$a\
};
'


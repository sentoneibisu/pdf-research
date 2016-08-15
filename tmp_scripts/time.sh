#!/bin/bash

TAR_PDF=$1
SECONDS=0
./pdf_parse_v2.py $1
time=$SECONDS
echo 'time:'$time'[sec]'

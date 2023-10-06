#!/bin/bash
ps -ef |grep "3.py 0 3999" | grep -v grep | awk '{print $2}' > pids.txt
ps -ef | grep '3.py 3999 7999' | grep -v grep | awk '{print $2}' >> pids.txt
ps -ef | grep '3.py 7999 11999' | grep -v grep | awk '{print $2}' >> pids.txt
ps -ef | grep '3.py 11999 15999' | grep -v grep | awk '{print $2}' >> pids.txt
ps -ef | grep '3.py 15999 19999' | grep -v grep | awk '{print $2}' >> pids.txt
ps -ef | grep '3.py 19999 22999' | grep -v grep | awk '{print $2}' >> pids.txt
ps -ef | grep 'price.py' | grep -v grep | awk '{print $2}' >> pids.txt


while IFS= read -r line; do
    kill -9 $line
done < pids.txt

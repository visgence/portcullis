#!/usr/bin/python

#System Imports
import sys
import re
import fileinput

def in_search(line, stmts):
    for s in stmts:
        if(re.match('^INSERT INTO "*' + s, line)):
            return True

    return False

stmtList = ['scaling_functions', 'data_streams', 'snmpPoller_host', 'snmpPoller_snmpstream']

for line in fileinput.input():
    line = line.rstrip()

    if(in_search(line, stmtList)):
        print line




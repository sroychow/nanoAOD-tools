#!/usr/bin/env python
import commands
import time
import re
import os
import string
from os import listdir
from os.path import isfile, join
import sys
import argparse
import copy

parser = argparse.ArgumentParser("")
parser.add_argument('-r', '--restore', help="", action='store_true')
args = parser.parse_args()

modules = os.listdir('../modules/jme')
modules_py = [m for m in modules if m[-3:]=='.py' and '__init__' not in m]
print modules_py

files = modules_py
for f in files:
    if args.restore:
        print 'Restoring file '+f
        os.system('mv ../modules/jme/'+f+'.old ../modules/jme/'+f)
        continue
    os.system('cp ../modules/jme/'+f+' ../modules/jme/'+f+'.old')
    f_in  = open('../modules/jme/'+f, 'r')
    f_out = open('../modules/jme/'+f+'.new', 'w')
    f_lines = f_in.readlines()
    count = 0
    for line in f_lines:
        new_line = copy.deepcopy(line)
        if ('branch(' in line or 'fillBranch' in line) and 'jetBranchName' in line and 'pt_nom' not in line:
            pos = len(line) - len(line.lstrip())
            new_line = (line[:pos]+"pass #"+line[pos:])
            count += 1
        f_out.write(new_line)
    f_out.close()
    print 'Updating file '+f+' with '+str(count)+' commented lines'
    os.system('mv ../modules/jme/'+f+'.new ../modules/jme/'+f)

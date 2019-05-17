
# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import sys
import codecs   # For Unicode Processing
from os import listdir, makedirs
import glob
import re

c = 0
kgfolder = '../data/kangyur-all-normalized/*.txt'
ptn = r'\[\d+[ab]\]'
volptn = r'(\d+)-FINAL'
totalpg = 0
for fname in glob.glob(kgfolder):
    vol = re.search(volptn, fname, re.M | re.I)
    vol = vol.group(1).lstrip("0")
    ftxt = open(fname, 'r').read()
    pgs = re.findall(ptn, ftxt)
    pgs = len(pgs)
    sep = ","
    print "Vol " + vol + sep + str(pgs)
    totalpg += pgs

print "\nTotal pages in Kangyur: {0}".format(totalpg)

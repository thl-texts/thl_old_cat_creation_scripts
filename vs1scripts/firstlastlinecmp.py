# coding=utf-8
#

from THLTextProcessing import *

sttxt = False

while not sttxt:
    sttxt = input("Start text: ")
    if not sttxt.isdigit():
        sttxt = False
endtxt = False
while not endtxt:
    endtxt = input("End text: ")
    if not endtxt.isdigit():
        endtxt = False

print "{0} through {1}".format(sttxt, endtxt)
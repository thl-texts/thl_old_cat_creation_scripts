# coding=utf-8
#
#  Compares two text files line by line
#

# import os       # For Directory travelling
# import codecs   # For Unicode Processing
import re
from THLTextProcessing import THLPageIterator, THLSource, THLText  # Custom class for text processing
# from lxml import etree


def normspace(txt2norm=''):
    newtxt = re.sub("[\x00-\x20]+", "\x20", txt2norm)
    #newtxt = re.sub("\s", " ", newtxt)
    return newtxt

if __name__ == "__main__":

    base_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    texts_root = base_dir + "catalogs/xml/kt/d/"
    old_texts = texts_root + "texts/"
    new_texts = texts_root + "texts-new/"

    filenm = '0006/kt-d-0006-da-09.xml'
    pgroot = '201b'



    oldtext = THLText(old_texts + filenm)
    newtext = THLText(new_texts + filenm)
    #print normspace(newtext.getline(pagenum))
    for i in range(1, 2):
        pagenum = pgroot + "." + str(i)
        oldline = normspace(oldtext.getline(pagenum))
        newline = normspace(newtext.getline(pagenum))
        cnum = 0
        for ch in oldline.decode('utf-8'):
            print cnum, ch, newline[cnum].decode('utf-8')
            cnum += 1


        # if newline == oldline:
        #    print "{0} is identical".format(pagenum)
        # else:
         #   print "Different:"
         #   print oldline
         #   print newline
         #   if newline.find("/xA0") > -1:
         #       print "Found non-breaking space"


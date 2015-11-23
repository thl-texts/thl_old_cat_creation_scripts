# coding=utf-8
#
# Compares two text files line by line
#

import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import exists
import re
from THLTextProcessing import THLPageIterator, THLSource, THLText  # Custom class for text processing
import sys
# from lxml import etree


def normspace(txt2norm=''):
    if not isinstance(txt2norm, str):
        #print "Line Not Available"
        return False
    newtxt = re.sub("[\x00-\x20]+", "\x20", txt2norm)
    #newtxt = re.sub("\s", " ", newtxt)
    return newtxt


def compare_one_file(oldtext, newtext):
    #print normspace(newtext.getline(pagenum))
    print "Comparing {0} to {1}".format(oldtext.xml_text_url, newtext.xml_text_url)
    rng = oldtext.getrange()
    print "Range: {0} to {1}".format(rng[0], rng[1])
    pglist = THLPageIterator(rng[0], rng[1])
    for linenum in pglist:
        print "Line {0}".format(linenum),
        oldline = normspace(oldtext.getline(linenum))
        if oldline is False:
            print "{0} does not exist in old text".format(linenum)
            continue
        newline = normspace(newtext.getline(linenum))
        if newline is False:
            print "{0} does not exist in new text".format(linenum)
            continue
        oldlist = list()
        for ch in oldline.decode('utf-8'):
            oldlist.append(ch)
            # print "Line {0}".format(i)
        newlist = list()
        for ch in newline.decode('utf-8'):
            newlist.append(ch)

        ind = 0
        diff = False
        for item in newlist:
            try:
                if ord(item) > 32 and item != oldlist[ind]:
                    if diff is False:
                        print "\nDiff at {0} of {1}: ".format(ind, len(oldlist)), "orig: ", oldlist[
                            ind], " proofed: ", item
                    diff = True
                    break
                ind += 1
            except IndexError:
                pass

        if diff is True:
            origold = oldline.decode('utf-8')
            orignew = newline.decode('utf-8')
            newold = origold[:ind] + "" + origold[ind:]
            newnew = orignew[:ind] + "**" + orignew[ind:]
            print newold
            print newnew
        else:
            print ": Identical!"

if __name__ == "__main__":
    """Compares a whole folder of a texts document set at tnum"""

    base_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    texts_root = base_dir + "catalogs/xml/kt/d/"
    old_texts = texts_root + "texts/"
    new_texts = texts_root + "texts-new/"

    mode = 'whole-text'

    if mode == 'single-file':
        tnum = '0009'
        filenm = 'kt-d-0009-tha-05.xml'
        outbase = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/comparisons'
        outurl = '{0}/{1}-comparison.txt'.format(outbase, filenm.replace('.xml', ''))
        print "Out url: {0}".format(outurl)
        sys.stdout = codecs.open(outurl, 'w', encoding='utf-8')
        oldtxt = THLText(old_texts + tnum + "/" + filenm)
        newtxt = THLText(new_texts + tnum + "/" + filenm)
        compare_one_file(oldtxt, newtxt)

    elif mode == 'whole-text':
        tnum = '0003'
        print 'Comparing text {0} files...'.format(tnum)
        # Print standard out to file for documentation
        outbase = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/comparisons/'
        outfolder = outbase + tnum
        if not exists(outfolder):
            makedirs(outfolder)
        #outurl = outbase + 'Kt-{0}-comparison.txt'.format(tnum)
        print "Directory: " + old_texts + tnum
        files = [fl for fl in listdir(old_texts + tnum) if fl.find('-text') == -1]
        # If no files found, means only -text.xml file exist. It's a one file text so use that one
        if len(files) == 0:
            files = listdir(old_texts + tnum)
        for filenm in files:
            outurl = outfolder + "/" + '{0}-comparison.txt'.format(filenm.replace('.', '-'))
            sys.stdout = codecs.open(outurl, 'w', encoding='utf-8')
            oldtxt = THLText(old_texts + tnum + "/" + filenm)
            newtxt = THLText(new_texts + tnum + "/" + filenm)
            if oldtxt.exists and newtxt.exists:
                compare_one_file(oldtxt, newtxt)
            else:
                if not oldtxt.exists:
                    print "{0} doesn't exist".format(oldtxt.xml_text_url)
                if not newtxt.exists:
                    print "{0} doesn't exist".format(newtxt.xml_text_url)
            sys.stdout.close()

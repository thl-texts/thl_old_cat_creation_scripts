# coding=utf-8
#
# Creating new files for Kg.Dg.0012 because the pagination has been wrong since the beginning
#
# Real Pagination is:
#   vol.

from THLTextProcessing import *  # Custom class for text processing

##### Main ######

outloc = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/out/'
pgrng = False
while pgrng is False:
    pgrng = raw_input("Enter Tibetan page.line range: ")
    pgrng = pgrng.lower()
    if pgrng == "exit" or pgrng == "end" or pgrng == "stop":
        print "Quiting program!"
        exit(0)
    pgs = pgrng.strip().split('-')
    if len(pgs) < 2:
        pgs = False

stpg = pgs[0].strip()
enpg = pgs[1].strip()

pageflipper = THLPageIterator(stpg, enpg)

outnm = "{0}milestones-{1}-{2}.txt".format(outloc, stpg, enpg)


with codecs.open(outnm, 'w', encoding='utf-8') as fout:
    currpg = False
    for msnm in pageflipper:
        mypg = msnm.split('.')[0]
        if mypg != currpg:
            fout.write('<milestone unit="page" n="{0}" />'.format(mypg))
            currpg = mypg
        fout.write('<milestone unit="line" n="{0}" />'.format(msnm))
# coding=utf-8
#

from THLTextProcessing import *

basefold = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/'
proofedvols = basefold + 'Convert2ndInput/workspace/ProofedVols/source-vols-latest/eKangyur_W4CZ5369-normalized-nocr/'
volpath = proofedvols + '041-FINAL-tags-cvd.txt'

outfileloc = basefold + 'Convert2ndInput/workspace/debug/'
outfilepath = outfileloc + 'srcvoldebug.xml'

srcobj = THLSource(volpath)

stpg = '204b.1'
endpg = '205b.1'

chunk = srcobj.getchunk(stpg, endpg)

outf = codecs.open(outfilepath, 'w', encoding="utf-8")
outf.write(chunk)
outf.close()

print "Done!"


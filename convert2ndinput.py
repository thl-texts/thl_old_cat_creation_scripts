#
#  Iterates through the numbered subdirectories of kt/d bibls and returns a flat list of each file
#        On each text folder it determines if single file or multifile.
#        On multifile text folders, it runs getMultiTextInfo.xsl on the -text.xml file which returns a list of volumes and their texts
#        Each volume item in the list has:
#               0: volume number
#               1: wylie vol letter
#               2: list of texts. Each texts is: [
#                   0: file name
#                   1: begin page
#                   2: end page
#                ]
# 
import os, sys
import codecs

voldir='/Users/thangrove/Projects/tibtexts/Kg2ndInput/textfiles/Kt-Dg-vol13-2ndInput'
outfile = voldir + '/kt-d-v013-2ndinput.xml'
out = codecs.open(outfile, 'w', encoding='utf-8')
path, dirs, files = os.walk(voldir).next()
print "HERE"
for f in files:
    if f.find('.txt') > 0:
        print "Reading {0} ...".format(f)
        #print "Parsing {0} in {1}".format(f, d)
        infile = codecs.open(os.path.join(voldir,f), 'r', encoding='utf-8')
        lct = 0
        for fline in infile:
            lct += 1
            if lct > 1:
                fline = fline.strip()
                fline = fline.replace(u'\u00A0', u'\u0020')
                fpts = fline.split('[')
                lpct = 0
                for fp in fpts:
                    lpct += 1
                    if len(fp) > 1:
                        if lpct > 1:
                            out.write(u'\u000D[')
                        out.write(fp)
        
print "Finished! Volume out is: {0}".format(outfile)

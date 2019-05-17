# coding=utf-8
#
# Creating new files for Kg.Dg.0012 because the pagination has been wrong since the beginning
#
# Real Pagination is:
#   vol.

from THLTextProcessing import *  # Custom class for text processing

##### Main ######

volsyntax = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/' + \
            'ProofedVols/source-vols-latest/eKangyur_W4CZ5369-normalized-nocr/' + \
            '0{0}-FINAL-tags-cvd.txt'
textloc = '/Users/thangrove/Sites/texts/production/catalogs/xml/kt/d/texts/0012/kt-d-0012-text.xml'
templatedoc = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/' + \
            'workspace/temp/kt-d-0012-template.xml'
outloc = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/out/'
text = etree.parse(textloc).getroot()
vols = text.xpath('//body/div[@type="vol"]')

for v in vols:
    volnum = v.get('n')
    print "Opening vol {0}".format(volnum)
    volpath = volsyntax.format(volnum)
    src = THLSource(volpath)
    docs = v.xpath('.//item')
    for d in docs:
        fnm = d.find('xref').text
        pgrng = d.find('num').text.split('-')
        # get the chunk
        stpg = pgrng[0] + 'a.1'
        if pgrng[0] == '1' or pgrng[0] == '207':
            stpg = pgrng[0] + 'b.1'
        endpg = pgrng[1] + 'b.7'
        if pgrng[1] == 297 or pgrng[1] == 306:
            endpg = pgrng[1] + 'a.6' # vol. 31 ends at 297a.6, vol 32 ends 306a.6
        chunk = src.getchunk(stpg, endpg)
        errs = chunk[1]
        chunk = chunk[0]
        # print stpg, endpg
        # print errs
        # with codecs.open(outloc + 'temptest.xml', 'w', encoding='utf-8') as testout:
        #     testout.write(chunk)
        # break

        # read in the template
        fin = codecs.open(templatedoc, 'r', encoding='utf-8')
        mytext = fin.read()
        fin.close()

        # Use all inclusive regex to replace <p>
        # Done this way because using lxml resolves all XML entities into XML,
        # which we don't want for writing back out
        pattern = r'<p>[\s\S]+</p>'
        chunk = u'<p>' + chunk + u'</p>'
        mytext = re.sub(pattern, chunk, mytext)
        outnm = outloc + fnm
        print "Writing {0}".format(fnm)
        with codecs.open(outnm, 'w', encoding='utf-8') as fout:
            fout.write(mytext)
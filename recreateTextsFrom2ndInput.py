# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import os       # For Directory travelling
import codecs   # For Unicode Processing
from THLTextProcessing import THLSource, THLText
from lxml import etree

if __name__ == "__main__":

    #  Test text: /Users/thangrove/S4ites/texts/dev/catalogs/xml/kt/d/texts/0002/kt-d-0002-text.xml
    #  Test Source volume: /Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/005 FINAL tags.txt
    #  test_path = '/Users/thangrove/Sites/texts/dev/catalogs/xml/kt/d/texts/0002/kt-d-0002-text.xml'

    #  Define Variables
    txtnum = 2                                                                          # Text being processesd
    volnum = 5                                                                          # Vol. Num Being Processed
    volstr = str(volnum).zfill(3)                                                       # Vol num with leading zeros (3 dig)
    mydir = os.path.dirname(__file__)                                                     # This script's dir
    vol_in_url = '{0}/../../../2ndInput/{1} FINAL tags.txt'.format(mydir, volstr)      # Vol in file
    orig_cat_dir = '/usr/local/projects/thlib-texts/cocoon/texts/catalogs/xml/kt/d/'    # Dege orig (dev) texts folder
    orig_vol_dir = '{0}texts/{1}'.format(orig_cat_dir, volstr.zfill(4))                 # Dege orig (dev) vol folder
    out_dir = os.path.dirname(__file__) + '/../z-out'                                   # Output directory name
    test_dir = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/'

    vol_in_url = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/005 FINAL tags.txt'
    test_text_url = '/Users/thangrove/Sites/texts/dev/catalogs/xml/kt/d/texts/0002/kt-d-0002-text.xml'

    outpath = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/'
    outfile = outpath + 'kd-d-0002-replaced.xml'

    proofed = THLSource(vol_in_url)
    proofed.convert_input_to_xml()

    text = THLText(test_text_url)
    msrange = text.getrange()
    #print range

    chunk = proofed.getchunk(msrange[0], msrange[1]) # by default wraps in <p> tag
    print chunk
    exit(0)
    outtext = text.replace_p(chunk)
    fout = codecs.open(outfile, 'w', encoding="utf-8")
    fout.write(outtext)
    fout.close()

    # TODO: now that source and text have been loaded we need to get the chunk from the source and replace it in text




# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

# import os       # For Directory travelling
import codecs   # For Unicode Processing
from THLTextProcessing import THLSource, THLText  # Custom class for text processing
# from lxml import etree

if __name__ == "__main__":

    # testout_dir = "/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test-out/"

    source_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
    source_in = source_dir + "005 FINAL tags.txt"

    texts_clone_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    texts_in_dir = texts_clone_dir + "catalogs/xml/kt/d/texts/"
    texts_out_dir = texts_clone_dir + "catalogs/xml/kt/d/texts-new/"
    test_text = "0002/kt-d-0002-text.xml"
    text_in_url = texts_in_dir + test_text
    text_out_url = texts_out_dir + test_text

    # test_in_dir = '/usr/local/projects/thlib-texts/current/cocoon/catalogs/xml/kt/d/texts/'
    # text_in_url = test_in_dir + test_text

    proofed = THLSource(source_in)
    proofed.convert_input_to_xml()
    print "Text in url: {0}".format(text_in_url)
    text = THLText(text_in_url)
    msrange = text.getrange()


    chunk = proofed.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag

    outtext = text.replace_p(chunk)
    fout = codecs.open(text_out_url, 'w', encoding="utf-8")
    fout.write(outtext)
    fout.close()





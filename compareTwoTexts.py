# coding=utf-8
#
#  Compares two text files line by line
#

# import os       # For Directory travelling
import codecs   # For Unicode Processing
from THLTextProcessing import THLPageIterator, THLSource, THLText  # Custom class for text processing
# from lxml import etree

if __name__ == "__main__":

    base_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    texts_root = base_dir + "catalogs/xml/kt/d/"
    text1url = texts_root + "texts/0002/kt-d-0002-text.xml"
    text2url = texts_root + "texts-new/0002/kt-d-0002-text.xml"

    text1 = THLText(text1url)
    text2 = THLText(text2url)

    rng = text1.getrange()

    for pn in THLPageIterator(rng[0], rng[1]):
        pg1 = text1.getline(pn)
        pg2 = text2.getline(pn)



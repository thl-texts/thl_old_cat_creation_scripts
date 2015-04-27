# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import exists, isfile, join
from THLTextProcessing import THLSource, THLText  # Custom class for text processing
# from lxml import etree
import pprint

cocoon_base = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
texts_dir = cocoon_base + "catalogs/xml/kt/d/texts/"
new_texts_dir  = cocoon_base + "catalogs/xml/kt/d/texts-new/"
proofed = None

def extract_one_text_from_proofed_data():
    """Extracts a single text based on locations set and creates a catalog XML file for it

    Returns:
        true if successful
    """
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
    return True


def extract_folder(fpath='', outpath=''):
    """Scans a folder in texts folder and extracts recreates its contents with proofed data
        NOTE: Only works with text contained in a single volume.
    Args:
        fpath (string): Path to folder to copy
        outpath (string): Path to folder for writing output

    Returns:
        True if successful
    """
    if fpath is '' or not exists(fpath) or outpath is '':
        print "Error: Problem with paths given."
        return

    if not exists(outpath):
        makedirs(outpath)

    vfiles = [f for f in listdir(fpath) if isfile(join(fpath, f)) and f[0] is not "."]
    #pp = pprint.PrettyPrinter()
    #print pp.pprint(vol_files)
    #print ", ".join(vol_files)
    for f in vfiles:
        out_url = join(outpath, f)
        newtxt = extract_file(fpath, f)
        if newtxt:
            fout = codecs.open(out_url, 'w', encoding="utf-8")
            fout.write(newtxt)
            fout.close()
        else:
            return False

    return True

def extract_file(fpath, fname):
    """Given a path and file name this function returns the text to write out to a file

    Args:
        fpath (string): path to the folder containing the file
        fname (string): name of the file with extension

    Returns:
        A string containing the XML to print out to a file

    """
    xmldoc = THLText(fpath + fname)
    txtrange = xmldoc.getrange()
    if txtrange:
        chunk = proofed.getchunk(txtrange[0], txtrange[1], 'p')  # wraps in <p> tag
        outtext = xmldoc.replace_p(chunk)
        return outtext
    else:
        return False

def get_source_volume(vnum=5):
    """Returns the object representing the proofed source volume from which texts are created

    Args:
        vnum (int): volume number to read in

    Returns:
        THLSource object of the desired volume
    """

    source_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
    source_in = source_dir + "{0:0>3} FINAL tags.txt".format(vnum)
    source = THLSource(source_in)
    source.convert_input_to_xml()
    return source

if __name__ == "__main__":
    # extract_one_text_from_proofed_data()
    proofed = get_source_volume()
    extract_folder(texts_dir + '0003test/', new_texts_dir + '0003/')
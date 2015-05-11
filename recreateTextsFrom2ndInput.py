# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import exists, isfile, join
import shutil
from THLTextProcessing import THLSource, THLText, THLBibl  # Custom class for text processing
# from lxml import etree
# import pprint

base_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
proof_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
texts_dir = base_folder + "catalogs/xml/kt/d/texts/"
new_texts_dir  = base_folder + "catalogs/xml/kt/d/texts-new/"
proofed = None
proofednum = 0

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
        NOTE: FOR TESTING ONLY. Only works with text contained in a single volume.
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


def extract_proofed_text(xmldoc):
    """Given THLText object that has read in a text xml file, returns a proofed version of that text object

        NOTE: "proofed" is global variable set elsewhere.

    Args:
        fpath (string): path to the folder containing the file
        fname (string): name of the file with extension

    Returns:
        A string containing the XML to print out to a file

    """

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


def get_bibl_path(txtpath):
    print "textpath: {0}".format(txtpath)
    pparts = txtpath.split('/')
    tnuminpath = pparts.pop()
    if not tnuminpath:
        tnuminpath = pparts.pop()
    fnum = tnuminpath[0]
    pparts.pop()
    bibl_path = '/'.join(pparts) + "/{0}/kt-d-{1}-bib.xml".format(fnum, tnum)
    return bibl_path


def load_proofed_vol(vnum):
    """Loads a volumes worth of proofed text and converts to xml. Assigns resulting THLSource object to
        global variable proofed and the volumn number to proofednum so it can be reused
        Used by convert_text

    Args:
        vnum (string): volume number to load

    Returns:
        Nothing but sets global variables proofed (THLSource) and proofednum (string)
    """
    global proofed, proofednum
    vnum = str(vnum)
    if vnum == proofednum:
        return
    proofednum = vnum
    vnum = vnum.zfill(3)
    volpath = proof_folder + "{0}/{0} FINAL tags.txt".format(vnum)
    proofed = THLSource(volpath)


def convert_text(inpath, outpath):
    """Creates a proofed version of files in a text folder of any type

    Args:
        tpath (string): path to text folder, e.g. .../oldtexts/0003
        outpath (string): directory in which to write the new files, e.g. ..../newtexts/0003.
    """
    global proofed

    if not exists(outpath):
        makedirs(outpath)

    dfiles = [f for f in listdir(inpath) if isfile(join(inpath, f))]

    if inpath[-1] is not '/':
        inpath += '/'

    if outpath[-1] is not '/':
        outpath += '/'

    if len(dfiles) == 1:  # Only a single file in the text folder
        # Need to read bibl and get vol number from it
        #print "only 1 file: {0}".format(dfiles[0])
        fpath = inpath + dfiles[0]
        foutpath = outpath + dfiles[0]
        bibl = THLBibl(get_bibl_path(inpath))
        volnum = bibl.get_volnums()
        volnum = volnum[0]
        load_proofed_vol(volnum)
        xmltxt = THLText(fpath)
        msrange = xmltxt.getrange()
        chunk = proofed.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag

        outtext = xmltxt.replace_p(chunk)
        fout = codecs.open(foutpath, 'w', encoding="utf-8")
        fout.write(outtext)
        fout.close()

    else:
        maindoc = [f for f in dfiles if "-text.xml" in f]
        print "Main doc file: {0}".format(maindoc[0])
        maindocpath = inpath + maindoc[0]
        maindocout = outpath + maindoc[0]
        shutil.copy(maindocpath, maindocout)
        main_xml = THLText(maindocpath)
        voldivs = main_xml.xpath('/*//body/div[@type="vol"]')
        for vd in voldivs:
            volnum = vd.get('n')
            print "Doing volume {0}".format(volnum)
            print volnum
            load_proofed_vol(volnum)
            xrefs = vd.findall('.//xref')
            for xref in xrefs:
                docnm = xref.text
                print "\t{0}".format(docnm)
                docxml = THLText(inpath + docnm)
                msrange = docxml.getrange()
                chunk = proofed.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag
                outtext = docxml.replace_p(chunk)
                foutpath = outpath + docnm
                fout = codecs.open(foutpath, 'w', encoding="utf-8")
                fout.write(outtext)
                fout.close()

    return


if __name__ == "__main__":
    # extract_one_text_from_proofed_data()
    for n in range(4, 7):
        tnum = str(n).zfill(4)
        print "****** Text {0} ******".format(tnum)
        txt_path = texts_dir + tnum
        out_path = new_texts_dir + tnum
        convert_text(txt_path, out_path)
        print "Done! \n\n"
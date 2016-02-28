# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import sys
import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import exists, isfile, join, isdir
import shutil
from THLTextProcessing import THLSource, THLText, THLBibl  # Custom class for text processing
# from lxml import etree
# import pprint

base_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
# Old proof_folder used in commented out line ~165
#proof_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
proof_folder = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols-latest/eKangyur_W4CZ5369-normalized-nocr/'
ed_dir = "/usr/local/projects/thlib-texts/cocoon/texts/catalogs/xml/kt/d/"
texts_dir = ed_dir + "texts/"
new_texts_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/catalogs/xml/kt/d/texts-new/"
proofed = None
proofednum = 0

def extract_one_text_from_proofed_data(volname=False, textnum=False):
    """Extracts a single text based on       locations set and creates a catalog XML file for it

    Args:
        volname (string): the full name of volume with extension
        textnum (integer/string): the integer number for the text ID or string representation of that number

    Returns:
        true if successful
    """
    global proofed

    # Return fals if either volname or textnum is not given
    if volname == False or textnum == False:
        return False

    # testout_dir = "/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test-out/"

    #source_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
    source_in = proof_folder + volname

    texts_clone_dir = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    texts_in_dir = texts_clone_dir + "catalogs/xml/kt/d/texts/"
    texts_in_dir = '/usr/local/projects/thlib-texts/cocoon/texts/catalogs/xml/kt/d/texts'
    texts_out_dir = texts_clone_dir + "catalogs/xml/kt/d/texts-new/"
    textnum = str(textnum).zfill(4)
    test_text = "{0}/kt-d-{0}-text.xml".format(textnum)
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
        xmldoc (THLText): an initiated THLText object

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
    #volpath = proof_folder + "{0}/".format(vnum) # goes with old proof_folder
    volfilepath = proof_folder + "{0}-FINAL-tags-cvd.txt".format(vnum)
    proofed = THLSource(volfilepath)
    # volfiles = listdir(volpath)
    # print volpath, volfiles
    # for vf in volfiles:
    #     volfilepath = volpath + vf
    #     # Sometimes volume proofed is 0000 FINAL tag.txt and sometimes 0000 Final tags.txt
    #     if vf.find('FINAL tag') > -1 and vf.find('.txt') > -1:
    #         print "Opening volume: {0}".format(volfilepath)
    #         proofed = THLSource(volfilepath)
    #         break
    #     else:
    #         print "Not suitable vol file: {0}".format(volfilepath)


def convert_text(inpath, outpath):
    """Creates a proofed version of files in a text folder of any type

    Args:
        inpath (string): path to text folder, e.g. .../oldtexts/0003
        outpath (string): directory in which to write the new files, e.g. ..../newtexts/0003.
    """
    global proofed

    if not isdir(inpath):
        print "Warning: the source directory, {0}, does not exist. Cannot create new text.".format(inpath)
        return

    if not exists(outpath):
        makedirs(outpath)

    dfiles = [f for f in listdir(inpath) if isfile(join(inpath, f))]
    print "There are {0} files".format(len(dfiles))
    if inpath[-1] is not '/':
        inpath += '/'

    if outpath[-1] is not '/':
        outpath += '/'
    print "Converting text: {0}".format(inpath)
    print "Writing output to: {0}".format(outpath)
    bibl = THLBibl(get_bibl_path(inpath))
    vols = bibl.get_volnums()
    volnum = vols[0]
    print "Volume number is: {0}".format(volnum)
    #   volnum = 56 # to override texts without bibls
    if len(dfiles) == 1:  # Only a single file in the text folder
        # Need to read bibl and get vol number from it
        #print "only 1 file: {0}".format(dfiles[0])
        fpath = inpath + dfiles[0]
        foutpath = outpath + dfiles[0]
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
        if not maindoc:
            print "Warning: No *-main doc found in directory, {0}! " \
                  "Cannot continue with conversion of this text.".format(inpath)
            return

        print "Main doc file: {0}".format(maindoc[0])
        maindocpath = inpath + maindoc[0]
        maindocout = outpath + maindoc[0]
        shutil.copy(maindocpath, maindocout)
        main_xml = THLText(maindocpath)
        voldivs = main_xml.xpath('/*//body/div[@type="vol"]')
        for vd in voldivs:
            print "Loading volume {0}".format(volnum)
            load_proofed_vol(volnum)
            xrefs = vd.findall('.//xref')
            for xref in xrefs:
                docnm = xref.text
                process_doc(docnm, inpath, outpath)
            volnum = int(volnum) + 1
            volnum = str(volnum)
        return


def process_doc(docnm, dinpath, doutpath):
    global proofed
    print "Processing Doc {0}".format(docnm)
    docxml = THLText(dinpath + docnm)
    msrange = docxml.getrange()

    if proofed is not None:

        chunk = proofed.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag
        outtext = docxml.replace_p(chunk)
        foutpath = doutpath + docnm
        fout = codecs.open(foutpath, 'w', encoding="utf-8")
        fout.write(outtext)
        fout.close()

    else:

        print "Unable to get proofed vol, it  is null. {0}".format(docnm)


def process_single_doc(volnm, docnm, dinpath, doutpath):
    load_proofed_vol(volnm)
    process_doc(docnm, dinpath, doutpath)


def get_text_bibl(prefix, mytnum):
    tbfol = 0
    if 999 < mytnum < 2000:
        tbfol = 1
    bibl_path = ed_dir + str(tbfol) + '/' + prefix + str(mytnum).zfill(4) + "-bib.xml"
    return THLBibl(bibl_path)


if __name__ == "__main__":

    contype = 'multi'  # Type of conversion to perform

    if contype == 'single':
        # Do just one text or limited range of text
        svolnum = 9
        for n in range(6, 17):
            sdocnm = 'kt-d-0009-tha-{0}.xml'.format(str(n).zfill(2))
            docpath = "{0}/{1}".format(str(svolnum).zfill(4), sdocnm)
            basepath = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/catalogs/xml/kt/d'
            sinpath = '{0}/texts/'.format(basepath)
            soutpath = '{0}/texts-new/'.format(basepath)
            print "Processing {0}".format(sdocnm)
            process_single_doc(svolnum, docpath, sinpath, soutpath)

    elif contype == 'multi':

        # extract_one_text_from_proofed_data()

        # Print standard out to file for documentation
        outbase = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/conversions'
        sttxt = 479
        endtxt = 500
        outurl = '{0}/kt-d-v{1}-{2}-conversion.log'.format(outbase, sttxt, endtxt)
        print "Logging output to: {0}".format(outurl)
        sys.stdout = codecs.open(outurl, 'w', encoding='utf-8')
        for n in range(sttxt, endtxt + 1):
            tnum = str(n).zfill(4)
            print "****** Text {0} ******".format(tnum)
            txt_path = texts_dir + tnum
            out_path = new_texts_dir + tnum
            convert_text(txt_path, out_path)

    else:
        # Final else is for testing/debugging
        bobj = get_text_bibl('kt-d-', 45)
        print bobj.get_volnums()

    print "Done! \n\n"
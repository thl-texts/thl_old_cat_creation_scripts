# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import sys
import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import exists, isfile, join, isdir
import shutil
import time
from THLTextProcessing import THLSource, THLText, THLBibl  # Custom class for text processing
# from lxml import etree
# import pprint

base_folder = "/Users/thangrove/Box/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/ProofedVols/"
# Old proof_folder used in commented out line ~165
#proof_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/source-vols/"
proof_folder = base_folder + 'source-vols-latest/eKangyur_W4CZ5369-normalized-nocr/'
ed_dir = "/Users/thangrove/Sites/texts/production/catalogs/xml/kt/d/"
texts_dir = ed_dir + "texts/"
new_texts_dir = base_folder + "texts-clone/catalogs/xml/kt/d/texts-new-july-2018/"
proofed = None
proofednum = 0
infolog = None
errorlog = None

def extract_one_text_from_proofed_data(volname=False, textnum=False):
    """Extracts a single text based on locations set and creates a catalog XML file for it

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
    texts_out_dir = texts_clone_dir + "catalogs/xml/kt/d/texts-new-july-2018/"
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
        convlog("Error: Problem with paths given.", 'error')
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
    convlog("textpath: {0}".format(txtpath), 'info')
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
    vnm = "{0}-FINAL-tags-cvd.txt".format(vnum)
    volfilepath = proof_folder + vnm
    convlog("Reading volume: {0}".format(vnm), 'both', True)
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
        outpath (string): directory in which to write the new-first files, e.g. ..../newtexts/0003.
    """
    global proofed

    if not isdir(inpath):
        convlog("Warning: the source directory, {0}, does not exist. Cannot create new-first text.".format(inpath), 'error')
        return

    if not exists(outpath):
        makedirs(outpath)

    dfiles = [f for f in listdir(inpath) if isfile(join(inpath, f))]
    print "There are {0} files".format(len(dfiles))
    if inpath[-1] is not '/':
        inpath += '/'

    if outpath[-1] is not '/':
        outpath += '/'
    # convlog("Converting text: {0}".format(inpath), 'both')
    convlog("Writing output to: {0}".format(outpath))
    bibl = THLBibl(get_bibl_path(inpath))
    vols = bibl.get_volnums()
    volnum = vols[0]
    convlog("Volume number is: {0}".format(volnum))
    #   volnum = 56 # to override texts without bibls
    if len(dfiles) == 1:  # Only a single file in the text folder
        # Need to read bibl and get vol number from it
        #print "only 1 file: {0}".format(dfiles[0])
        fpath = inpath + dfiles[0]
        foutpath = outpath + dfiles[0]
        load_proofed_vol(volnum)
        xmltxt = THLText(fpath)
        msrange = xmltxt.getrange()
        if msrange:
            res = proofed.getchunk(msrange[0], msrange[1], 'p', u'༄༅༅།')  # wraps in <p> tag
            chunk = res[0]
            convlog(res[1])
            outtext = xmltxt.replace_p(chunk)
            fout = codecs.open(foutpath, 'w', encoding="utf-8")
            fout.write(outtext)
            fout.close()
        else:
            convlog("Warning: Could not get range for text: {0}".format(fpath), 'error')
            return

    else:  # Text with multiple files
        maindoc = [f for f in dfiles if "-text.xml" in f]  # find the -text.xml = maindoc
        if not maindoc:
            convlog( "Warning: No *-main doc found in directory, {0}! " \
                  "Cannot continue with conversion of this text.".format(inpath), 'error')
            return

        convlog("Main doc file: {0}".format(maindoc[0]))

        # Copy the main doc to the output location
        maindocpath = inpath + maindoc[0]
        maindocout = outpath + maindoc[0]
        shutil.copy(maindocpath, maindocout)

        # Using THLText find xrefs to chunk files in main doc and process them
        main_xml = THLText(maindocpath)
        voldivs = main_xml.xpath('/*//body/div[@type="vol"]')
        for vd in voldivs:
            convlog("Loading volume {0}".format(volnum))
            load_proofed_vol(volnum)  # load the proofed volume for this range of texts (maindoc div)
            xrefs = vd.findall('.//xref')
            for xref in xrefs:
                docnm = xref.text
                process_doc(docnm, inpath, outpath)  # process each text file referred to in main doc
            print " "
            volnum = int(volnum) + 1
            volnum = str(volnum)
        return


def process_doc(docnm, dinpath, doutpath):
    global proofed
    convlog("Processing Doc {0}".format(docnm))
    print ".",
    docxml = THLText(dinpath + docnm)
    msrange = docxml.getrange()

    if not msrange:
        convlog("Cannot get range for text {0}".format(docnm), 'error')
        return

    if proofed is not None:
        #print "msrange", str(msrange)
        (chunk, msgs) = proofed.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag
        convlog(msgs, 'list')
        outtext = docxml.replace_p(chunk)
        foutpath = doutpath + docnm
        fout = codecs.open(foutpath, 'w', encoding="utf-8")
        fout.write(outtext)
        fout.close()

    else:

        convlog("Unable to get proofed vol, it  is null. {0}".format(docnm), 'error')


def process_single_doc(volnm, docnm, dinpath, doutpath):
    load_proofed_vol(volnm)
    process_doc(docnm, dinpath, doutpath)


def get_text_bibl(prefix, mytnum):
    tbfol = 0
    if 999 < mytnum < 2000:
        tbfol = 1
    bibl_path = ed_dir + str(tbfol) + '/' + prefix + str(mytnum).zfill(4) + "-bib.xml"
    return THLBibl(bibl_path)

def convlog(str, type='info', printme=False):
    global infolog, errorlog
    if isinstance(str, list):
        for s in str:
            if ':' in s:
                pts = s.split(':')
                convlog(pts[1], pts[0])
    elif type == 'error':
        errorlog.write(str + "\n")
    elif type == 'both':
        errorlog.write(str + "\n")
        infolog.write(str + "\n")
    else:
        infolog.write(str + "\n")

    if printme:
        print str


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
            soutpath = '{0}/texts-new-201807/'.format(basepath)
            convlog("Processing {0}".format(sdocnm), 'info', True)
            process_single_doc(svolnum, docpath, sinpath, soutpath)

    elif contype == 'multi':

        # extract_one_text_from_proofed_data()

        # Print standard out to file for documentation
        outbase = '/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/conversions'
        sttxt = 479
        endtxt = 1118
        ts = int(time.time())
        infologurl = '{0}/ktd-{1}-{2}-txtconv-{3}-info.log'.format(outbase, sttxt, endtxt, ts)
        errorlogurl = '{0}/ktd-{1}-{2}-txtconv-{3}-error.log'.format(outbase, sttxt, endtxt, ts)
        print "Logging output to: {0}".format(infologurl)
        infolog = codecs.open(infologurl, 'w', encoding='utf-8')
        errorlog = codecs.open(errorlogurl, 'w', encoding='utf-8')
        convlog("Converting texts: {0} to {1}".format(sttxt, endtxt), 'info', True)
        convlog("Start: {0}".format(time.strftime("%c")), 'info', True)
        starttime = time.time()
        for n in range(sttxt, endtxt + 1):
            tnum = str(n).zfill(4)
            convlog("****** Text {0} ******".format(tnum), 'both', True)
            txt_path = texts_dir + tnum
            out_path = new_texts_dir + tnum
            convert_text(txt_path, out_path)
        endtime = time.time()
        dtime = endtime - starttime
        secs = int(dtime % 60)
        mins = int(dtime / 60)
        convlog("Finished at {0}. Total time: {1} mins, {2} secs.".format(time.strftime("%c"), mins, secs), 'info', True)
    else:
        # Final else is for testing/debugging
        bobj = get_text_bibl('kt-d-', 45)
        print bobj.get_volnums()

    print "Done! \n\n"
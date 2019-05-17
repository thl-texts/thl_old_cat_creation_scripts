"""Recreate Dege Kangyur Text from Proofed Input

This script is a refactoring of recreateTextsFrom2ndInput.py cleaning up and modularizing the code as well as
generalizing paths and upgrading from Python 2to Python 3. Rather than packing multiple uses into a single script
as its predecessor, this script creates a single text from the proofed input, whereas the conversion of multiple texts
or a range of texts will be achieved by calling this script from elsewhere.



"""

from THLTextProcessing import THLSource, THLText, THLBibl  # Custom class for text processing

base_folder = "../workspace/ProofedVols"
proof_folder = base_folder + 'source-vols-latest/eKangyur_W4CZ5369-normalized-nocr/'
ed_dir = "/usr/local/projects/thlib-texts/current/catalogs/xml/kt/d/"
texts_dir = ed_dir + "texts/"
new_texts_dir = base_folder + "texts-clone/catalogs/xml/kt/d/texts-new-may-2019/"

def load_proofed_vol(vnum):
    """Loads a volumes worth of proofed text and converts to xml. Assigns resulting THLSource object to
        global variable proofed and the volumn number to proofednum so it can be reused
        Used by convert_text

    Args:
        vnum (string): volume number to load

    Returns:
        Nothing but sets global variables proofed (THLSource) and proofednum (string)
    """
    vnum = str(vnum)
    vnum = vnum.zfill(3)
    vnm = "{0}-FINAL-tags-cvd.txt".format(vnum)
    volfilepath = proof_folder + vnm
    return THLSource(volfilepath)

def process_doc(volnm, docnm, dinpath, doutpath):

    vol = load_proofed_vol(volnm)
    # convlog("Processing Doc {0}".format(docnm))
    print(".", end="")
    docxml = THLText(dinpath + docnm)
    msrange = docxml.getrange()

    if not msrange:
        # convlog("Cannot get range for text {0}".format(docnm), 'error')
        return

    if proofed is not None:
        #print "msrange", str(msrange)
        (chunk, msgs) = vol.getchunk(msrange[0], msrange[1], 'p')  # wraps in <p> tag
        # convlog(msgs, 'list')
        outtext = docxml.replace_p(chunk)
        foutpath = doutpath + docnm
        fout = open(foutpath, 'w', encoding="utf-8")
        fout.write(outtext)
        fout.close()

    else:
        pass
        #convlog("Unable to get proofed vol, it  is null. {0}".format(docnm), 'error')


if __name__ == "__main__":
    vnm = 1
    docnm = "somedoc"
    dinpath = "path"
    doutpath =
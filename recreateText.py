"""Recreate Dege Kangyur Text from Proofed Input

This script is a refactoring of recreateTextsFrom2ndInput.py cleaning up and better (?) modularizing the code as well as
generalizing paths and upgrading from Python 2 to Python 3. Rather than packing multiple uses into a single script
as its predecessor, this script creates a single text from the proofed input, whereas the conversion of multiple texts
or a range of texts will be achieved by calling this script from elsewhere.


"""
from thl.thl_source import THLSource

base_folder = "../workspace/ProofedVols/"
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


if __name__ == "__main__":
    print(dir())

    vnm = 5
    vol = load_proofed_vol(vnm)
    if vol:
        txt, msgs = vol.getchunk('4b.3', '6a.2')
        print(txt)
        print(msgs)
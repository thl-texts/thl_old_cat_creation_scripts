# coding=utf-8
#
#  Recreates the XML Text files for Dege catalog from the *.txt files of the second input
#

import sys
import codecs   # For Unicode Processing
from os import listdir, makedirs
from os.path import abspath, dirname, exists, isfile, join
import shutil
from THLTextProcessing import THLCatalog  # Custom class for text processing
from lxml import etree
from csv import DictReader

bibldata = {}
# import pprint

# Function to get the bibl template file to fill in for the record. Returns as parsed etree XML objects
def get_bibl_template(bpath):
    bibl_template = bpath + "bibl/kt-d-bibl-template.xml"
    bibtree = etree.parse(bibl_template)
    bibroot = bibtree.getroot()
    return bibroot

# Get the pagination for a text from it's input data
def get_text_pagination(tid):
    text_folder = get_cat_path('textdir')
    text_path = text_folder + "{0}/kt-d-{0}-text.xml".format(tid)
    #print " Path is: {0}".format(text_path)
    try:
        textroot = etree.parse(text_path).getroot()
        # Get Milestones
        miles = textroot.xpath('//milestone[@unit="line"]')
        # Get Xrefs for MultiPart Docs
        xrefs = textroot.xpath('//div[@type="vol"]//xref')

        # Get Start page and line
        if len(miles) > 0:
            stpg = miles[0].get('n').split('.')
        else:
            xref = xrefs[0]
            txt_pt_path = text_folder + "/{0}/".format(tid) + xref.text
            txt_pt_root = etree.parse(txt_pt_path).getroot()
            txt_pt_miles = txt_pt_root.xpath('//milestone[@unit="line"]')
            if len(txt_pt_miles) > 0:
                stpg = txt_pt_miles[0].get('n').split('.')
            else:
                stpg = ['n/a', 'n/a']

        # Get End page and line
        if len(miles) > 0:
            lstpg = miles[-1].get('n').split('.')
        else:
            xref = xrefs[-1]
            txt_pt_path = text_folder + "/{0}/".format(tid) + xref.text
            txt_pt_root = etree.parse(txt_pt_path).getroot()
            txt_pt_miles = txt_pt_root.xpath('//milestone[@unit="line"]')
            if len(txt_pt_miles) > 0:
                lstpg = txt_pt_miles[-1].get('n').split('.')
            else:
                lstpg = ['n/a', 'n/a']

    except IOError as err:
        print "IOError for {0} : {1}".format(tid, err.message)
        stpg = ['n/a', 'n/a']
        lstpg = ['n/a', 'n/a']

    except etree.XMLSyntaxError as xerr:
        print "XMLSyntaxError for {0} : {1}".format(tid, xerr.message)
        stpg = ['n/a', 'n/a']
        lstpg = ['n/a', 'n/a']

    return stpg, lstpg


def get_tibetan(wyl):
    convurl = "http://www.thlib.org/cgi-bin/thl/lbow/wylie.pl?input={0}&xml=true".format(wyl)
    tibroot = etree.parse(convurl).getroot()
    phr = tibroot.xpath('//phr')
    tib = u''
    if len(phr) > 0:
        phr = phr[0]
        tib = phr.text
    return tib


# Function to fill in the bibl record template
def fill_in_template(bibltmp, btid, mycat):
    # Get pagination from db info
    textinfo = get_text_data(btid)

    # Set the ID values
    bid = "kt-d-{0}-bib".format(btid)
    bidint = str(int(btid))  # no leading zero version of bibl text id
    bibltmp.set("id", bid)
    bibltmp.xpath('//controlinfo/sysid')[0].text = bid
    bibltmp.xpath('//tibiddecl/tibid//tibid[@type="edition" and @system="sigla"][1]/tibid[1]')[0].text = bidint

    if textinfo:
        # Fill in vol info from Phil's db
        volel = bibltmp.xpath('//tibiddecl/tibid//tibid[@type="edition" and @system="sigla"][1]/tibid')[1]
        volel.text = textinfo['stvol']
        voltib = get_tibetan(textinfo['stvol-let'])
        volwyl = etree.Comment(textinfo['stvol-let'])
        volel.getchildren()[0].append(volwyl)
        volwyl.tail = voltib
        volel.getchildren()[1].text = textinfo['text-in-vol']
        # Fill in pagination etc
        pageel = bibltmp.xpath('//physdecl/pagination')
        volrs = pageel[0].getchildren()[0]
        volrs.set('n', textinfo["stvol"])

        stpg, enpg = get_text_pagination(btid)
        strs = volrs.getchildren()[0].getchildren()
        strs[0].text = stpg[0]
        strs[1].text = stpg[1] if len(stpg) > 1 else 'n/a'
        if len(stpg) == 1:
            print "No line number for start pagination in {0}".format(tid)

        # Old way of geting start page from Phil's DB
        # sidestr = "a" if textinfo["stsd"] == 1 else "b"
        # strs[0].text = textinfo["stpg"] + sidestr
        # strs[1].text = textinfo["stln"]

        endrs = volrs.getchildren()[1].getchildren()
        endrs[0].text = enpg[0]
        endrs[1].text = enpg[1] if len(enpg) > 1 else 'n/a'
        if len(enpg) == 1:
            print "No line number for end pagination in {0}".format(tid)

        # Old way of getting end page
        # sidestr = "a" if textinfo["endsd"] == 1 else "b"
        # endrs[0].text = textinfo["endpg"] + sidestr
        # endrs[1].text = textinfo["endln"]

    # Get the doxgraphical doc with title info for text
    doxdoc = cat.get_dox_for_text(btid, 'root')
    trec = doxdoc.xpath('//idno[@type="text" and text()="' + str(int(btid)) + '"]//ancestor::bibl[1]')[0]
    doxid = cat.get_dox_for_text(tid)
    tibdox = cat.get_dox_for_text(tid, 'tib')
    #print "Tib dox array:", tibdox

    # Set the doxography assigned element info
    doxel = bibltmp.xpath('//doxography[@type="category" and @subtype="assigned"]')[0]
    doxel.set('n', doxid)
    doxel.text = tibdox[0]
    doxel.append(etree.Comment(tibdox[1]))

    # Get title info
    ttitles = trec.xpath('./title[@lang="tib"]')
    tibtitle = ttitles[0].text
    wytitle = ttitles[1].text
    titleel = bibltmp.xpath('//titledecl[@n="normalized-title"]/title[@lang="tib" and @type="normalized-title"]')[0]
    wycomm = etree.Comment(wytitle)
    titleel.append(wycomm)
    titleel.text = tibtitle

    return bibltmp

# Loads data of correspondences
def load_dictionaries():
    global bibldata
    corresps = {}
    csvfile1 = 'data/Master Corresp.csv'
    with open(csvfile1, 'r') as csvin:
        reader = DictReader(csvin)
        for row in reader:
            corresps[int(row['Db ID'])] = int(row['New Master ID'])
    csvfile2 = 'data/Dg Phil Cat with Corresp.csv'
    with open(csvfile2, 'r') as csvin:
        reader = DictReader(csvin)
        for row in reader:
            mid = corresps[int(row["dbid"].replace('?',''))]
            bibldata[mid] = row

def get_text_data(tid):
    global bibldata
    tid = int(tid)
    if tid in bibldata:
        return bibldata[tid]
    else:
        print "No data for tid {0} in get_text_data".format(tid)
        return False

def get_cat_path(type = 'folder'):
    base_folder = "/Users/thangrove/Box Sync/Projects/THL/TextsTib/Kangyur/Dege/DgTextProcessing/Convert2ndInput/workspace/ProofedVols/texts-clone/"
    outpath = base_folder + "catalogs/xml/kt/d/"
    if type == 'cat':
        outpath += 'kt-d-cat.xml'
    elif type == 'textdir':
        outpath += 'texts/'
    return outpath


# MAIN ROUTINE
if __name__ == "__main__":
    mycatpath = get_cat_path('cat')
    cat = THLCatalog(mycatpath, 'mycat')
    allbibs = cat.xpath('/*//xptr[@type="texts"]')
    nobibs = cat.xpath('/*//xptr[@type="texts" and @rend="nobibl"]')
    print "{1} total texts\n{0} without bibl records".format(len(nobibs), len(allbibs))
    tl = cat.get_text_list('nobibl')
    mypath = dirname(abspath(__file__)) + "/"
    # print mypath

    load_dictionaries()  # Load the text information into dictionary variables
    ct = 0
    # tl = ['0065']
    for tid in tl:
        ct += 1
        if int(tid) > 1118:
            print "End of Kangyur"
            break
        #print "Creating kt-d-{0}-bib.xml".format(tid)
        bibldoc = get_bibl_template(mypath)
        bibldoc = fill_in_template(bibldoc, tid, cat)

        outstr = etree.tostring(bibldoc, encoding='utf-8', pretty_print=True, xml_declaration=True,
             doctype = '<!--DOCTYPE tibbibl SYSTEM "http://texts.thlib.org/catalogs/xtibbibl3.dtd" -->')
        outstr = unicode(outstr, "utf-8")

        outurl = mypath + "bibl/new/kt-d-{0}-bib.xml".format(tid)

        xmlout = codecs.open(outurl, "w", "utf-8")
        xmlout.write(outstr)
        xmlout.close()

        if ct % 100 == 0:
            print "Finished converting kt-d-{0}".format(tid)

    print "Conversion complete. {0} documents processed.".format(ct)


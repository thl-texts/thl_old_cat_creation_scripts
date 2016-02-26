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

def get_bibl_template(bpath):
    bibl_template = bpath + "bibl/kt-d-bibl-template.xml"
    bibtree = etree.parse(bibl_template)
    bibroot = bibtree.getroot()
    return bibroot

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
        # Fill in vol info
        volel = bibltmp.xpath('//tibiddecl/tibid//tibid[@type="edition" and @system="sigla"][1]/tibid')[1]
        volel.text = textinfo['stvol']
        volel.getchildren()[0].text = textinfo['stvol-let']
        volel.getchildren()[1].text = textinfo['text-in-vol']
        # Fill in pagination etc
        pageel = bibltmp.xpath('//physdecl/pagination')
        volrs = pageel[0].getchildren()[0]
        volrs.set('n', textinfo["stvol"])
        strs = volrs.getchildren()[0].getchildren()
        sidestr = "a" if textinfo["stsd"] == 1 else "b"
        strs[0].text = textinfo["stpg"] + sidestr
        strs[1].text = textinfo["stln"]
        endrs = volrs.getchildren()[1].getchildren()
        sidestr = "a" if textinfo["endsd"] == 1 else "b"
        endrs[0].text = textinfo["endpg"] + sidestr
        endrs[1].text = textinfo["endln"]
        if textinfo["stvol"] != textinfo["endvol"]:
            print "Multi volume text: " + bid

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

if __name__ == "__main__":
    base_folder = "/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/texts-clone/"
    ed_dir = base_folder + "catalogs/xml/kt/d/"
    mycatpath = ed_dir + 'kt-d-cat.xml'
    cat = THLCatalog(mycatpath, 'mycat')
    allbibs = cat.xpath('/*//xptr[@type="texts"]')
    nobibs = cat.xpath('/*//xptr[@type="texts" and @rend="nobibl"]')
    print "{1} total texts\n{0} without bibl records".format(len(nobibs), len(allbibs))
    tl = cat.get_text_list('nobibl')
    mypath = dirname(abspath(__file__)) + "/"
    print mypath

    load_dictionaries()  # Load the text information into dictionary variables

    for tid in tl:
        if int(tid) > 1118:
            print "End of Kangyur"
            exit(0)
        #print "Creating kt-d-{0}-bib.xml".format(tid)
        bibldoc = get_bibl_template(mypath)
        bibldoc = fill_in_template(bibldoc, tid, cat)
        #print etree.tostring(bibldoc, encoding='utf-8')

        outstr = etree.tostring(bibldoc, encoding='utf-8')
        outstr = unicode(outstr, "utf-8")

        outurl = mypath + "/bibl/new/kt-d-{0}-bib.xml".format(tid)
        xmlout = codecs.open(outurl, "w", "utf-8")
        xmlout.write(outstr)
        xmlout.close()

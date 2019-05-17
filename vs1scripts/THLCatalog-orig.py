# coding=utf-8
# import os
import codecs
from lxml import etree
# from copy import deepcopy
from os import listdir
from os.path import dirname, join
from urllib import urlopen, urlencode
from re import search
from datetime import date

#### THL Catalog Class   ####
class THLCatalog():
    """A class for processing THL catalog documents (not to be confused with OCRProcessing's Catalog)
       Takes a regular THL catalog XML document and extracts information from it
       Initialized with a path to the catalog xml file (catpath) and a machine name/id (name) for the catalog"""

    name = ""
    catpath = ""
    catdoc = ''
    xmltree = None
    root = None

    def __init__(self, catpath, name):
        self.name = name
        catpts = catpath.rpartition('/')
        self.catpath = catpts[0]
        if len(catpts) < 3:
            print "Initial path must contain catalog file name too"
            self.catdoc = ''
        else:
            self.catdoc = catpts[2]
            self.xmltree = etree.parse(self.catpath + "/" + self.catdoc)
            self.root = self.xmltree.getroot()

    def get_name(self):
        return self.name

    def get_root(self):
        """Get the xml root for the catalog document"""
        return False if not self.root else self.root

    def get_dox_for_text(self, tnum, dtype='str'):
        """Get the doxographical category for a text numb either as a id/label (str),
         a list of tib, wylie names for the category, or as an xml element (root) of its text list
         :param tnum: integer text number whose dox cat you want to find
         :param dtype: string type of return value desired ('str', 'tib', 'root') """
        if not self.xmltree:
            return False
        tnum = int(tnum)
        tnumstr = str(tnum).zfill(4)
        parentdiv = self.root.xpath('/*//body//bibl/xptr[@n="' + tnumstr + '"]/ancestor::div[1]')[0]
        doxid = parentdiv.get('id')
        if dtype == 'str':  # Return String ID for doxographical category
            return doxid
        elif dtype == 'tib':  # Return array of tib, wyl for doxographical category label
            return [parentdiv.find('bibl/title/title[1]').text, parentdiv.find('bibl/title/title[2]').text]
        elif dtype == 'root':  # return the root element of the doxographical doc that lists its titles
            doxpath = '{0}/genres/{1}-bib.xml'.format(self.catpath, doxid)
            doxdoc = etree.parse(doxpath)
            doxroot = doxdoc.getroot()
            return doxroot

    def get_text_title(self, tnum, lang='tib'):
        """Get the title for a text in a catalog in the desired language
        :param tnum: integer number of text
        :param lang: string lang to return title in ('tib', 'wyl', 'san')
        :return: the title string in that language
        """
        if not self.xmltree:
            return False
        tnum = int(tnum)
        doxroot = self.get_dox_for_text(tnum, 'root')
        textbibl = doxroot.xpath('/*//idno[@n="dgnum" and text()="' + str(tnum) + '"]/ancestor::bibl[1]')[0]
        tind = 0
        if lang == 'wyl':
            tind = 1
        elif lang == 'san':
            tind = 2
        return textbibl[tind].text

    def get_text_list(self, ltype='all'):
        """Returns a list of texts in catalog
        :param ltype: string denoting type of list to return (all or nobibl only)
        """
        sel = ' and @rend="nobibl"' if ltype == 'nobibl' else ""
        return self.root.xpath('/*//xptr[@type="texts"{0}]/@n'.format(sel))


if __name__ == "__main__":
    mycatpath = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/' \
                'texts-clone/catalogs/xml/kt/d/kt-d-cat.xml'
    bibltemplate = '/Users/thangrove/Box Sync/Projects/THL/Cataloging/Collections/Kangyur_Tengyur/Dege/' \
                   'DegeBiblsTexts/kt-d-nobibl-bib.xml'
    cat = THLCatalog(mycatpath, 'mycat')
    tl = cat.get_text_list('nobibl')
    txtnum = 65
    res = cat.get_dox_for_text(txtnum, 'tib')
    print tl, res[0], res[1]




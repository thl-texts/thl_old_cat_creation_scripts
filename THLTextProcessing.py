# coding=utf-8
#
# __author__ = 'thangrove'

import codecs
from lxml import etree
from os import listdir
from os.path import exists, dirname, join
from urllib import urlopen, urlencode
from datetime import date
import re
from StringIO import StringIO

#### Common Functions ####

def convert_milestone(ms1):
    """Converts Milestone to one with unit attribute before n attribute"""
    ms2 = etree.Element('milestone')
    ms2.set('unit', ms1.get('unit'))
    ms2.set('n',  ms1.get('n'))
    ms2.tail = ms1.tail
    return ms2

####  THLCatalog Class ####
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
            #print etree.tostring(parentdiv)
            titles = parentdiv.xpath('./bibl/title/title')
            #print "titles in catalog", titles
            tibtitle = titles[0].text if len(titles) > 0 else ""
            wytitle = titles[1].text if len(titles) > 1 else ""
            return [tibtitle, wytitle]
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

    def xpath(self, xpathstr):
        """Perform an xpath search on main catalog document"""
        return self.root.xpath(xpathstr)

#### End of THLCatalog Class ###


####  THLSource Class ####
class THLSource(object):
    """THL Source: An Object for manipulating XML data about one text in a catalog

        Attributes:
            source_url : (optional) Url to the source file for the text
            stype : (default = xml) type of source being loaded (xml or text)
            text_root : root element of source
            bibl_url : (optional) URL to the Bibl file
            bibl_root : root element of bibl

        Args:
            source_url (string): the source URL for a volume's text with just pagination in brackets or xml
            is_xml (boolean): whether the source is marked up as XML

        Attributes:
            source_url (string): URL for source assigned from the init arguments
            source (string): Source data read as string in from source_url
            mytree (ElementTree): Marked up and parsed XML data tree from source data
            xml_text (string): Source data wrapped in a <div> element for parsing as XML
            is_xml (boolean): whether or not there is an xml ElementTree for the document
    """

    def __init__(self, source_url='', is_xml=False):
        self.source_url = source_url
        self.source = self.read_doc(self.source_url)
        self.sourcetxt = '' if is_xml else self.source
        self.mytree = None
        self.xml_text = ''
        if not is_xml:
            self.convert_input_to_xml()
            is_xml = True
        self.is_xml = is_xml

    def convert_input_to_xml(self):
        """Converts plain text source data into an XML object

        Attributes:
            mytree (ElementTree): creates lxml element tree of the marked up XML data for a volume created from source
            
        """
        mysource = self.source
        mysource = mysource.replace('[b1]', '[1b]', 1)  # fix mistaken page found in one vol
        mysource = mysource.replace('[]', '')  # remove empty brackets anywhere
        newsource = re.sub(r'\[([^\]\.]+)\]', r'<milestone n="\1" unit="page"/>', mysource)
        newsource = re.sub(r'\[([^\.]+\.[\d])\]', r'<milestone n="\1" unit="line"/>', newsource)
        self.xml_text = u'<div><p>' + newsource + u'</p></div>'
        ftxt = StringIO(self.xml_text)
        self.mytree = etree.parse(ftxt)
        self.source = self.mytree.getroot()
        self.is_xml = True

    def write(self, outurl):
        """Writes either the source text or the parsed XML to a file depending on the value of is_xml

        Args:
            outurl (string): the path and name of the outfile

        """
        if self.is_xml:
            # TODO: do something here NEEDS TO BE FLESHED OUT!
            xfile = codecs.open(outurl, "w", "utf-8")

        else:
            xfile = codecs.open(outurl, "w", "utf-8")
            xfile.write(self.xml_text)
            xfile.close()

    def writetext(self, outurl):
        """Writes just source text to a file regardless on the value of is_xml

        Args:
            outurl (string): the path and name of the outfile

        """
        xfile = codecs.open(outurl, "w", "utf-8")
        xfile.write(self.sourcetxt)
        xfile.close()

    def removecrlf(self):
        """Removes carriage returns before page and line numbers in brackets

        Args:
            outurl (string): the path and name of the outfile

        """
        srctxt = self.sourcetxt
        self.sourcetxt = ''.join(srctxt.splitlines())


    def getmilestone(self, msnum):
        """Returns the milestone element with a given value

        Args:
            msnum (string): the \@n value of the desired milestone

        Returns:
            The milestone as an Element
        """
        lpath = '/*//milestone[@n="{0}"]'.format(msnum)
        msel = self.source.xpath(lpath)
        if len(msel) > 0:
            if len(msel) > 1:
                print "More than one milestone with n={0} in {1}".format(msnum, self.source_url)
            msel = msel[0]
        else:
            print "Milestone, {0}, not found!".format(msnum)
            msel = False
        return msel

    def getline(self, linenum):
        """Converts a milestone and following line to string used by getchunk

        Args:
            linenum (string): The desired line number, e.g. 3b.5

        Returns:
            String represenation of a line preceded by the milestone element
        """
        outln = u''
        if linenum.find(".1") > -1:
            pgnum = linenum.replace(".1", "")
            pg = self.getmilestone(pgnum)
            if pg is not False:
                pg = convert_milestone(pg)  # See the top of this file for this function
                outln += etree.tostring(pg)
        ln = self.getmilestone(linenum)
        if ln is not False:
            ln = convert_milestone(ln)
            tail = ln.tail if ln.tail is not None else u''
            ln.tail = u''
            outln += etree.tostring(ln) + tail
        return outln

    def getchunk(self, stln, endln, wrapper=''):
        """Returns a chunk of the volume with milestones and optionally wrapped in an element of your choice

        Args:
            stln (string): Milestone value for the first line of chunk
            endln (string): Milestone value for the last line of chunk
            wrapper (string/list): Element name to wrap the chunk in, e.g. 'div', 'p', etc. or list of wrapper names

        Returns:
            A string representation of an XML chunk of text
        """
        outchunk = u''
        if isinstance(wrapper, list):
            for en in wrapper:
                outchunk += u'<{0}>'.format(en)
        elif len(wrapper) > 0:
            outchunk = u'<{0}>'.format(wrapper)
        print "Start ln {0}; End ln {1}".format(stln, endln)
        for pn in THLPageIterator(stln, endln):
            # print "Loading {0}".format(pn)
            outln = self.getline(pn)
            outchunk += outln
        if isinstance(wrapper, list):
            for en in reversed(wrapper):
                outchunk += u'</{0}>'.format(en)
        elif len(wrapper) > 0:
            outchunk += u'</{0}>'.format(wrapper)
        return outchunk

    @staticmethod
    def get_xml_root_of_url(url):
        """Parse an XML document from a URL and return the root element"""
        if len(url) > 0:
            xtree = etree.parse(url)
            return xtree.getroot()
        else:
            return False

    @staticmethod
    def read_doc(url):
        """Reads in a document from the given local url"""
        txt = ""
        try:
            vol_in_stream = codecs.open(url, 'r', encoding='utf-8')
            txt = vol_in_stream.read()

        except UnicodeDecodeError:
            try:
                vol_in_stream = codecs.open(url, 'r', encoding='utf-16')
                txt = vol_in_stream.read()

            except UnicodeDecodeError:
                print "Unable to open volume file as either utf8 or utf16"

        return txt

####  THLBibl Class ####
class THLBibl(object):
    """THL Bibl: An object for reading in and extracting information from a Tib Text catalog record or Tibbibl

        Args:


        Attributes:

    """
    def __init__(self, bibl_url):
        print "bibl url: {0}".format(bibl_url)
        self.bibl_url = bibl_url
        self.root = self.read_bibl()

    def read_bibl(self):
        """
        Reads in the bibl XML document and returns the root

        Returns:
            Root Element if URL given otherwise returns FALSE
        """
        if len(self.bibl_url) > 0:
            #print "url is: {0}".format(self.bibl_url)
            tree = etree.parse(self.bibl_url)
            return tree.getroot()
        else:
            return None

    def get_text_number(self):
        xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/' + \
            'tibid[@type="text" and @system="number"]/text()'
        res = self.root.xpath(xpq)
        return res[0]

    def get_volnums(self):
        xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/' + \
            'tibid[@type="volume" and @system="number"]/text()[1]'
        res = self.root.xpath(xpq)
        return res

####  THLText Class ####

class THLText(object):
    """THL Text: An Object for manipulating XML data within a transcribed text file. This can either be a full text or
        a part of a text as found in the /texts folder

        Args:
            text_url (string): Url to the source file for the text
            bibl_url (string): URL to the Bibl file

        Attributes:
            text_root (Element): root element of source
            bibl_root (Element): root element of bibl
    """
    def __init__(self, text_url='', bibl_url=''):
        self.xml_text_url = text_url                        # Url for the text XML file
        if exists(self.xml_text_url):
            self.exists = True
            self.tree = None
            self.xml_text = self.get_xml_root(self.xml_text_url)    # text is the root element of text
            self.bibl_url = ''                              # bibl_url is the url for the bibl xml file
            self.bibl = None                                # bibl is the root element of the bibl file
            if bibl_url:                                    # Can set bibl_url at init or after by calling function
                self.set_bibl(bibl_url)
            pts = text_url.split('/')
            self.file_name = ''                             # file_name is last string part of url
            while self.file_name == '':
                self.file_name = pts.pop()
        else:
            self.exists = False

    def set_bibl(self, bibl_url):
        """Function for setting the bibl url and element of a text"""
        self.bibl_url = bibl_url
        self.bibl = self.get_xml_root(self.bibl_url)

    def getrange(self):
        """Returns the page rage of text as a 2 item list, first item is start line, second is end line

        Returns:
            array containing start and end milestone n attribute or False if no or just one milestone found
        """
        xp = '/*//body//milestone[@unit="line"]/@n'
        mss = self.xml_text.xpath(xp)
        if len(mss) < 2:
            return False
        else:
            return [mss[0],  mss.pop()]

    def getline(self, lnum, mstype='line'):
        """Returns a single line from the text"""
        xp = '/*//body//milestone[@unit="{0}" and @n="{1}"]'.format(mstype, lnum)
        mss = self.xml_text.xpath(xp)
        if len(mss) == 0:
            mss = False

        elif len(mss) == 1:
            mss = etree.tostring(mss[0], encoding='UTF-8')

        return mss

    def replace_p(self, newp='<p></p>'):
        """Replaces the content of the text'sp element with new (proofed) Tibetan text"""
        # Check if multiple <p> elements and write warning
        pct = len(self.xml_text.xpath('/*//text//p'))
        if pct > 1:
            print "{0} <p> elements found in {1}. Replacing all with new text!".format(pct, self.file_name)
        # Read in file
        fout = codecs.open(self.xml_text_url, 'r', encoding='utf-8')
        mytext = fout.read()
        fout.close()
        # Use all inclusive regex to replace <p>
        # Done this way because using lxml resolves all XML entities into XML, which we don't want for writing back out
        pattern = r'<p>[\s\S]+</p>'
        mytext = re.sub(pattern, newp, mytext)
        return mytext

    def write(self, outurl):
        """Writes the text out to a url path

        Args:
            outurl (string): Path to which to write the text

        """
        # place holder for now
        # TODO: Flesh this out
        self.tree.write(outurl, encoding='utf-8', xml_declaration=True)

    def get_xml_root(self, url=''):
        """Gets the root element for the XML document

        Args:
            url (string): Url of the file to parse into XML

        Returns:
            Root Element if URL given otherwise returns FALSE
        """
        if len(url) > 0:
            #print "url is: {0}".format(url)
            self.tree = etree.parse(url)
            return self.tree.getroot()
        else:
            return False

    def xpath(self, xpstr):
        print "Xpath query is: {0}".format(xpstr)
        return self.xml_text.xpath(xpstr)

    @staticmethod
    def read_doc(url):
        """Reads in a Document

        Args:
            url (string): Path to the document to read in

        Returns:
            Text of the read document
        """
        vol_in_stream = codecs.open(url, 'r', encoding='utf-16')
        txt = vol_in_stream.read()
        return txt

####  THL Page Iterator for sides with a/b and ####

class THLPageIterator:
    def __init__(self, st, en, numlines=7):
        self.numlines = numlines
        # for cases where milestone mistakenly has multiple line values: 101a.1101a.2... etc.
        if st.count('.') > 1:
            st = st[0:st.find('.') + 2]
        if en.count('.') > 1:
            en = en[0:en.find('.') + 2]
        pts = st.split('.')
        # go back one line to include start line given
        stpg = pts[0]
        stln = int(pts[1]) - 1
        if stln == 0:
            if stpg.find('b') > -1:
                stpg = stpg.replace('b', 'a')
            else:
                stpg = str(int(stpg.replace('a', '')) - 1) + 'b'
            stln = self.numlines
        self.pg = stpg
        self.ln = int(stln)
        pts = en.split('.')
        self.endpg = pts[0]
        self.endln = pts[1]

    def __iter__(self):
        return self

    def next(self):
        self.ln += 1
        if self.ln > self.numlines:
            if self.pg.find('a') > -1:
                self.pg = self.pg.replace('a', 'b')
            else:
                npg = self.pg.replace('b', '')
                npg = int(npg) + 1
                self.pg = str(npg) + "a"
            self.ln = 1

        if self.pg == self.endpg and int(self.ln) > int(self.endln):
            raise StopIteration
        elif self.pg == self.endpg.replace('a', 'b'):
            raise StopIteration
        elif int(self.pg.replace('a', '').replace('b', '')) > int(self.endpg.replace('a', '').replace('b', '')):
            raise StopIteration
        else:
            return self.pg + "." + str(self.ln)

if __name__ == "__main__":

    mycatpath = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/' \
                'texts-clone/catalogs/xml/kt/d/kt-d-cat.xml'
    cat = THLCatalog(mycatpath, 'mycat')
    tl = cat.get_text_list('nobibl')
    print tl

    # myurl = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/test-out/crlftest.txt'
    # srcobj = THLSource(myurl)
    # srcobj.removecrlf()
    #
    # print srcobj.sourcetxt

    #biblurl = '/Users/thangrove/Sites/texts/dev/catalogs/xml/kt/d/0/kt-d-0001-bib.xml'
    #print biblurl


    #bibl = THLBibl(biblurl)
    #print bibl.get_volnums()

    # Old Code
    #text1url = '/Users/thangrove/Sites/texts/dev/catalogs/xml/kt/d/texts/0002/kt-d-0002-text.xml'
    #outpath = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/'
    #outfile = outpath + 'kd-d-0002-replaced.xml'
    #text1 = THLText(text1url)
    #rng = text1.getrange()
    #print "Before replacing the text ranges from {0} to {1}".format(rng[0], rng[1])

    #chunk = text2.getchunk('1b.1', '3a.1')

    #  OLD CODE

    #test_path2 = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/testvol.txt'
    #chunkout = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/testchunk.xml'
    #text2 = THLSource(test_path2)
    #text2.convert_input_to_xml()
    #ms = text2.getmilestone('2a.6')
    #print etree.tostring(ms, encoding='utf-8')

    # text2.write(outpath)
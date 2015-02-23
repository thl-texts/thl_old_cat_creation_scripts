__author__ = 'thangrove'

import codecs
from lxml import etree
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


####  THLSource Class ####
class THLSource(object):
    """THL Text: An Object for manipulating XML data about one text in a catalog

        Attributes:
            source_url : (optional) Url to the source file for the text
            stype : (default = xml) type of source being loaded (xml or text)
            text_root : root element of source
            bibl_url : (optional) URL to the Bibl file
            bibl_root : root element of bibl
    """

    def __init__(self, source_url='', is_xml=False):
        self.source_url = source_url
        self.source = self.read_doc(self.source_url)
        self.mytree = None
        self.text = ''
        self.is_xml = is_xml

    def convert_input_to_xml(self):
        mysource = self.source
        mysource = mysource.replace('[b1]', '[1b]', 1)
        newsource = re.sub(r'\[([^\]\.]+)\]', r'<milestone n="\1" unit="page"/>', mysource)
        newsource = re.sub(r'\[([^\.]+\.[\d])\]', r'<milestone n="\1" unit="line"/>', newsource)
        self.text = u'<div>' + newsource + u'</div>'
        ftxt = StringIO(self.text)
        self.mytree = etree.parse(ftxt)
        self.source = self.mytree.getroot()
        self.is_xml = True

    def write(self, outurl):
        if self.is_xml:
            # TODO: do something here NEEDS TO BE FLESHED OUT!
            xfile = codecs.open(outurl, "w", "utf-8")

        else:
            xfile = codecs.open(outurl, "w", "utf-8")
            xfile.write(self.text)
            xfile.close()

    def getmilestone(self, msnum):
        lpath = '/*//milestone[@n="{0}"]'.format(msnum)
        msel = self.source.xpath(lpath)
        if len(msel) > 0:
            if len(msel) > 1:
                print "More than one milestone with n={0}".format(msnum)
            msel = msel[0]
        else:
            print "Milestone, {0}, not found!".format(msnum)
            msel = False
        return msel

    def getline(self, linenum):
        outln = u''
        if linenum.find(".1") > -1:
            pgnum = linenum.replace(".1", "")
            pg = self.getmilestone(pgnum)
            if pg is not False:
                pg = convert_milestone(pg)
                outln += etree.tostring(pg)
        ln = self.getmilestone(linenum)
        if ln is not False:
            ln = convert_milestone(ln)
            tail = ln.tail
            ln.tail = u''
            outln += etree.tostring(ln) + tail
        return outln

    def getchunk(self, stln, endln, wrapper='p'):
        outchunk = u''
        if len(wrapper) > 0:
            outchunk = u'<{0}>'.format(wrapper)
        for pn in THLPageIterator(stln, endln):
            # print "Loading {0}".format(pn)
            outln = self.getline(pn)
            outchunk += outln
        if len(wrapper) > 0:
            outchunk += u'</{0}>'.format(wrapper)
        return outchunk

    @staticmethod
    def get_xml_root_of_url(url):
        if len(url) > 0:
            xtree = etree.parse(url)
            return xtree.getroot()
        else:
            return False

    @staticmethod
    def read_doc(url):
        vol_in_stream = codecs.open(url, 'r', encoding='utf-16')
        txt = vol_in_stream.read()
        return txt

####  THLText Class ####

class THLText(object):
    """THL Text: An Object for manipulating XML data about one text in a catalog

        Parameter Attributes:
            text_url : (optional) Url to the source file for the text
            bibl_url : (optional) URL to the Bibl file
        Internal Attributes:
            text_root : oot element of source
            bibl_root : root element of bibl
    """

    def __init__(self, text_url, bibl_url=''):
        self.text_url = text_url                        # Url for the text XML file
        self.tree = None
        self.text = self.get_xml_root(self.text_url)    # text is the root element of text
        self.bibl_url = ''                              # bibl_url is the url for the bibl xml file
        self.bibl = None                                # bibl is the root element of the bibl file
        if bibl_url:                                    # Can set bibl_url at init or after by calling function
            self.set_bibl(bibl_url)
        pts = text_url.split('/')
        self.file_name = ''                             # file_name is last string part of url
        while self.file_name == '':
            self.file_name = pts.pop()

    def set_bibl(self, bibl_url):
        """Function for setting the bibl url and element of a text"""
        self.bibl_url = bibl_url
        self.bibl = self.get_xml_root(self.bibl_url)

    def getrange(self):
        """Returns the page rage of text as a 2 item list, first item is start line, second is end line"""
        xp = '/*//body//milestone[@unit="line"]/@n'
        mss = self.text.xpath(xp)
        return [mss[0],  mss.pop()]

    def replace_p(self, newp='<p></p>'):
        """Replaces the content of the text'sp element with new (proofed) Tibetan text"""
        # Check if multiple <p> elements and write warning
        pct = len(self.text.xpath('/*//text//p'))
        if pct > 1:
            print "{0} <p> elements found in {1}. Replacing all with new text!".format(pct, self.file_name)
        # Read in file
        fout = codecs.open(self.text_url, 'r', encoding='utf-8')
        mytext = fout.read()
        fout.close()
        # Use all inclusive regex to replace <p>
        # Done this way because using lxml resolves all XML entities into XML, which we don't want for writing back out
        pattern = r'<p>[\s\S]+</p>'
        mytext = re.sub(pattern, newp, mytext)
        return mytext

    def write(self, outurl):
        # place holder for now
        # TODO: Flesh this out
        self.tree.write(outurl, encoding='utf-8', xml_declaration=True)

    def get_xml_root(self, url=''):
        if len(url) > 0:
            print "url is: {0}".format(url)
            self.tree = etree.parse(url)
            return self.tree.getroot()
        else:
            return False

    @staticmethod
    def read_doc(url):
        vol_in_stream = codecs.open(url, 'r', encoding='utf-16')
        txt = vol_in_stream.read()
        return txt

####  THL Page Iterator for sides with a/b and ####

class THLPageIterator:
    def __init__(self, st, en, numlines=7):
        self.numlines = numlines
        pts = st.split('.')
        # go back one line to include start line given
        stpg = pts[0]
        stln = int(pts[1]) - 1
        if stln == 0:
            if stpg.find('b') > -1:
                stpg = stpg.replace('b', 'a')
            else:
                stpg = str(int(stpg.replace('a','')) - 1) + 'b'
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
    text1url = '/Users/thangrove/Sites/texts/dev/catalogs/xml/kt/d/texts/0002/kt-d-0002-text.xml'
    outpath = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/'
    outfile = outpath + 'kd-d-0002-replaced.xml'
    text1 = THLText(text1url)
    rng = text1.getrange()
    print "Before replacing the text ranges from {0} to {1}".format(rng[0], rng[1])

    chunk = text2.getchunk('1b.1', '3a.1')

    #  OLD CODE

    #test_path2 = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/testvol.txt'
    #chunkout = '/Users/thangrove/Documents/Project Data/THL/DegeKT/ProofedVols/test/testchunk.xml'
    #text2 = THLSource(test_path2)
    #text2.convert_input_to_xml()
    #ms = text2.getmilestone('2a.6')
    #print etree.tostring(ms, encoding='utf-8')

    # text2.write(outpath)
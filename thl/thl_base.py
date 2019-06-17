"""
ThlBase is the base object for all the classes in this package.
It assumes that the class/object is base on data stored in a file, XML or otherwise
Or else it is to create such a file
"""

from lxml import etree
import os
import os.path


class THLBase(object):
    path = ''
    filename = ''
    content = ''
    catname = ''
    catsig = ''
    edname = ''
    edsig = ''
    id = ''
    type = 'base'
    is_xml = False
    xmltree = None
    root = None

    def __init__(self, path='', is_xml=False):
        self.path = path
        self.filename = os.path.basename(self.path)
        self.is_xml = is_xml
        if self.is_xml:
            self.load_xml()
        else:
            self.load_doc()

    def load_xml(self):
        if self.path is not '':
            self.xmltree = etree.parse(self.path)
            if self.xmltree:
                self.root = self.xmltree.getroot();

    def load_doc(self):
        if self.path is not '':
            self.content = self.read_doc(self.path)

    def read_doc(self, url):
        """Reads in a document from the given local url"""
        try:
           with open(url, 'r', encoding='utf-8') as filein:
                txt = filein.read()

        except Exception as e:
                print("Unable to open file: {}".format(e))
                txt = None
        return txt

    def xpath(self, xpathstr):
        """Perform an xpath search on main catalog document"""
        return self.root.xpath(xpathstr)

    def convert_milestone(self, ms1):
        """Converts Milestone to one with unit attribute before n attribute"""
        ms2 = etree.Element('milestone')
        ms2.set('unit', ms1.get('unit'))
        ms2.set('n', ms1.get('n'))
        ms2.tail = ms1.tail
        return ms2

    def write(self, outpath=''):
        outpath = outpath if outpath is not '' else self.path
        if self.is_xml:
            outdoc = etree.tostring(self.root, pretty_print=True)
        else:
            outdoc = self.content
        with open(outpath, "wb") as outp:
            outp.write(outdoc)


class THLPageIterator:
    def __init__(self, st, en, numlines=7):
        self.numlines = numlines
        #  print "st: {0}, en: {1}".format(st, en)
        st = st.replace(',', '.')
        en = en.replace(',', '.')
        # for cases where milestone mistakenly has multiple line values: 101a.1101a.2... etc.
        if st.count('.') > 1:
            st = st[0:st.find('.') + 2]
        if en.count('.') > 1:
            en = en[0:en.find('.') + 2]
        pts = st.split('.')
        # go back one line to include start line given
        stpg = pts[0]
        #print pts
        stln = int(pts[1]) - 1
        if stln == 0:
            if stpg.find('b') > -1:
                stpg = stpg.replace('b', 'a')
            else:
                stpg = str(int(stpg.replace('a', '')) - 1) + 'b'
            stln = self.numlines
        self.pg = stpg
        self.ln = int(stln)
        if en:
            pts = en.split('.')
            self.endpg = pts[0]
            self.endln = pts[1]
        else:
            self.endpg = stpg
            self.endln = int(stln)
            print("Warning! No End line found in page iterator. Assuming one line text!")

    def __iter__(self):
        return self

    def __next__(self):
        self.ln += 1
        if self.ln > self.numlines:
            if self.pg.find('a') > -1:
                self.pg = self.pg.replace('a', 'b')
            else:
                npg = self.pg.replace('b', '')
                npg = int(npg) + 1
                self.pg = str(npg) + "a"
            self.ln = 1

        # Stop Iteration if...
        if self.pg == self.endpg and int(self.ln) > int(self.endln): # iterator is on end page at a line past the end
            raise StopIteration
        elif 'a' in self.endpg and self.pg == self.endpg.replace('a','b'): # iterator is on the b page when the end page is an a page
           raise StopIteration
        elif int(self.pg.replace('a', '').replace('b', '')) > int(self.endpg.replace('a', '').replace('b', '')):
            # the number value of the iterators page is greater than the number value of the end page
            raise StopIteration
        else:
            return self.pg + "." + str(self.ln)

class THLTextException(Exception):
    def __init__(self, eargs):
        Exception.__init__(self, "Could not find Milestone {0} in THL text processing function {1}".format(
            eargs.get('msnum'), eargs.get('funcname')))
        self.ErrorArguments = eargs


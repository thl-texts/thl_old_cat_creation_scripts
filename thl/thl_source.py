####  THL Source Class ####
import re
from io import StringIO
import html
from .thl_base import *

class THLSource(THLBase):
    """THL Source: An Object for manipulating XML data about one text in a catalog

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
        super().__init__(source_url, is_xml)
        self.type = 'source'
        if self.content is None:
            print ("No source content to convert!")
        elif not self.is_xml:
            self.convert_input_to_xml()
            self.is_xml = True

    def convert_input_to_xml(self):
        """Converts plain text source data into an XML object

        Attributes:
            mytree (ElementTree): creates lxml element tree of the marked up XML data for a volume created from source

        """
        mysource = self.content
        mysource = mysource.replace('[b1]', '[1b]', 1)  # fix mistaken page found in one vol
        mysource = mysource.replace('[]', '')  # remove empty brackets anywhere
        newsource = re.sub(r'\[([^\]\.]+)\]', r'<milestone n="\1" unit="page"/>', mysource)
        newsource = re.sub(r'\[([^\.]+\.[\d])\]', r'<milestone n="\1" unit="line"/>', newsource)
        self.xml_text = '<div><p>' + newsource + '</p></div>'
        ftxt = StringIO(self.xml_text)
        magical_parser = etree.XMLParser(encoding='utf-8', recover=True)  # prevents failing on encoding errors
        self.mytree = etree.parse(ftxt, magical_parser)
        self.root = self.mytree.getroot()
        self.is_xml = True


    def removecrlf(self):
        """Removes carriage returns before page and line numbers in brackets

        Args:
            outurl (string): the path and name of the outfile

        """
        srctxt = self.content

        # remove paragraph returns in middle of line before page/line numbers
        srcjoined = ''.join(srctxt.splitlines())
        p = r'([ཀ-ྼ་])།([ཀ-ྼ])'
        r = '\g<1>། \g<2>'
        srcjoined = re.sub(p, r, srcjoined)

        # Add paragraph return after each space
        p = r'\s+'
        r = " \n"
        srcjoined = re.sub(p, r, srcjoined)
        self.content = srcjoined

    def getmilestone(self, msnum):
        """Returns the milestone element with a given value

        Args:
            msnum (string): the \@n value of the desired milestone

        Returns:
            The milestone as an Element
        """
        lpath = '/*//milestone[@n="{0}"]'.format(msnum)
        msel = self.xpath(lpath)
        if len(msel) > 0:
            if len(msel) > 1:
                print("\nMore than one milestone with n={0} in {1}\n".format(msnum, self.source_url))
            msel = msel[0]
        else:
            # print "Milestone, {0}, not found!".format(msnum)
            raise THLTextException({'msnum': msnum, 'funcname': 'getMilestone'})

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
            #  If it's line one, also get the page milestone
            pgnum = linenum.replace(".1", "")
            pg = self.getmilestone(pgnum)
            if pg is not False:
                pg = self.convert_milestone(pg)
                bytstr = etree.tostring(pg)  # No tail on page milestone because folled by line 1
                outln += bytstr.decode('utf-8')
        ln = self.getmilestone(linenum)
        if ln is not False:
            ln = self.convert_milestone(ln)
            bytstr = etree.tostring(ln, with_tail=True)  # Get tail with line milestones to include following text
            outln += bytstr.decode('utf-8')
        outln = html.unescape(outln)
        return outln

    def getchunk(self, stln, endln, wrapper='', text_delimiter=False):
        """Returns a chunk of the volume with milestones and optionally wrapped in an element of your choice

        Args:
            stln (string): Milestone value for the first line of chunk
            endln (string): Milestone value for the last line of chunk
            wrapper (string/list): Element name to wrap the chunk in, e.g. 'div', 'p', etc. or list of wrapper names

        Returns:
            A string representation of an XML chunk of text
        """
        if self.content is None:
            return "No data available!"

        outchunk = u''
        msgs = []
        if isinstance(wrapper, list):
            for en in wrapper:
                outchunk += u'<{0}>'.format(en)
        elif len(wrapper) > 0:
            outchunk = u'<{0}>'.format(wrapper)
        msgs.append("info:Start ln {0}; End ln {1}".format(stln, endln))
        for pn in THLPageIterator(stln, endln):
            # print "Loading {0}".format(pn)
            try:
                outln = self.getline(pn)
                if text_delimiter and text_delimiter in outln:
                    if pn == stln:
                        pts = outln.split(text_delimiter)
                        ind = pts[0].rfind('/>') + 2  # Find index for end of the last milestone
                        mst = pts[0][:ind]  # get the string for the milestone(s) could be page and line milestones
                        outln = u'{0}{1}{2}'.format(mst, text_delimiter, pts[1])
                    if pn == endln:
                        pts = outln.split(text_delimiter)
                        outln = u'{}'.format(pts[0])
                outchunk += outln
            except thl_base.THLTextException as te:
                # print('error: {0}'.format(te))
                msgs.append('error: {0}'.format(te))

        if isinstance(wrapper, list):
            for en in reversed(wrapper):
                outchunk += u'</{0}>'.format(en)
        elif len(wrapper) > 0:
            outchunk += u'</{0}>'.format(wrapper)
        # Replace spaces with non-breaking spaces
        # patt = r'།\s+'
        # rep = u'། '  # space here is nbsp unichr(160)
        # outchunk = re.sub(patt, rep, outchunk)
        # patt = r'ག\s+'
        # rep = u'ག '  # space here is nbsp unichr(160)
        # outchunk = re.sub(patt, rep, outchunk)
        return outchunk, msgs

    def getlastline(self, mode="number"):
        lpath = '/*//milestone[@unit="line"][last()]'
        if mode == "number":
            lpath += '/@n'
        msel = self.xpath(lpath)
        if len(msel) > 0:
            return msel[0]
        else:
            return False

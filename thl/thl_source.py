####  THL Source Class ####
import re
from io import StringIO
from lxml import etree
from . import thl_base


####  THLSource Class ####
class THLSource(thl_base.ThlBase):
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
        super().__init__(source_url, is_xml)
        if not self.is_xml:
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
        self.xml_text = u'<div><p>' + newsource + u'</p></div>'
        ftxt = StringIO(self.xml_text)
        magical_parser = etree.XMLParser(encoding='utf-8', recover=True)  # prevents failing on encoding errors
        self.mytree = etree.parse(ftxt, magical_parser)
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

        # remove paragraph returns in middle of line before page/line numbers
        srcjoined = ''.join(srctxt.splitlines())
        p = u'([ཀ-ྼ་])།([ཀ-ྼ])'
        r = u'\g<1>། \g<2>'
        srcjoined = re.sub(p, r, srcjoined)

        # Add paragraph return after each space
        p = u' '
        r = u" \n"
        srcjoined = re.sub(p, r, srcjoined)
        self.sourcetxt = srcjoined

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
                print
                "\nMore than one milestone with n={0} in {1}\n".format(msnum, self.source_url)
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

    def getchunk(self, stln, endln, wrapper='', text_delimiter=False):
        """Returns a chunk of the volume with milestones and optionally wrapped in an element of your choice

        Args:
            stln (string): Milestone value for the first line of chunk
            endln (string): Milestone value for the last line of chunk
            wrapper (string/list): Element name to wrap the chunk in, e.g. 'div', 'p', etc. or list of wrapper names

        Returns:
            A string representation of an XML chunk of text
        """
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
                        outln = u"{0}{1}{2}".format(mst, text_delimiter, pts[1])
                    if pn == endln:
                        pts = outln.split(text_delimiter)
                        outln = pts[0]
                outchunk += outln
            except THLTextException as te:
                msgs.append('error: {0}'.format(te))

        if isinstance(wrapper, list):
            for en in reversed(wrapper):
                outchunk += u'</{0}>'.format(en)
        elif len(wrapper) > 0:
            outchunk += u'</{0}>'.format(wrapper)
        # Replace spaces with non-breaking spaces
        patt = u'།\s+'
        rep = u'།\xa0'  # space here is nbsp unichr(160)
        outchunk = re.sub(patt, rep, outchunk)
        patt = u'ག\s+'
        rep = u'ག\xa0'  # space here is nbsp unichr(160)
        outchunk = re.sub(patt, rep, outchunk)
        return outchunk, msgs

    def getlastline(self, mode="number"):
        lpath = '/*//milestone[@unit="line"][last()]'
        if mode == "number":
            lpath += '/@n'
        msel = self.source.xpath(lpath)
        if len(msel) > 0:
            return msel[0]
        else:
            return False

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
                print
                "Unable to open volume file as either utf8 or utf16"

        return txt

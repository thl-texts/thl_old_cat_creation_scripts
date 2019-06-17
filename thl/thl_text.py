
####  THLText Class ####
from os import path
from .thl_base import *

class THLText(THLBase):
    """THL Text: An Object for manipulating XML data within a transcribed text file. This can either be a full text or
        a part of a text as found in the /texts folder

        Args:
            text_url (string): Url to the source file for the text
            bibl_url (string): URL to the Bibl file

        Attributes:
            text_root (Element): root element of source
            bibl_root (Element): root element of bibl
    """
    exists = False
    bibl_url = ''
    bibl = None

    def __init__(self, text_url='', bibl_url=''):
        self.xml_text_url = text_url.replace('//', '/')                        # Url for the text XML file
        if path.exists(self.xml_text_url):
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
            self.xml_text = False

    def set_bibl(self, bibl_url):
        """Function for setting the bibl url and element of a text"""
        self.bibl_url = bibl_url
        self.bibl = self.get_xml_root(self.bibl_url)

    def get_page_file(self, pgnum):
        """
        Only for use with -text.xml files the list subfiles, finds the subfile containing that page.
        :param pgnum: string pagenumber as in "123b.4"
        :return: THLText file with that page
        """
        mtc = re.findall(r"(\d+)[ab]\.\d", pgnum)
        pgnum = mtc.pop() if mtc else False
        if pgnum:
            pgnum = int(pgnum)
            xp = '/*//body//div[@type="vol"]//list/item/num[@type="pages"]'
            pitems = self.xml_text.xpath(xp)
            for pi in pitems:
                rng = pi.text.split("-")
                if len(rng) == 2:
                    if int(rng[0]) <= pgnum <= int(rng[1]):
                        # Previous tag is the xref
                        lind = self.xml_text_url.rfind("/") + 1
                        newurl = self.xml_text_url[0:lind] + pi.getprevious().text
                        return THLText(newurl)

        return self

    def getrange(self):
        """Returns the page rage of text as a 2 item list, first item is start line, second is end line

        Returns:
            array containing start and end milestone n attribute or False if no or just one milestone found
        """
        if self.xml_text is not False and self.xml_text is not None:
            xp = '/*//body//milestone[@unit="line"]/@n'
            mss = self.xml_text.xpath(xp)
            if len(mss) < 2:
                return False

            # Sometime first milestone has no n attribute value so use the next one
            if not mss[0]:
                return [mss[1],  mss.pop()]
            else:
                return [mss[0],  mss.pop()]
        else:
            return False

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
        """Replaces the content of the text'sp element with new-first (proofed) Tibetan text"""
        # Check if multiple <p> elements and write warning
        pct = len(self.xml_text.xpath('/*//text//p'))
        # if pct > 1:
            #print "{0} <p> elements found in {1}. Replacing all with new-first text!".format(pct, self.file_name)
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
        #print "Xpath query is: {0}".format(xpstr)
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

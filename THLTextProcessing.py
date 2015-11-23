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
# Taken from OCRProcessing Catalog.py

my_path = dirname(__file__)
tmpl_path = join(my_path, 'templates')
data_path = join(my_path, '..', 'data')
vol_dir = join(my_path, '..', '..', 'volsource')  # directory which contains OCR volume files


class THLCatalog():
    """A class for processing an XML document that is a list of texts.
       The XML expected here is based on the simple schema for mapping from an Excell document,
       Peltsek_Excell_Datamap.xsd This is a <spreadsheet> element with a series of <textrecord>s in it. Each text
       record has the following children:
         tnum, key, title, vnum, startpage, endpage, numofchaps, chaptype, doxography, translators, crossrefs, notes """

    docpath = ""
    tree = None
    colname = {
        "eng": "",
        "tib": "",
        "wyl": ""
    }
    coll = ""
    sigla = ""
    vols = {}
    texts = {}
    textcount = 0
    volcount = 0
    voldir = ""

    def __init__(self, path, name, voldir=vol_dir):
        """Takes a path to an XML document and parse it, creating two dictionary attributes:
            1. vols = an dictionary of volumes keyed on vol num and 2. texts a dictionary of texts keyed on text num"""
        try:
            self.name = name
            self.voldir = voldir
            seqvnum = 0
            oldvnum = 0
            # done = False

            # Load XML doc and perform xpath search for text elements
            self.tree = etree.parse(path)
            root = self.tree.getroot()
            textels = root.xpath('/*//' + Vars.textelement)

            # Iterate through the text elements found in the XML doc
            for txt in textels:
                vnum = txt.find(Vars.vnumelement).text  # volume number in catalog
                if vnum != oldvnum:                    # sequential volume number
                    seqvnum += 1
                    oldvnum = vnum

                # Calculate sequential numbering by counting number of preceding text elements
                pt = txt.itersiblings(tag=Vars.textelement, preceding=True)
                tnum = len(list(pt)) + 1  # calculate text number as number of preceding siblings plus one

                # Add the text to the volumes text list or else start a new vol text list
                if seqvnum in self.vols:
                    self.vols[seqvnum]["texts"].append(tnum)
                else:
                    self.vols[seqvnum] = {"texts": [tnum]}

                # If there is no ID element with sequential number then add one
                if txt.find(Vars.idel) is None:
                    se = etree.Element(Vars.idel)
                    se.text = unicode(str(tnum))
                    txt.find("tnum").addprevious(se)

                # Add the element to the text list using its sequential number as id
                self.texts[tnum] = txt

            # set the object's textcount and volcount
            self.textcount = len(self.texts)
            self.volcount = len(self.vols)

            #print "Automatically fixing missing paginations and line numbers."
            #print "To disable this, comment out Catalog.py line 88 and 89."
            #self.fixMissingPaginations()
            #self.fixMissingPaginations()
            #  above is hack to cover those ending paginations where there is not start pagination for following texts
        except IOError:
            print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(path)

    @staticmethod
    def __type__():
        return "THL Catalog"

    # General THL Catalog Functions
    def write(self, path, outtype="simple", doc="self"):
        """Function to write either the catalog, volume tocs or volume bibls"""
        if outtype == "simple":
            if doc == "self":
                doc = self.tree
            fout = codecs.open(path, 'w', encoding='utf-8')
            fout.write(etree.tostring(doc, encoding=unicode))
            fout.close()

        # vols outtype produces a div structure of volumes in TEI format
        elif outtype == "vols":
            catroot = etree.Element("div", {"type": "vols"})
            voltemplate = join(tmpl_path, 'toc-vol.xml')
            txttemplate = join(tmpl_path, 'toc-text.xml')
            for k, v in self.vols.iteritems():
                vdoc = etree.parse(voltemplate).getroot()
                vid = "ngb-pt-v" + str(int(k)).zfill(3)
                print "VID is: {0}".format(vid)
                vnum = int(k)
                vdoc.set('id', vid)
                set_template_val(vdoc, '/*//title[@id="vtitle"]', "Volume {0}".format(vnum))
                vnumel = vdoc.xpath('/*//num[@id="vnum"]')[0]
                vnumel.set('n', v['wylie'])
                vnumel.set('value', str(vnum))
                vnumel.text = v['tib']
                vnumel.attrib.pop("id")
                set_template_val(vdoc, '/*//num[@id="starttxt"]', v['texts'][0])
                set_template_val(vdoc, '/*//num[@id="endtxt"]', v['texts'][-1])
                for txt in self.get_volume_toc(k, 'list'):
                    tdoc = etree.parse(txttemplate).getroot()
                    tid = "ngb-pt-{0}".format(txt["key"].zfill(4))
                    tdoc.set("id", tid)
                    title = txt["title"]
                    set_template_val(tdoc, '/*//title[@id="tibtitle"]', title)
                    set_template_val(tdoc, '/*//title[@id="wylietitle"]', self.tib_to_wylie(title))
                    set_template_val(tdoc, '/*//idno[@id="tid"]', txt["key"].zfill(4))
                    if txt["start"] is not None:
                        stpg = txt["start"].split('.')
                        set_template_val(tdoc, '/*//num[@id="stpg"]', stpg[0])
                        if len(stpg) == 2:
                            set_template_val(tdoc, '/*//num[@id="stln"]', stpg[1])
                        else:
                            set_template_val(tdoc, '/*//num[@id="stln"]', "1")
                    else:
                        self.remove_attributes(tdoc, 'id', ['stpg', 'stln'])
                    if txt["end"] is not None:
                        endpg = txt["end"].split('.')
                        set_template_val(tdoc, '/*//num[@id="endpg"]', endpg[0])
                        if len(endpg) == 2:
                            set_template_val(tdoc, '/*//num[@id="endln"]', endpg[1])
                        else:
                            set_template_val(tdoc, '/*//num[@id="endln"]', "6")
                    else:
                        self.remove_attributes(tdoc, 'id', ['endpg', 'endln'])
                    vdoc.append(tdoc)
                catroot.append(vdoc)
            fout = codecs.open(path, 'w', encoding='utf-8')
            fout.write(etree.tostring(catroot, encoding=unicode))
            fout.close()

        # Output of volume bibls using template
        elif outtype == "volbibs":
            voltemplate = join(tmpl_path, 'volbib.xml')
            for k, v in self.vols.iteritems():
                vdoc = etree.parse(voltemplate).getroot()
                vid = "ngb-pt-v" + str(int(k)).zfill(3)
                print "VID is: {0}".format(vid)
                #  vnum = int(k)
                vdoc.set('id', vid)
                set_template_val(vdoc, '/*//sysid[@id="sysid"]', vid)
                set_template_val(vdoc, '/*/controlinfo/date', str(date.today()))
                set_template_val(vdoc, '/*//tibid[@id="vid"]', k)
                set_template_val(vdoc, '/*//altid[@id="vlet"]', v['tib'], v['wylie'])
                set_template_val(vdoc, '/*//rs[@id="vollabel"]', u"༼" + v['tib'] + u"༽")
                set_template_val(vdoc, '/*//divcount[@id="texttotal"]', v['tcount'])
                set_template_val(vdoc, '/*//extent[@id="textfirst"]', "Pt." + str(v['texts'][0]))
                set_template_val(vdoc, '/*//extent[@id="textlast"]', "Pt." + str(v['texts'][-1]))
                set_template_val(vdoc, '/*//extent[@id="sides"]', v['lastpage'])
                set_template_val(vdoc, '/*//num[@id="pagelast"]', v['lastpage'])
                fout = codecs.open(join(path, vid + "-bib.xml"), 'w', encoding='utf-8')
                fout.write(etree.tostring(vdoc, encoding=unicode))
                fout.close()

    # Volume Functions in THL Catalog
    def import_vol_info(self, path):
        voldoc = etree.parse(path).getroot()
        volels = voldoc.xpath('/*//volume')
        for vol in volels:
            vnum = int(vol.find('num').text)
            vobj = self.get_volume(vnum)
            if vobj is not None:
                vobj['wylie'] = vol.find('name[@lang="wylie"]').text
                vobj['tib'] = vol.find('name[@lang="tib"]').text
                vobj['dox'] = vol.find('dox').text
                vobj['tcount'] = vol.find('textcount').text
                vsstr = "vol" + str(vnum).zfill(2)
                lasttext = self.get_text(vobj['texts'][-1])
                if lasttext and isinstance(lasttext.endpage, str):
                    vobj['lastpage'] = int(float(lasttext.endpage))
                for f in listdir(self.voldir):
                    if vsstr in f:
                        vobj['ocrfile'] = join(self.voldir, f)
                        break

    def fix_missing_paginations(self):
        """This function inserts missing paginations based on the previous or subsequent texts' paginations"""
        # First fix problem with start page
        spct = 0
        enct = 0
        nofix = 0
        tlist = {}
        for tn in self.texts:
            ptxt = self.texts[tn - 1] if tn > 1 else None
            ntxt = self.texts[tn + 1] if tn < len(self.texts) else None
            t = self.texts[tn]
            tid = t.find("key").text

            # Fix Start pages
            startpg = t.find("startpage").text
            if isinstance(startpg, str):
                # if no line number for start page assume, get line from prev text if page same
                # otherwise assume line .1
                linenm = ".1"
                if not "." in startpg:
                    if ptxt is not None:
                        pend = ptxt.find("endpage").text
                        if isinstance(pend, str) and "." in pend:
                            pendpts = pend.split('.')
                            if pendpts[0] == startpg and len(pendpts) > 1:
                                linenm = "." + pendpts[1]
                            elif int(pendpts[0]) == int(startpg) - 1 and int(pendpts[1]) == 6:
                                linenm = ".1"
                    t.find("startpage").text = startpg + linenm
                    spct += 1
                    tlist[tid] = 1
            elif ptxt is not None:
                # if no page number then get it from the previous texts ending
                pend = ptxt.find("endpage").text
                if pend:
                    if ".6" in pend:  # if previous text ends at .6 assume this test starts at .1 of next page
                        pend = str(int(float(pend)) + 1) + ".1"
                    t.find("startpage").text = pend
                    spct += 1
                    tlist[tid] = 1
            else:
                print "text {0} has no start page and can't find previous text".format(tid)
                nofix += 1

            # Fix End pages
            endpage = t.find("endpage").text
            if isinstance(endpage, str):
                # if not end line number get from next text start page if the same page
                # else assume line 6
                linenm = ".6"
                if not "." in endpage:
                    if ntxt is not None:
                        nst = ntxt.find("startpage").text
                        if isinstance(nst, str) and "." in nst:
                            nstpts = nst.split('.')
                            if nstpts[0] == endpage and len(nstpts) > 1:
                                linenm = "." + nstpts[1]
                            if int(nstpts[0]) == int(endpage) + 1 and int(nstpts[1]) == 1:
                                linenm = ".6"
                    t.find("endpage").text = endpage + linenm
                    enct += 1
                    tlist[tid] = 1
            elif ntxt is not None:
                nstart = ntxt.find("startpage").text
                if nstart:
                    if ".1" in nstart or "." not in nstart:
                        # if next text starts at .1, assume this ends .6 of previous page
                        nstart = str(int(float(nstart)) - 1) + ".6"
                    t.find("endpage").text = nstart
                    enct += 1
                    tlist[tid] = 1
            else:
                print "text {0} has no end page and can't find next text".format(tid)
                nofix += 1

                # print "Startpages changed: {0}".format(spct)
                #print "Endpages changed: {0}".format(enct)
                #print "Missing pages unable to change: {0}".format(nofix)
                #print "Total text records changed: {0}".format(len(tlist))
                #print "Texts changed: "
                #knum = 0
                #for k in sorted(tlist.iterkeys(), key=int):
                #  print k.zfill(3),
                #  knum += 1
                #  if knum % 10 == 0:
                #    print ""
                #print ""

    def get_volume(self, n):
        n = int(n)
        if n in self.vols.keys():
            return self.vols[n]
        else:
            return None

    def get_volume_toc(self, n, method='plain'):
        n = int(n)
        voltoc = []
        if n in self.vols.keys():
            vol = self.get_volume(n)
            for tn in vol["texts"]:
                txt = self.get_text(tn)
                if method == 'list':
                    voltoc.append({
                        "key": txt.key,
                        "tnum": txt.tnum,
                        "title": txt.title,
                        "vnum": txt.vnum,
                        "start": txt.startpage,
                        "end": txt.endpage
                    })
                elif method == 'texts':
                    voltoc.append(self.get_text(txt.key))
                else:
                    title = self.tib_to_wylie(txt.title)
                    print txt.key, txt.tnum, title, txt.vnum, txt.startpage, txt.endpage
        else:
            print "There is no volume {0}".format(n)
        if method != 'plain':
            return voltoc

    # Text functions in THL Catalog
    def get_text(self, n, mytype="object"):
        """Returns a text object"""
        if isinstance(n, str):
            n = int(n)
        if n in self.texts.keys():
            if mytype == "element":
                return self.texts[n]
            elif mytype == "string":
                return etree.tostring(self.texts[n], encoding=unicode)
            else:
                return Text.Text(self.texts[n], self)
        else:
            return None

    def get_text_list(self, listtype="tuple", tibformat="unicode"):
        """Get a list of texts in one of three formats: tuples (default), arrays, or dictionaries"""
        out = []
        for t in self.iter_texts():
            out.append(t.getData(listtype, tibformat))
        return out

    def iter_texts(self, ttype="object"):
        txts = self.texts
        for k, txt in txts.iteritems():
            if ttype == "xml":
                yield txt
            else:
                yield Text.Text(txt, self)

    def iter_volumes(self):
        vols = self.vols
        for k, v in vols.iteritems():
            yield v

    @staticmethod
    def tib_to_wylie(txt):
        url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
        q = {'conversion': 'uni2wy', 'plain': 'true', 'input': unicode(txt).encode('utf-8')}
        out = ''
        fh = urlopen(url + urlencode(q))
        for l in fh.readlines():
            out += l
        fh.close()
        return out

    @staticmethod
    def remove_attributes(doc, att, vals):
        for v in vals:
            xp = "/*//*[@" + att + "='" + v + "']"
            els = doc.xpath(xp)
            if len(els) > 0:
                el = els[0]
                el.attrib.pop(att)
            else:
                print "Could not find attribute to remove with xpath: {0}".format(xp)

    def renumber_texts(self):
        tnum = 0
        for t in self.iter_texts("xml"):
            tnum += 1
            t.find("key").text = str(tnum)


def set_template_val(doc, xp, val, cmt=""):
    atnm = "id"
    match = search(r'\[@(\w+)=', xp)
    if match:
        atnm = match.group(1)
    els = doc.xpath(xp)
    if len(els) == 0:
        print "Xpath: {0} not found".format(xp)
    else:
        el = els[0]
        #  for sel in el:
        #     list(el).pop()
        if cmt != "":
            c = etree.Comment(cmt)
            c.tail = val
            el.insert(0, c)
        else:
            if isinstance(val, int) or isinstance(val, float):
                val = str(val)
            el.text = val
        el.attrib.pop(atnm)

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
    myurl = '/Users/thangrove/Documents/Project_Data/THL/DegeKT/ProofedVols/test-out/crlftest.txt'
    srcobj = THLSource(myurl)
    srcobj.removecrlf()

    print srcobj.sourcetxt

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
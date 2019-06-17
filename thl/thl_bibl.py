####  THLBibl Class ####
from .thl_base import *

class THLBibl(THLBase):
    """
    THL Bibl: An object for reading in and extracting information from a Tib Text catalog record or Tibbibl
    """
    id=''
    textno= ''
    noinvol = ''
    volnos = []


    def __init__(self, bibl_path, is_xml=True):
        super().__init__(bibl_path, is_xml)
        self.type = 'bibl'
        self.set_info()

    def set_info(self):
        try:
            # Get Cat Info
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection" and @system="sigla"]/text()'
            self.catsig = str(self.root.xpath(xpq)[0])
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/text()'
            self.edname = str(self.root.xpath(xpq)[0])
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/text()'
            self.edsig = str(self.root.xpath(xpq)[0])
        except:
            print("Problem setting catalog and edition info from bibl")

        try:
            # Set text number
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/' + \
                'tibid[@type="text" and @system="number"]/text()'
            self.textno = str(self.root.xpath(xpq)[0])
        except:
            print("Problem getting the text number from bibl")

        try:
            # Set Number in Vol
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/' + \
                  'tibid[@type="volume" and @system="number"]/tibid[@type="text" and @system="number"]/text()'
            self.noinvol = str(self.root.xpath(xpq)[0])
        except:
            print("Problem getting number in vol from bibl")

        try:
            # Set vol numbers
            xpq = '/tibbibl/tibiddecl/tibid[@type="collection"]/tibid[@type="edition"]/tibid[@system="sigla"]/' + \
                'tibid[@type="volume" and @system="number"]/text()'
            res = self.root.xpath(xpq)
            vols = [str(r).strip() for r in res]
            self.volnos = filter(None, vols)
        except:
            print("Problem getting vol numbers from bibl")

    def test(self):
        print("I am {} {}.{}, the {} text in volume {}".format(self.catsig, self.edsig, self.textno, self.noinvol, ', '.join(self.volnos)))

if __name__ == "__main__":
    pth = '/usr/local/projects/thlib-texts/thlib-texts-xml/catalogs/xml/kt/d/0/kt-d-0518-bib.xml'
    mybib = THLBibl(pth)
    mybib.test()

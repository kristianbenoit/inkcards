#! /usr/bin/python2
'''
Copyright (C) 2018 Kristian Benoit, kristian.benoit@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import sys
import re
from StringIO import StringIO
sys.path.append('/usr/share/inkscape/extensions')
import inkex
from inkex import etree, debug, NSS

_card_types = {
    'poker': [
        #'<symbol id="card" viewBox="0 0 2.8333333 3.6666667">'
        '<symbol id="card" viewBox="0 0 %f %f">'
          '<rect id="poker-card" x="-1.25" y="-1.75" width="2.5" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000;stroke-width:0.25;stroke-opacity:1"/>'
          '<line x1="-1.5" y1="-1.75" x2="1.5" y2="-1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1.5" y1="1.75" x2="1.5" y2="1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1.25" y1="-2" x2="-1.25" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="1.25" y1="-2" x2="1.25" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<rect x="-1.25" y="-1.75" width="2.5" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000;stroke-width:0.1;stroke-opacity:1"/>'
        '</symbol>',
        ('2.5in','3.5in')],
    
    'bridge': [
        '<symbol id="card" viewBox="0 0 2.8333333 3.6666667">'
          '<rect id="bridge-card" x="-1.125" y="-1.75" width="2.25" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000000;stroke-width:0.25;stroke-opacity:1"/>'
          '<line x1="-1.375" y1="-1.75" x2="1.375" y2="-1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1.375" y1="1.75" x2="1.375" y2="1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1.125" y1="-2" x2="-1.125" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="1.125" y1="-2" x2="1.125" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<rect x="-1.125" y="-1.75" width="2.25" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000;stroke-width:0.1;stroke-opacity:1"/>'
        '</symbol>',
        ("2.25in","3.5in")],
    
    'visit-US-card': [
        '<symbol id="card" viewBox="0 0 2.8333333 3.6666667">'
          '<rect id="visit-US-card" x="-1" y="-1.75" width="2" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000000;stroke-width:0.25;stroke-opacity:1"/>'
          '<line x1="-1.25" y1="-1.75" x2="1.25" y2="-1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1.25" y1="1.75" x2="1.25" y2="1.75" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="-1" y1="-2" x2="-1" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<line x1="1" y1="-2" x2="1" y2="2" style="stroke:#888;stroke-width:0.01;stroke-opacity:1"/>'
          '<rect x="-1" y="-1.75" width="2" height="3.5" fill="none" rx="0.25" ry="0.25" style="stroke:#000;stroke-width:0.1;stroke-opacity:1"/>'
        '</symbol>',
        ("2in","3.5in")]
}

def available_card_types():
    return _card_types.keys()

class cards_xml(object):
    def __init__(self, ex):
        self.ex = ex
        self.document = ex.document

    @property
    def available_card_types(self):
        return available_card_types()

    def get_card(self, card_type):
        page_w, page_h = [ float(x) for x in self.document.getroot().attrib['viewBox'].split(" ")[2:]]
        #svg_w = page_w / self.ex.unittouu(self.document.getroot().attrib['width'])
        #svg_h = page_h / self.ex.unittouu(self.document.getroot().attrib['height'])
        #nb_card_wide = int(svg_w/(_card_types[card_type][1][0]))
        #nb_card_high = int(svg_h/(_card_types[card_type][1][1]))
        card_w = self.ex.unittouu(_card_types[card_type][1][0])
        card_h = self.ex.unittouu(_card_types[card_type][1][1])
        nb_card_wide = int(page_w/card_w)
        nb_card_high = int(page_h/card_h)

        card_xml_str = _card_types[card_type][0] % [ page_w/nb_card_wide, page_h/nb_card_high ]
        return etree.fromstring(card_xml_str)

    def add_card_type(self, cardType):
        defs = etree.Element('defs')
        defs.append(self.get_card(cardType))
        self.document.getroot().append(defs)
    
class SheetOfCards(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option(
            "-s", "--sheetformat", type="string", default="['8.5in', '11in']", #defaul="default"
            action="store", dest="sheetformat",
            help="Type of sheet. e.g. ['8.5in', '11in'] for letter")

        self.OptionParser.add_option(
            "-c", "--cardformat", type="string", default="poker",
            action="store", dest="cardformat",
            help="Type of cards to tile. e.g. (%s)" % ", ".join(cards_xml(self).available_card_types))

        self.OptionParser.add_option(
            '--orientation', type='string', default='vert',
            action='store', dest='orientation',
            help='Orientation of the cards to tile. (vert|horiz)')

        self.OptionParser.add_option(
            '--bleed', type='float', default='3.0',
            action='store', dest='bleed',
            help='Size of the bleed in mm.')

    #def parse(self, filename=None):
        #pass
        # Add card layout into the SVG first.
        #inkex.Effect.parse(self, filename)
        #self.svg = self.document.getroot()
        #self.cardformat = self.evalFormat(self.options.cardformat)
        #self.sheetformat = self.evalFormat(self.options.sheetformat)

    def effect(self):
        print(self)
        card = cards_xml(self).add_card_type('poker')
        

if __name__ == "__main__":
    sheet = SheetOfCards()
    sheet.affect()
    sys.exit(errorCode)

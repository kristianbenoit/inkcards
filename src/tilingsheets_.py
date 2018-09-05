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
sys.path.append('/usr/share/inkscape/extensions')
import inkex
from inkex import etree, debug

# Set the error status if called then return the value.
errorCode = 0
def errormsg(msg, error=0):
    global errorCode
    errorCode = error
    inkex.errormsg(msg)

class SheetOfCards(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option(
            "-s", "--sheetformat", type="string", default="['8.5in', '11in']",
            action="store", dest="sheetformat",
            help="Type of sheet. e.g. ['8.5in', '11in'] for letter")

        self.OptionParser.add_option(
            "-c", "--cardformat", type="string", default="['3.5in', '2.5in']",
            action="store", dest="cardformat",
            help="Type of cards to tyle. e.g. ['2.5in', '3.5in'] for poker")

        self.OptionParser.add_option(
            '--orientation', type='string', default='vert',
            action='store', dest='orientation',
            help='Orientation of the cards to tile. (vert|horiz)')

        self.OptionParser.add_option(
            '--bleed', type='float', default='3.0',
            action='store', dest='bleed',
            help='Size of the bleed in mm.')

    def parse(self, filename=None):
        inkex.Effect.parse(self, filename)
        self.svg = self.document.getroot()
        self.cardformat = self.evalFormat(self.options.cardformat)
        self.sheetformat = self.evalFormat(self.options.sheetformat)

    def evalFormat(self, value, userunit=False):
        #r = re.compile('([\d\.]+)(\w+)')
        arr = eval(value)
        return [int(self.unittouu(v)) for v in arr]

    def getLayers(self):
        return self.document.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=inkex.NSS)

    def getLayersLabel(self, start_label): # UnNumbered label
        label_attrib = '{{{inkscape}}}label'.format(**inkex.NSS)
        all_layers = [l.attrib[label_attrib] for l in self.getLayers()]
        layersLabel = [l for l in all_layers if l.startswith(start_label)]
        return layersLabel

    def newLayer(self, parent, label='layer', idx=None):
        r = re.compile(r'[^\d](\d+)$')
        nums = [int(r.match(l)) for l in self.getLayersLabel(label)]
        if len(nums) is 0:
            label += '1'
        else:
            label += str(max(nums)+1)
        #layerlabels = [n.attrib['{{{inkscape}}}label'.format(**inkex.NSS)] for n in layers if n.attrib['{{{inkscape}}}label'.format(**inkex.NSS)].startswith("back")]

        layer = etree.Element('g')
        layer.set('id', self.uniqueId('layer'))
        layer.set(inkex.addNS('label', u'inkscape'), label)
        layer.set(inkex.addNS('groupmode', u'inkscape'), 'layer')
        if type(idx) is not int:
            parent.append(layer)
        else:
            parent.insert(idx, layer)
        return layer

    def create_guideline(self, orientation, x,y):
        namedview = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        guide = inkex.etree.SubElement(namedview, inkex.addNS('guide', 'sodipodi'))
        guide.set("orientation", orientation)
        guide.set("position", str(x)+","+str(y))
        return guide

    def create_horizontal_guideline(self, position):
        return self.create_guideline("0,1", 0, position)

    def create_vertical_guideline(self, position):
        return self.create_guideline("1,0", position, 0)

    def effect(self):
        # Calculate the number of cards per layer/sheet
        if self.options.orientation == "horiz":
            nb_cards_vert = int(self.sheetformat[0] / self.cardformat[0])
            nb_cards_horiz = int(self.sheetformat[1] / self.cardformat[1])
        else:
            nb_cards_vert = int(self.sheetformat[0] / self.cardformat[1])
            nb_cards_horiz = int(self.sheetformat[1] / self.cardformat[0])

        def getlendata(string):
            float_re = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
            re_len = re.compile(r"(%s)(%s)$" % (float_re,
                                '|'.join(inkex.Effect._Effect__uuconv.keys())))
            return re_len.match(string).groups()
            
        def add_guidelines():
            cardUnit = getlendata(eval(self.options.cardformat)[0])[1]
            sheetUnit = getlendata(eval(self.options.sheetformat)[0])[1]
            sh_width, sh_height = eval(self.options.sheetformat)
            self.svg.set("width", sh_width)
            self.svg.set("height", sh_height)
            sh_width = float(getlendata(sh_width)[0]) * \
                    self._Effect__uuconv[sheetUnit] / self._Effect__uuconv['mm']
            sh_height = float(getlendata(sh_height)[0]) * \
                    self._Effect__uuconv[sheetUnit] / self._Effect__uuconv['mm']
            self.svg.set("viewBox", "0 0 %f %f" % (sh_width, sh_height))
            vert_boundaries = [x * sh_width / float(nb_cards_vert)
                               for x in xrange(nb_cards_vert+1)]
            horiz_boundaries = [x * sh_height / float(nb_cards_horiz)
                                for x in xrange(nb_cards_horiz+1)]
            guides = []
            for g in vert_boundaries:
                guides.append(self.create_vertical_guideline(g))
            for g in horiz_boundaries:
                guides.append(self.create_horizontal_guideline(g))

            for g in guides:
                g.set('{{{inkscape}}}color'.format(**inkex.NSS), 'rgb(64,64,64)')

####
        def draw_card_bleed((cardw, cardh), bleed, name, parent):
            style = {'stroke': 'none',
                     'fill':str(style.l_th),
                     'fill-opacity': '1'}

            line_attribs = {'style' : simplestyle.formatStyle(line_style),
                            inkex.addNS('label','inkscape') : name,
                            'd' : 'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}

            line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

        def draw_layout(layer):
            #draw_card_bleed((self.sheetformat
            nb_cards_vert = int(self.sheetformat[0] / self.cardformat[0])
            pass
            
####


        layer = self.newLayer(self.svg, 'Card Layout')
        draw_layout(layer)
        add_guidelines()

if __name__ == "__main__":
    sheet = SheetOfCards()
    sheet.affect()
    sys.exit(errorCode)

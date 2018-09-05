#!/usr/bin/python2
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
import os
from shutil import copyfile
from ConfigParser import ConfigParser
import argparse
import re

sys.path.append('/usr/share/inkscape/extensions')
# TODO: If running on windows append inkscape extensions path.
import inkex
from lxml import etree


# Set the error to true if called then pass it back to inkex.
errorCode = 0
def errormsg(msg, error=0):
    errorCode = error
    inkex.errormsg(msg)

def unsignedLong(signedLongString):
    longColor = long(signedLongString)
    if longColor < 0:
        longColor = longColor & 0xFFFFFFFF
    return longColor

class CardTiling(inkex.Effect, object):
    __metaclass__ = type
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option(
            '--extension', type='inkbool', default=False,
            action='store', dest='extension',
            help= "'True' if run as an extension from inkscape")

        self.OptionParser.add_option(
            '--conf', type='string', default='~/Documents/inkcards.conf',
            action='store', dest='file',
            help='Where to read the layers configured per card (using the '\
                 'inkcards extension).')

        self.OptionParser.add_option(
            '--cardsSVG', type='string', default=None,
            action='store', dest='cardsSVG',
            help='The name of the SVG file built with inkcards that contain '\
                 'the description of all card layers.')

        self.OptionParser.add_option(
            '--tab', type='string', default="stuff",
            action='store', dest='tab')

        self.OptionParser.add_option(
            '--page', type='int', default=1,
            action='store', dest='page',
            help='The number of the page to render')

        self.OptionParser.add_option(
            '--ncwide', type='int', default=2,
            action='store', dest='nbcwide',
            help='The number of cards wide.')

        self.OptionParser.add_option(
            '--nchigh', type='int', default=4,
            action='store', dest='nbchigh',
            help='The number of cards high.')

        self.OptionParser.add_option(
            '--hex', type='inkbool', default=False,
            action='store', dest='hex',
            help='These tiles are hex.')

        self.OptionParser.add_option(
            '--side', type='string', default='long_edge',
            action='store', dest='sidingLayout',
            help='Two side layout, value should be one of: (single, long_edge, short_edge, folded)')

        self.OptionParser.add_option(
            '--orientation', type='string', default='vert',
            action='store', dest='orientation',
            help='Orientation of the cards to tile.')

        self.OptionParser.add_option(
            '--bgcolor', type='string', default='4294967295',
            action='store', dest='bgcolor',
            help='The number of cards high.')

        self.getoptions()
        #self.confFile = os.path.expanduser(self.options.file)
        self.config = ConfigParser()
        self.outfile = None

    def getLayer(self, layername):
        return self.document.xpath("//svg:g[@inkscape:groupmode='layer'][@inkscape:label='" + layername + "']", namespaces=inkex.NSS)[0]

    def output(self):
        """Serialize document into XML on stdout or in a file if outfile is
        defined an inkscape extension.
        
        This override inkex.Effect.output method."""

        if (self.outfile):
            self.document.write(self.outfile)
        else:
            super(CardTiling, self).output()

    #SVG element generation routine
    def draw_rect(self, parent, (w,h), (x,y), **style):
        style = ';'.join("%s:%s" % (key, value) for (key, value) in style.items())
        attribs = {
            'height'    : str(h),
            'width'     : str(w),
            'x'         : str(x),
            'y'         : str(y),
            'style'     : style
        }
        inkex.etree.SubElement(parent, inkex.addNS('rect','svg'), attribs )

    def get_ind1(self, rootEl, nodeType, NS=None):
        idx = [i for i, item in
               enumerate(rootEl) if inkex.addNS(nodeType, NS) == item.tag]
        return idx[0]
    
    def set_bleed(self, svg):
        """"Create a backgroung layer with a rect colored according to the arg
            bgcolor."""
        try:
            bg = self.getLayer('background')
            for el in bg:
                if el.tag == inkex.addNS('rect', u'svg'):
                    bg.remove(el)

        except IndexError:
            bg = etree.Element('g')
            bg.set('id', self.uniqueId('layer'))
            bg.set(inkex.addNS('label', u'inkscape'), 'background')
            bg.set(inkex.addNS('groupmode', u'inkscape'), 'layer')

        style={'fill-opacity':'1'}
        if self.options.bgcolor.startswith('#'):
            style['fill'] = self.options.bgcolor
        else:
            colorSTR = "%8.8x" % int(unsignedLong(self.options.bgcolor))
            style['fill'] = "#%s" % colorSTR[0:6]
            style['fill-opacity'] = int(colorSTR[6:8], 16)/255.0

        self.draw_rect(bg, ('100%', '100%'), (0, 0), **style)

        svg.insert(self.get_ind1(svg, 'g', u'svg'), bg)

    def generate_page(self, svg, pageNB):

        def get_cards_layer(root):
            try:
                layer = self.getLayer('cards')
            except IndexError:
                layer = etree.Element('g')
                layer.set('id', self.uniqueId('layer'))
                layer.set(inkex.addNS('label', u'inkscape'), 'Cards page %s' % self.options.page)
                layer.set(inkex.addNS('groupmode', u'inkscape'), 'layer')
                root.insert(self.get_ind1(root, 'g', u'svg'), layer)
            return layer

        #Define the space for a card
        pagew = self.unittouu(svg.get('width'))
        pageh = self.unittouu(svg.get('height'))
        size = [pagew/self.options.nbcwide, pageh/self.options.nbchigh]
        center = [x/2 for x in size]
        origin = [center[0] - 64.5/2, center[1] - 88.9/2] #TODO: Get the card size by options
        img = etree.Element('image', **{
            inkex.addNS('href', u'xlink'): 'forest-front.svg',
            "x": "38.1",
            "y": "0",
            "width" : str(size[1]),
            "height" : str(size[0]),
            "transform" : "rotate(-90, " + str(center[0]) + ", " + str(center[0]) + ")"
        })
        self.draw_rect(svg, (1,1), tuple(center), fill='#888888')
        self.draw_rect(svg, (1,1), tuple(origin), fill='#888888')
        cards_layer = get_cards_layer(svg)
        cards_layer.append(img)
        #img = etree.Element('rect', **{
        #    inkex.addNS('href', u'xlink'): 'forest-front.svg',
        #    "x": "38.1",
        #    "y": "0",
        #    "width" : str(size[1]),
        #    "height" : str(size[0]),
        #    "transform" : "rotate(-90, " + str(center[0]) + ", " + str(center[0]) + ")"
        #})
        #cards_layer.append(img)


        #Set CuttingLayout color as opposite of background color

        #<image x="0" y="0" width="64.5" height="88.9" xlink:href="forest-front.svg" transform="rotate(90,44.45,44.45)"/>

        #self.getDocumentHeight()
        #self.getDocumentWidth()
        #layer_width = inkex.unittouu(svg.get('width'))
        #layer_height = inkex.unittouu(svg.get('height'))

        return

        # unit convertion Example
        #self.getDocumentHeight()
        #self.getDocumentWidth()
        #layer_width = inkex.unittouu(svg.get('width'))
        #layer_height = inkex.unittouu(svg.get('height'))
        #self.getposinlayer()

    def effect(self):
        svg = self.document.getroot()
        self.set_bleed(svg)
        self.generate_page(svg, self.options.page)

if __name__ == "__main__":
    pages = CardTiling()
    pages.affect()
    # Return the error only if not called from inkscape as inkex is not
    # expected to report errors.
    if not pages.options.extension:
        sys.exit(errorCode)

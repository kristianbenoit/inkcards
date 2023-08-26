#! /usr/bin/python3
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
import copy

sys.path.append('/usr/share/inkscape/extensions')
import inkex
from inkex import etree, debug, NSS

class Card(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.arg_parser.add_argument(
            '--extension', type=inkex.Boolean, default=False,
            action='store', dest='extension',
            help="'True' if run as an extension from inkscape")

        self.arg_parser.add_argument(
            "-c", "--cardformat", default="['2.5in', '3.5in']",
            action="store", dest="cardformat",
            help="Size of the document to create. e.g. ['2.5in', '3.5in'] for Poker")

        self.arg_parser.add_argument(
            "-r", "--rotate", type=inkex.Boolean, default=False,
            action="store", dest="rotate",
            help="Rotate the card 90 ?")

    def effect(self):
        cardformat = eval(self.options.cardformat)

        sizeInUU = tuple(map(self.svg.unittouu, cardformat))
        if self.options.rotate:
            viewbox = '0 0 {1} {0}'.format(*sizeInUU)
            cardformat[0], cardformat[1] = cardformat[1], cardformat[0]
        else:
            viewbox = '0 0 {0} {1}'.format(*sizeInUU)

        svg = self.document.getroot()
        svg.set('width', cardformat[0])
        svg.set('height', cardformat[1])
        svg.set('viewBox', viewbox)

if __name__ == "__main__":
    card = Card()
    card.run()

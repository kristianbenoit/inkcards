#!/usr/bin/python3
'''
Copyright (C) 2018-2023 Kristian Benoit, kristian.benoit@gmail.com

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
# inkex doc:
# https://inkscape.gitlab.io/extensions/documentation/inkex.html
# https://wiki.inkscape.org/wiki/index.php/Updating_your_Extension_for_1.0
# https://wiki.inkscape.org/wiki/index.php/Release_notes/1.0 
# https://gitlab.com/inkscape/extensions/-/tree/master/inkex
# http://inkscape.gitlab.io/inkscape/doxygen-extensions/namespaceinkex.html

import sys
import re
import copy

sys.path.append('/usr/share/inkscape/extensions')
import inkex
from inkex import NSS
from inkex.utils import debug
from inkex.elements import addNS
from lxml import etree
errorCode=0

def registerNS(nsmap):
    """Should be moved to inkex and automatically called at the object creation
    with the namespaces defined in using_namespaces:
    class makeSomeChanges(inkex.effect):
        using_namespaces={"someNamespace": "http://domain.com/someNamespce"}"""
    for nsK, NS in nsmap.items():
        inkex.NSS[nsK] = NS
        etree.register_namespace(nsK, NS)
    #inkex.SSN = dict((b, a) for (a, b) in inkex.NSS.items())


class inkcardsError(Exception):
    def __init__(self, msg):
        super(inkcardsError, self).__init__(msg)

    def reportToInkex(self):
        inkex.errormsg(self.args[0])


class inkcards(inkex.Effect):
    """Inherit from this to create an inkcards aware extension"""
    def __init__(self):
        """Global arguments for all inkcards extensions"""
        inkex.Effect.__init__(self)

        self.arg_parser.add_argument(
            '--extension', type=inkex.Boolean, default=False, dest='extension',
            help="'True' if run as an extension from inkscape")

    @property
    def activeLayersID(self):
        return self.svg.xpath('//svg:g[@inkscape:groupmode="layer" and (not(@style) or @style="display:inline")]/@id')

    @property
    def layers(self):
        return self.svg.xpath('//svg:g[@inkscape:groupmode="layer"]'%(groupmode))

    def effect(self):
        registerNS({u"inkcards": u"http://boardgamegeek.com/inkscape/extension/inkcards"})

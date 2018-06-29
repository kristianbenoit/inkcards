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
import ConfigParser

sys.path.append('/usr/share/inkscape/extensions')
import inkex

class extention(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--tab',
                                     action='store',
                                     type='string', dest='tab')
        self.OptionParser.add_option('--file',
                                     action='store',
                                     type='string', dest='file', default='/tmp/inkcards.conf',
                                     help='Where to read the layers configured per card.')
        self.OptionParser.add_option('--cardNo',
                                     action='store',
                                     type='int', dest='cardNo', default=0,
                                     help='The card number to activate the layers, hide the others.')
        self.OptionParser.add_option('--side',
                                     action='store',
                                     type='string', dest='side', default='front', # 1 is front and 2 is rear
                                     help='side of the card (front/rear)')
        self.getoptions()

    def effect(self):
        config = ConfigParser.ConfigParser()
        allLayers = self.document.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=inkex.NSS)
        self.options.tab = self.options.tab.strip('"')

        if self.options.tab == 'conf':
            if os.path.isfile(self.options.file):
                inkex.errormsg("File (%s) already exist, remove it first." % (self.options.file))
                return

            configFile = file(self.options.file, 'w')
            configFile.write(
                "# This is a ini style config file, where you define all layers that compose\n"
                "# a card (by sides).\n#\n"
                "# Like so:\n\n")

            config.add_section('card 1')
            layerStr=""
            for l in allLayers:
                layerStr += l.attrib['{' + inkex.NSS["inkscape"] + '}label'] + ", " 

            config.set('card 1', "front", layerStr[:-2])
            config.set('card 1', "rear", layerStr[:-2])

            config.write(configFile)

        elif self.options.tab == "show":
            config.read(self.options.file)

            cardName = "card " + str(self.options.cardNo)
            if cardName not in config.sections():
                inkex.errormsg("No such section (%s), in %s" % (cardName, self.options.file))
                return

            visibleLayers = map(str.strip, config.get(cardName, self.options.side).split(","))
            for l in allLayers:
                # Switch on the visibitity of layers specified in the config file
                if l.attrib['{' + inkex.NSS["inkscape"] + '}label'] in visibleLayers:
                    l.set("style", "display:inline")
                else:
                    # Turn off the visibility of all other layers
                    l.set("style", "display:none")
        else:
            inkex.errormsg(str(os.environ["PWD"]))
            inkex.errormsg("Unknown tab \"%s\"" % self.options.tab)

if __name__ == "__main__":
    e = extention()
    e.affect()

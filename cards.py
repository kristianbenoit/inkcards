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

sys.path.append('/usr/share/inkscape/extensions')
import inkex
from lxml import etree

# Set the error to true if called then pass it back to inkex.
error = 0
def errormsg(msg):
    error=1
    inkex.errormsg(msg)

class extension(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--tab',
                                     action='store',
                                     type='string', dest='tab')
        self.OptionParser.add_option('--file',
                                     action='store',
                                     type='string', dest='file', default='~/Documents/inkcards.conf',
                                     help='Where to read the layers configured per card.')
        self.OptionParser.add_option('--cardNo',
                                     action='store',
                                     type='int', dest='cardNo', default=0,
                                     help='The card number to activate the layers, hide the others.')
        self.OptionParser.add_option('--side',
                                     action='store',
                                     type='string', dest='side', default='front', # 1 is front and 2 is rear
                                     help='side of the card (front/rear)')
        self.OptionParser.add_option('--svgout',
                                     action='store',
                                     type='string', dest='svgout', default=None,
                                     help='A sub argument of --tab=show. Save the card into ... Use to differentiate if called from inkscape or not')
        self.getoptions()
        self.options.file = os.path.expanduser(self.options.file)

        if self.options.svgout:
            self.outfile=file(self.options.svgout, 'w')
        else:
            self.outfile=sys.stdout

    def output(self):
        """Serialize document into XML on stdout or outfile if the svgout option was passed"""
        result = etree.tostring(self.document)
        self.document.write(self.outfile)

    def __write_conf(self, config, allLayers):
        """Write a sample conf file with all layers in a single card."""
        if os.path.isfile(self.options.file):
            errormsg("File (%s) already exist, remove it first." % (self.options.file))
            return

        configFile = file(self.options.file, 'w')
        configFile.write(
            "# This is a ini style config file, where you define all layers that compose\n"
            "# a card (by side).\n"
            "#\n"
            "# Like so:\n\n")

        config.set(None, "SVG_src","card_layers.svg")
        config.set(None, "dest","output.pdf")

        config.add_section('card 1')
        layers=[]
        for l in allLayers:
            layers.append(l.attrib['{' + inkex.NSS["inkscape"] + '}label'])

        config.set("card 1", "front", layers)
        config.set("card 1", "rear", layers)

        config.write(configFile)

    
    def __create_card(self, config, allLayers):
        """Activate only the layers for this card, described in inkcards.conf. To support being an inkscape extension, the cards are named: "card i", where i is a number."""
        config.read(self.options.file)
        cardName = "card " + str(self.options.cardNo)
        if cardName not in config.sections():
            errormsg("No such section (%s), in %s" % (cardName, self.options.file))
            errormsg("PWD is %s" % (os.getcwd()))
            return

        visibleLayers = config.get(cardName, self.options.side)
        visibleLayers = eval(visibleLayers)

        for l in allLayers:
            # Switch on the visibitity of layers specified in the config file
            if l.attrib['{' + inkex.NSS["inkscape"] + '}label'] in visibleLayers:
                l.set("style", "display:inline")
            else:
                # Turn off the visibility of all other layers
                l.set("style", "display:none")

    def effect(self):
        config = ConfigParser()
        allLayers = self.document.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=inkex.NSS)
        self.options.tab = self.options.tab.strip('"')

        if self.options.tab == 'conf':
            self.__write_conf(config, allLayers)
        elif self.options.tab == "show":
            self.__create_card(config, allLayers)
        else:
            errormsg("Unknown tab \"%s\"" % self.options.tab)

if __name__ == "__main__":
    e = extension()
    e.affect()
    # Return the error only if not called from inkscape as inkex do not seem to report errors?
    if e.options.svgout:
        sys.exit(error)

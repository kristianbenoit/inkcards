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

class Card(inkex.Effect, object):
    __metaclass__ = type
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--extension',
                                     action='store',
                                     type='inkbool', dest='extension', default='false',
                                     help="'true' if run as an extension from inkscape")

        self.OptionParser.add_option('--gen-conf',
                                     action='store_true',
                                     dest='genconf', default=False,
                                     help='Generate a config file with a single card with all layers. Useful to copy/paste them.')

        self.OptionParser.add_option('--__genconf',
                                     action='store',
                                     type='inkbool', dest='__genconf', default='false',
                                     help='Same as --gen-conf, but for inkscape specific use. (not a flag)')

        self.OptionParser.add_option('--conf',
                                     action='store',
                                     type='string', dest='file', default='~/Documents/inkcards.conf',
                                     help="Where to read the layers configured per card. If --gen-conf is passed, that's the file the config will be written to.")

        self.OptionParser.add_option('--card',
                                     action='store',
                                     type='string', dest='cardName', default=None,
                                     help='The card name from which you want to activate the layers, hide all other layers.')

        self.OptionParser.add_option('-f', '--front',
                                     action='store_true',
                                     dest='showFront', default=True,
                                     help='show side front')

        self.OptionParser.add_option('-r', '--rear',
                                     action='store_false',
                                     dest='showFront',
                                     help='show side rear')

        self.getoptions()
        self.confFile = os.path.expanduser(self.options.file)
        self.outfile=None

    def output(self):
        """Serialize document into XML on stdout or in a file named <card-name>-<card-side>.svg if not running as an inkscape extension. This override inkex.Effect.output method."""
        if (self.outfile):
            self.document.write(self.outfile)
        else:
            super(Card, self).output()

    def _write_conf(self, config, allLayers):
        """Write a sample conf file with all layers in a single card."""
        if os.path.isfile(self.confFile):
            errormsg(_("File (%s) already exist, remove it first.") % (self.options.file))
            return

        configFile = file(self.confFile, 'w')
        configFile.write(_(
            "# This is a ini style config file, where you define all layers that compose\n"
            "# a card (by side).\n"
            "#\n"
            "# Like so:\n\n"))

        #config.set(None, "SVG_src","card_layers.svg")
        #config.set(None, "dest","output.pdf")

        layers=[]
        for l in allLayers:
            layers.append(l.attrib['{' + inkex.NSS["inkscape"] + '}label'])

        config.add_section('card 1')
        config.set("card 1", "front", layers)
        config.set("card 1", "rear", layers)

        config.write(configFile)

    def _create_card(self, config, allLayers):
        """Activate only the layers for this card, described in inkcards.conf. To support being an inkscape extension, the cards are named: "card i", where i is a number."""
        if not os.path.isfile(self.confFile):
            errormsg(_("File (%s) does not exist. You should generate the conf file first.") % (self.options.file))
            return

        config.read(self.confFile)
        self.getposinlayer()
        currentLayerName = self.current_layer.attrib['{' + inkex.NSS["inkscape"] + '}label']

        if self.options.cardName:
            cardName = self.options.cardName
            if cardName not in config.sections():
                errormsg(_("No such section (%s), in %s") % (cardName, self.confFile))
                return
            side = 'front' if self.options.showFront else 'rear'
        else:
            if not self.options.extension:
                errormsg(_("You should choose a cardname to create when you run the app outside inkscape. Choosing the card using the last layer selected within inkscape."))
            found = False
            for cardName in config.sections():
                if currentLayerName in config.get(cardName, 'front'):
                    side = 'front'
                    found = True
                    break
                elif currentLayerName in config.get(cardName, 'rear'):
                    side = 'rear'
                    found = True
                    break
            if not found:
                errormsg(_("Layer %s (the current layer) is not found in any cards. Please select a layer that is defined and (ideally) unique to the card/side you want to show.") % (currentLayerName))
                return

        if not self.options.extension:
            self.outfile = file(cardName + '-' + side + '.svg', 'w')

        visibleLayers = config.get(cardName, side)
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

        if self.options.genconf:
            self._write_conf(config, allLayers)
        else:
            self._create_card(config, allLayers)

if __name__ == "__main__":
    card = Card()
    card.affect()
    # Return the error only if not called from inkscape as inkex is not expected to report errors.
    if not card.options.extension:
        sys.exit(error)
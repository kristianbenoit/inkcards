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
import inkex
import os
from shutil import copyfile
import ConfigParser
#from lxml import etree

class extention(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--tab',
                                     action='store',
                                     type='string', dest='tab')
        self.OptionParser.add_option('--file',
                                     action='store',
                                     type='string', dest='file', default='/tmp/inkcards.conf',
                                     help='Where to read the layers configured per page.')
        self.OptionParser.add_option('--pageNo',
                                     action='store',
                                     type='int', dest='page', default=0,
                                     help='The page number to activate the layers, hide the others.')
        self.getoptions()

    def pageParams(self):
        line = linecache.getline(self.options.file, self.options.page)
        return line.split()

    def effect(self):
        configFile = self.options.file
        config = ConfigParser.ConfigParser()
        config.read(configFile)

        if self.options.tab is "exportAll":
            inkex.errormsg("export all pages is not yet implemented.\nself.__dict__=" + str(self.__dict__))
        else:
            svg_filename = self.args[-1]
            self.parse(svg_filename)
            allLayers = self.document.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=inkex.NSS)
            for l in allLayers:
                # Turn off the visibility of all layer
                l.set("style", "display:none")

                # Switch on the visibitity of layers specified in the config file
                pageName = "page " + str(self.options.page)
                visibleLayers = map(str.strip, config.get(pageName, "Layers").split(","))
                if l.attrib['{' + inkex.NSS["inkscape"] + '}label'] in visibleLayers:
                    l.set("style", "display:inline")

                #inkex.errormsg("Put debug info here.")


if __name__ == "__main__":
    e = extention()
    e.affect()

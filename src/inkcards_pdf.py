#!/usr/bin/python3
'''
Copyright (C) 2023 Kristian Benoit, kristian.benoit@gmail.com

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

sys.path.append('/usr/share/inkscape/extensions')
import inkex

# See Jessyink_export

#class Inkscape_PDF(inkex.Effect):
class Inkscape_PDF(inkex.OutputExtension):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument(
            '--page_layer_name', type=str, default='Layer', dest='page_layer_name',
            help="The base name of layers used for pages. Exporting each one (and it's sub layers) to a PDF and unite them.")

    @property
    def allPages(self):
        return self.svg.xpath("//svg:g[@inkscape:groupmode='layer' and starts-with(@inkcape:label,'%s']" % self.options.page_layer_name)

    #def effect(self):
    #    for page in allPages:
    #        #set the page and export it.

    #    sys.exit() #To prevent from any change.

    def save(self, stream):
        #save all pages layer to file$i.pdf
        #and unite them with `pdfunite [file*.pdf] result.pdf`
        pass


if __name__ == "__main__":
    conv = Inkscape_PDF()
    conv.run()

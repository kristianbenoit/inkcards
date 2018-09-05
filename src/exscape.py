#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
A module act as Inkscape to help extensions

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
import os
import re
import sys
from lxml import etree

sys.path.append('/usr/share/inkscape/extensions')
# TODO: If running on windows append inkscape extensions path.
import inkex
from inkex import debug

# A class to use inkex as an external tool.
class _inkex (inkex.Effect):

# These are class to draw ...

class Text:
    """<svg:text ...>"""

class Rect:
    """<svg:rect ...>"""

class Layer:
    """<svg:g inkscape:label="Layer 1" ...>"""

class Path:
    """<svg:path ...>"""

# End of drawing tools

class Exscape(object):
    """ This is a higher level replacement of inkex, where inkex Effect is used
        as an external tool. You should overload this class instead of
        inkex.Effect."""

    def __init__ (self, *argc, **argv):
        pass

if __name__ == "__main__":
    inkex.errormsg("This is a super extension, just like inkex (using inkex) your extenstion could/should use this.")

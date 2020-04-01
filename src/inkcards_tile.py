#! /usr/bin/python
# vim: set fileencoding=utf-8
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
import math
from enum import Enum, unique

sys.path.append('/usr/share/inkscape/extensions')
import inkex
from inkex import etree, debug, NSS, addNS

icNS="http://boardgamegeek.com/inkscape/extension/inkcards"

@unique
class Layout(Enum):
    plain = 0
    book1P = 1
    book2P = 2

class inkcardsError(Exception):
    def __init__(self, msg):
        super(inkcardsError, self).__init__(msg)

    def reportToInkex(self):
        inkex.errormsg(self.message)

class struct(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Tile(inkex.Effect):
    """First the __init__ which contain The declaration for all command line
    arguments. Then the Helpers, a lot of them should be moved to a super class.
    Then last part contain's the tiling style definitions, which structure the
    layout to tile the cards in different ways, according to the options.
    """
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option(
            '--function', type='string',
            action="store", dest='function',
            help="Ignored") 

        self.OptionParser.add_option(
            '--extension', type='inkbool', default=False,
            action='store', dest='extension',
            help="'True' if run as an extension from inkscape")

        self.OptionParser.add_option(
            '--file', type='string',
            action='store', dest='file',
            help="A path to a file containing the cards.")

        self.OptionParser.add_option(
            '--deckname', type='string',
            action='store', dest='deckname',
            help="Name of the deck you want to tile, if more than one, separate by comma.")

        self.OptionParser.add_option(
            '--orientation', type='string',
            action='store', dest='orientation',
            help="The orientation of the card, portrait, landscape, space efficient, ... could add flip/rotations?")

        self.OptionParser.add_option(
            '--tilestyle', type='string', default='book1p',
            action='store', dest='tilestyle',
            help="Choose a tyling layout type (strait, single page (folded), 2 pages).")

        self.OptionParser.add_option(
            '--vert-brd', type='int', default=0,
            action='store', dest='pageVertBrd',
            help="Reserve this border size on the page top/bottom.")
        
        self.OptionParser.add_option(
            '--horiz-brd', type='int', default=0,
            action='store', dest='pageHorizBrd',
            help="Reserve this border size on the page left/right.")
        
        self.OptionParser.add_option(
            '--cardspacingsize', type='int', default=10,
            action='store', dest='cardspacingsize',
            help="Set a minimal spacing size between cards. It enlarge the space reserved for a card by half this size")

        self.OptionParser.add_option(
            '--nospacing', type='inkbool', default=True,
            action='store', dest='cardspacing',
            help="NOT IMPREMENTED: Cards are tiled next to each other, so a single cut is necessary.")

    # HELPERS

    @property
    def defs(self):
        defs = self.document.xpath('//svg:defs', namespaces=NSS)
        if not defs:
            defs = etree.Element(addNS('defs', 'svg'), attrib={'id':self.uniqueId('defs')}, nsmap=NSS)
            self.document.getroot().insert(2, defs)
        else:
            defs = defs[0]

        return defs
    
    def copyLayers(self, doc):
        gLayer = etree.Element(addNS('g', 'svg'), attrib={
                'id':                           self.uniqueId('layer'),
                addNS('groupmode', 'inkscape'): 'layer',
                addNS('label', 'inkscape'):     'inkcards Layers'},
            nsmap=NSS)
        self.defs.append(gLayer)

        layers = doc.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=NSS)

        for layer in layers:
	    try:
	    	layer.attrib.pop('style')
	    except KeyError:
		pass
            gLayer.append(layer)
	
        return layers

    def copyCards(self):
        try:
            # This is a hack to be able to use inkex.Effect method with the card document.
            self.cards = inkex.Effect()
            farg = '--file='
            cardFileName = filter(lambda x : x.startswith(farg), sys.argv)[0][len(farg):]

            self.cards.affect(args=[cardFileName], output=False)
        except inkcardsError as e:
            raise inkcardsError("Error while reading the file (%s)\n%s"%(self.options.file, e))

        allLayers = self.copyLayers(self.cards.document)
        allcards = self.cards.document.xpath('//inkcards:card', namespaces=NSS)
        defs = self.defs
        needRear = []
        for nb in range(len(allcards)):
            c = allcards[nb]
            deck_key = addNS('deck', 'inkcards')
            numb_key = addNS('number', 'inkcards')
            attrib = {'id': self.uniqueId('card'), deck_key: c.attrib[deck_key], numb_key: c.attrib[numb_key]}
            cardlayers = c[:]
            card = etree.Element('g', attrib=attrib)
            for l in cardlayers:
                card.append(etree.Element('use', attrib={
                    'id': self.uniqueId('use'),
                    addNS('href', u'xlink'): '#%s'%(l.attrib[addNS('layer', 'inkcards')]),
                    'x': '0',
                    'y': '0',
                }))
            defs.append(card)

            if c.attrib.has_key(addNS("rear", "inkcards")): # Temporarily get the id in the other file.
                card.attrib[addNS("rear", "inkcards")] = c.attrib[addNS("rear", "inkcards")]
                needRear.append(card)

        for card in needRear:
            oldRearID = self.document.xpath('//g[@inkcards:deck="%s" and @inkcards:number="%s"]/@inkcards:rear'%(card.attrib[addNS('deck', 'inkcards')], card.attrib[addNS('number', 'inkcards')]), namespaces=NSS)[0]

            oldRear = self.cards.getElementById(oldRearID)
            deck = oldRear.attrib[addNS('deck', 'inkcards')]
            number = oldRear.attrib[addNS('number', 'inkcards')]
            newRearID = self.document.xpath('//g[@inkcards:deck="%s" and @inkcards:number="%s"]/@id'%(deck, number), namespaces=NSS)[0]

            card.attrib[addNS("rear", "inkcards")] = newRearID

    
    def getCards(self):
        if self.options.deckname:
            decknames = [dn.strip() for dn in self.options.deckname.split(',')]
            decknames = ['@inkcards:deck="%s"'%dn for dn in decknames]
            decknames = ' or '.join(decknames)
            cards = self.document.xpath('//g[(%s) and @inkcards:number]'%decknames, namespaces=NSS)
            if not cards:
                raise inkcardsError("No cards found in the provided deck names:\n%s"%self.options.deckname)
        else:
            cards = self.document.xpath('//g[@inkcards:deck and @inkcards:number]', namespaces=NSS)

        return cards

    @property
    def docSize(self):
        size = map(lambda x: float(x), self.document.getroot().attrib['viewBox'].split())
        size = struct(zip(['X','Y','W','H'], size))
        size.X = size.X + self.uutounit(self.options.pageVertBrd, 'mm')
        size.Y = size.Y + self.uutounit(self.options.pageHorizBrd, 'mm')
        size.W = size.W - self.uutounit(2*self.options.pageVertBrd, 'mm')
        size.H = size.H - self.uutounit(2*self.options.pageHorizBrd, 'mm')
        return size

    @property
    def cardSize(self):
        size = map(lambda x: float(x), self.cards.document.getroot().attrib['viewBox'].split())
        if self.options.orientation == '90' or self.options.orientation == '-90' :
            return struct(zip(['X','Y','H','W'], size))
        else:
            return struct(zip(['X','Y','W','H'], size))

    @staticmethod
    def nbColumns(docSize, tileSize, minCardSpacing = 0):
        return math.trunc(docSize.W/(tileSize.W + minCardSpacing))

    @staticmethod
    def nbRows(docSize, tileSize, minCardSpacing = 0):
        return math.trunc(docSize.H/(tileSize.H + minCardSpacing))

    @staticmethod
    def tileLocations(docSize, tileSize, minCardSpacing = 0):
        nbColumns = Tile.nbColumns(docSize, tileSize, minCardSpacing)
        nbRows = Tile.nbRows(docSize, tileSize, minCardSpacing)
        tileW = docSize.W/nbColumns
        tileH = docSize.H/nbRows
        extraW = (tileW-tileSize.W)/2
        extraH = (tileH-tileSize.H)/2
        offsetW = docSize.X + extraW
        offsetH = docSize.Y + extraH
        return map(lambda t: struct(zip(
                ['X',                           'Y',                           'W',          'H',          'extraW', 'extraH'],
                   (t%nbColumns*tileW + offsetW,   t/nbColumns*tileH + offsetH,   tileSize.W,   tileSize.H,  extraW,   extraH))),
             range(nbRows*nbColumns))

    def nextLayerLabel(self, label):
        Labels = self.document.getroot().xpath('//svg:g[@inkscape:groupmode="layer" and starts-with(@inkscape:label, "%s")]/@inkscape:label'%label, namespaces=NSS)     
        return "%s%d"%(label, max(map(lambda lbl: int(re.search(r'\d+$', lbl).group())+1, Labels))) if Labels else "%s1"%(label)


    def nextPage(self):
        page = etree.Element(addNS('g', 'svg'), attrib={
                'id':                           self.uniqueId('layer'),
                addNS('groupmode', 'inkscape'): 'layer',
                addNS('label', 'inkscape'):     self.nextLayerLabel("Page ")},
            nsmap=NSS)
        self.document.getroot().append(page)
        return page

    def drawCutLines(self, *locations):
        layer = self.document.getroot().xpath('//svg:g[@inkscape:groupmode="layer" and starts-with(@inkscape:label, "Cutmarks")]', namespaces=NSS)     
        if layer:
            layer = layer[0]
        else:
            layer = etree.Element(addNS('g', 'svg'), attrib={
                'id':                           self.uniqueId('layer'),
                addNS('groupmode', 'inkscape'): 'layer',
                addNS('label', 'inkscape'):     "Cut Marks"},
            nsmap=NSS)
            self.document.getroot().append(layer)
        for l in locations:
            cardlayer = etree.Element(addNS('g', 'svg'), attrib={
                    'id':                           self.uniqueId('layer'),
                    addNS('groupmode', 'inkscape'): 'layer',
                    addNS('label', 'inkscape'):     self.nextLayerLabel("Cut Card ")},
            nsmap=NSS)
            layer.append(cardlayer)

            for mark in [(l.X     -l.extraW, l.Y,      l.extraW, -l.extraH),
                         (l.X+l.W +l.extraW, l.Y,     -l.extraW, -l.extraH),
                         (l.X     -l.extraW, l.Y+l.H,  l.extraW,  l.extraH),
                         (l.X+l.W +l.extraW, l.Y+l.H, -l.extraW,  l.extraH)]:
                cardlayer.append(etree.Element(addNS('path', 'svg'), attrib={
                    'id':       self.uniqueId('layer'),
                    'style':    'fill:none;stroke:#000000;stroke-width:0.5px',
                    'd':        'M %f,%f h %f v %f'%mark}, nsmap=NSS))

    def drawFoldLine(self):
        layer = etree.Element(addNS('g', 'svg'), attrib={
            'id':                           self.uniqueId('layer'),
            addNS('groupmode', 'inkscape'): 'layer',
            addNS('label', 'inkscape'):     "Fold Mark"},
        nsmap=NSS)
        self.document.getroot().append(layer)
        halfdoc = self.docSize
        halfdoc.Y = halfdoc.Y + halfdoc.H/2.0
        layer.append(etree.Element(addNS('path', 'svg'), attrib={
            'id':       self.uniqueId('layer'),
            'style':    'fill:none;stroke:#000000;stroke-width:1.0px',
            'd':        'M {X},{Y} h {W}'.format(**halfdoc)}, nsmap=NSS))

    # END HELPERS

    def layoutPlain(self):
        self.copyCards()
        cards = self.getCards()
        orientation = int(self.options.orientation)
        locations = Tile.tileLocations(self.docSize, self.cardSize, self.options.cardspacingsize)

        self.drawCutLines(*locations)

        for cardnb in range(len(cards)):
            cardlocnb = cardnb%len(locations)
            page = self.nextPage() if cardlocnb == 0 else page
            pos = locations[cardlocnb]
            card = cards[cardnb].attrib['id']
            if self.options.orientation == '90':
                rotAxisX = pos.W/2 
                rotAxisY = pos.W/2
            elif self.options.orientation == '-90':
                rotAxisX = pos.H/2 
                rotAxisY = pos.H/2
            else: #(self.options.orientation is '0' or '180')
                rotAxisX = pos.W/2 
                rotAxisY = pos.H/2
            e = etree.Element(addNS("use", "svg"), attrib={
                addNS('href', u'xlink'): '#%s'%(card),
                'x':"0",
                'y':"0",
                'transform':"translate(%f,%f) rotate(%s,%f,%f)"%(pos.X, pos.Y, orientation, rotAxisX, rotAxisY)
            })
            page.append(e)
            cardnb += 1
            if cardnb >= len(cards):
                break

    def layout1P(self):
        self.copyCards()
        cards = self.getCards()
        orientation = int(self.options.orientation)
        top = self.docSize
        bot = self.docSize
        top.H = bot.H = top.H/2
        bot.Y = top.Y + top.H
        topLocations = Tile.tileLocations(top, self.cardSize, self.options.cardspacingsize)
        botLocations = Tile.tileLocations(bot, self.cardSize, self.options.cardspacingsize)

        # Flip (exchange/reverse) bottom locations by column
        nbColumns = Tile.nbColumns(bot, self.cardSize, self.options.cardspacingsize)
        nbRows = Tile.nbRows(bot, self.cardSize, self.options.cardspacingsize)
        for r in range(nbRows/2):
            rs1 = r*nbColumns # rs1 = RowStart1
            rs2 = (nbRows-1-r)*nbColumns # rs2 = RowStart2
            for c in range(nbColumns):
                botLocations[rs1 + c], botLocations[rs2 + c] = botLocations[rs2 + c], botLocations[rs1 + c]

        self.drawCutLines(*(topLocations + botLocations))
        self.drawFoldLine()

        for cardnb in range(len(cards)):
            cardlocnb = cardnb%len(topLocations)
            page = self.nextPage() if cardlocnb == 0 else page
            tpos = topLocations[cardlocnb]
            bpos = botLocations[cardlocnb]
            card = cards[cardnb]
            try:
                rear = card.attrib[addNS('rear', 'inkcards')]
            except KeyError:
                rear = None
            card = card.attrib['id']

            # Tile the front sides in the top half.
            if self.options.orientation == '90':
                rotAxisX = tpos.W/2 
                rotAxisY = tpos.W/2
            elif self.options.orientation == '-90':
                rotAxisX = tpos.H/2 
                rotAxisY = tpos.H/2
            else: # self.options.orientation is '0' or '180'
                rotAxisX = tpos.W/2 
                rotAxisY = tpos.H/2
            e = etree.Element(addNS("use", "svg"), attrib={
                addNS('href', u'xlink'): '#%s'%(card),
                'x':"0",
                'y':"0",
                'transform':"translate(%f,%f) rotate(%s,%f,%f)"%(tpos.X, tpos.Y, orientation, rotAxisX, rotAxisY)
            })
            page.append(e)
            # Tile the cards back in the bottom half
            if rear:
                if orientation == 0:
                    rearOrient = 180
                elif orientation == 180:
                    rearOrient = 0
                else:
                    rearOrient = orientation

                e = etree.Element(addNS("use", "svg"), attrib={
                    addNS('href', u'xlink'): '#%s'%(rear),
                    'x':"0",
                    'y':"0",
                    'transform':"translate(%f,%f) rotate(%s,%f,%f)"%(bpos.X, bpos.Y, rearOrient, rotAxisX, rotAxisY)
                })
                page.append(e)

            cardnb += 1
            if cardnb >= len(cards):
                break

    def layout2P(self):
        raise inkcardsError("Not implemented yet")

    def effect(self):
        try:
            NSS['inkcards'] = icNS
            {   "plain"     : self.layoutPlain,
                "book1p"    : self.layout1P,
                "book2p"    : self.layout2P,
            } [re.match('^"?([^"]*)"?$',self.options.tilestyle).group(1)]()
            #self.clean()
        except inkcardsError as e:
            if self.options.extension:
                e.reportToInkex()
            else:
                raise e


if __name__ == "__main__":
    tile = Tile()
    tile.affect()
    # Return the error only if not called from inkscape as inkex is not expected to report errors.
    if not tile.options.extension:
        sys.exit(errorCode)

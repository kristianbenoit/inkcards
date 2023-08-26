#! /usr/bin/python3
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

from inkcards import *

icNS = "http://boardgamegeek.com/inkscape/extension/inkcards"

class Card(inkcards):
    def __init__(self):
        inkcards.__init__(self)

        self.arg_parser.add_argument(
            "-n", "--deckname", type=str, dest="deckname",
            help="Name of the deck, concatenated with the a sequence number to get the cardID.")

        self.arg_parser.add_argument(
            "-f", "--function", type=str, default="list", dest="function",
            help="Name of function to use on the list of cards. Available "\
                "functions are:\n"\
                "  add          Define a new card.\n"\
                "  list         Show the list of defined card\n"\
                "  remove       Cleanup and remove a card defined to use the currently visible layers\n"\
                "  activate     Activate le layers for a named card.\n"\
                "  changedeck   Move the cards from deckname to newdeck.\n"\
                "  shift        Change the cards order in deckname.\n"\
                "  rear         Create associations of rear and front.\n")

        self.arg_parser.add_argument(
            "--delbynb", type=inkex.Boolean, dest="delbynb",
            help="When removing, remove the card at a specific position.")

        self.arg_parser.add_argument(
            "--cardno", type=int, dest="cardno",
            help="The position of the card to remove (need to \"delbynb\")")

        self.arg_parser.add_argument(
            "--activateid", type=int, dest="activateid",
            help="A name sequence id concatenated to the name to form a unique id.")

        self.arg_parser.add_argument(
            "--destdeck", type=str, dest='destdeck',
            help="Append the cards using displayed layers to a deck")

        self.arg_parser.add_argument(
            "--where", type=str, dest='shift',
            help="Change the position the card at the \"start\" or \"end\" of the deck.")

        self.arg_parser.add_argument(
            "--reardeck", type=str, dest='reardeck',
            help="Choose a deck name for the back")

        self.arg_parser.add_argument(
            "--rearnb", type=int, dest='rearnb',
            help="The position of the card in the rear deck")

        self.arg_parser.add_argument(
            "--shiftpos", type=int, dest='shiftpos',
            help="The new position of the card")

        self.arg_parser.add_argument(
            "--vrepos", type=inkex.Boolean, dest='vRepos',
            help="Be verbose when repositionning")

        self.arg_parser.add_argument(
            "--verbose", type=inkex.Boolean, dest='verbose',
            help="Show the list of resulting cards after execution")

    # HELPERS
    @property
    def activeLayers(self):
        return self.svg.xpath('//svg:g[@inkscape:groupmode="layer" and (not(@style) or @style="display:inline")]/@id')

    @property
    def allLayers(self):
        return self.svg.xpath("//svg:g[@inkscape:groupmode='layer']")

    @staticmethod
    def groupbycat(srcL, getcat):
        res={}
        for e in srcL:
            cat = getcat(e)
            if not cat in res:
                res[cat] = [e]
            else:
                res[cat].append(e)
        return res

    def getLayernamesOfCard(self, card):
        cardLayerIDs = self.svg.xpath('//inkcards:card[@id="%s"]/inkcards:using/@inkcards:layer'%(card.attrib['id']  ))
        allLayers = dict(map(lambda l: (l.attrib['id'], l.attrib[addNS('label','inkscape')]), self.allLayers))
        return [allLayers[l] for l in cardLayerIDs]

    @staticmethod
    def dictmap(keyfct, l):
        return {keyfct(e):e for e in l}

    def getCardsInDeck(self, deckname):
        return self.svg.xpath('//inkcards:card[@inkcards:deck="%s"]'%deckname)

    def nextCardNB(self, deckname):
        cards_nb = self.svg.xpath('//inkcards:card[@inkcards:deck="%s"]/@inkcards:number'%deckname)
        try:
            return str(max(map(int, cards_nb)) + 1)
        except ValueError:
            return '1'

    def getCard(self, deckname, cardnb):
        return self.svg.xpath(
            '//inkcards:card[@inkcards:deck="%s" and @inkcards:number="%d"]'%(deckname, cardnb),
            namespaces=NSS)[0]

    def getCardLayers(self, deckname, cardnb):
        return self.svg.xpath(
            '//inkcards:card[@inkcards:deck="%s" and @inkcards:number="%d"]/inkcards:using/@inkcards:layer'%(deckname, cardnb),
            namespaces=NSS)

    def getCardsWithNoBack(self, deckname):
        return self.svg.xpath(
            '//inkcards:card[@inkcards:deck="%s" and not(@inkcards:rear)]'%(deckname),
            namespaces=NSS)

    def getCardsUsingActiveLayers(self):
        activeLayers = self.activeLayers
        cards = self.svg.xpath('//inkcards:card[@inkcards:deck="%s"]'%(self.options.deckname))
        res=[]
        for card in cards:
            layers = map(lambda y: y.attrib[addNS('layer', 'inkcards')], card)
            if all(layer in layers for layer in activeLayers):
                res.append(card)
        return res

    def getCardDetails(self, card):
        detail = ""
        if addNS("rear", 'inkcards') in card.attrib:
            rear = self.svg.getElementById(card.attrib[addNS('rear', 'inkcards')])
            detail = "  🂠 %s (%s %s) ↷ 🃟 %s %s"%(
                rear.attrib[addNS('deck', 'inkcards')],
                rear.attrib[addNS('number', 'inkcards')],
                str(self.getLayernamesOfCard(rear)),
                card.attrib[addNS('number', 'inkcards')],
                str(self.getLayernamesOfCard(card)))
        else:
            detail = "  🃟 %s %s"%(
                card.attrib[addNS('number', 'inkcards')],
                str(self.getLayernamesOfCard(card)))
        return detail

    # End of HELPERS

    def add(self):
        if not self.options.deckname:
            raise inkcardsError("You need to give the deck name you want to add a card to.")
        nsmap = dict(self.svg.nsmap, inkcards=icNS)
        card = etree.SubElement(self.svg,
                                addNS('card', 'inkcards'),
                                nsmap=nsmap)
            
        card.attrib['id'] = self.svg.get_unique_id('card')
        card.attrib[addNS('deck', 'inkcards')] = self.options.deckname
        card.attrib[addNS('number', 'inkcards')] = self.nextCardNB(card.attrib[addNS('deck', 'inkcards')])

        for lname in self.activeLayers:
            l = etree.SubElement(card,
                                 addNS('using', 'inkcards'),
                                 nsmap=nsmap)
            l.attrib[addNS('layer', 'inkcards')] = lname

        if self.options.verbose:
            self.list()

    def remove(self):
        deckname = self.options.deckname
        if self.options.delbynb:
            cards = self.svg.xpath('//inkcards:card[@inkcards:deck="%s" and @inkcards:number="%s"]'%(deckname, self.options.cardno))
            cards[0].getparent().remove(cards[0])
        else:
            layers = self.activeLayers

            for card in self.getCardsInDeck(deckname):
                cardLayerNames = map(lambda using: using.attrib[addNS('layer', 'inkcards')], card[:])
                if all(l in cardLayerNames for l in layers):

                    card.getparent().remove(card)

        if self.options.verbose:
            self.list()

    def list(self):
        self.clean()
        cards = self.svg.xpath('//inkcards:card')
        decks = Card.groupbycat(cards, lambda x: self.svg.xpath('//inkcards:card[@id="%s"]/@inkcards:deck'%x.attrib['id'])[0])
        debug("Currently defined cards are:")
        
        for d in sorted(decks.keys()):
            deck=decks[d]
            deck.sort(key=lambda e: int(e.attrib[addNS('number', 'inkcards')]))
            debug("")
            debug("Deck: %s"%d)
            for c in decks[d]:
                debug(self.getCardDetails(c))
                
    def changeDeck(self):
        cards = self.getCardsUsingActiveLayers()
        if not cards:
            cards = self.getCardsInDeck(self.options.deckname)
        currentdeck = self.getCardsInDeck(self.options.destdeck)
        currentdeck.sort(key=lambda c: c.attrib[addNS('number', 'inkcards')])
        cards.sort(key=lambda c: c.attrib[addNS('number', 'inkcards')])
        for card in cards:
            card.attrib[addNS('deck', 'inkcards')] = self.options.destdeck
            card.attrib[addNS('number', 'inkcards')] = str(len(currentdeck))
            currentdeck.append(card)
        if self.options.verbose:
            self.list()
        
    def reposition(self):
        deck = self.getCardsInDeck(self.options.deckname)
        deck.sort(key=lambda c: int(c.attrib[addNS('number', 'inkcards')]))
        #card = deck.pop(self.getCardsUsingActiveLayers()[0])
        #debug(map(lambda x: x.attrib[addNS('number', 'inkcards')], deck))
        for card in self.getCardsUsingActiveLayers():
            deck.insert(self.options.shiftpos-1, deck.pop(deck.index(card)))
        for pos in range(len(deck)):
            deck[pos].attrib[addNS('number', 'inkcards')] = str(pos)
        if self.options.verbose:
            self.list()

    def activate(self):
        deckname = self.options.deckname
        cardnb = self.options.activateid
        try:
            layers = self.getCardLayers(deckname, cardnb)
        except IndexError:
            raise inkcardsError("There is no card %d in the deck '%s'"%(cardnb, deckname))

        for l in self.allLayers:
            if l.attrib['id'] in layers:
                l.attrib["style"] = "display:inline"
            else:
                l.attrib["style"] = "display:none"

    def clean(self):
        cards = self.svg.xpath('//inkcards:card')
        if not cards:
            return
        try:
            decks = Card.groupbycat(cards, lambda x: self.svg.xpath('//inkcards:card[@id="%s"]/@inkcards:deck'%x.attrib['id'])[0])
        except IndexError as e:
            raise e

        for deckname in decks:
            deck = decks[deckname]
            deck.sort(key=lambda e: int(e.attrib[addNS('number', 'inkcards')]))
            i = 1
            for card in deck:
                card.attrib[addNS('number', 'inkcards')] = str(i)
                i += 1

    def associateRear(self):
        if self.activeLayers:
            frontcards = self.getCardsUsingActiveLayers()
            if not frontcards:
                raise inkcardsError("There is no cards using all the active layers in the deck '%s'."%self.options.deckname)
        else:
            frontcards = self.getCardsWithNoBack(self.options.deckname)
            if not frontcards:
                raise inkcardsError("There is no deck named '%s'."%self.options.deckname)


        try:
            rearcard = self.getCard(self.options.reardeck, self.options.rearnb)
        except IndexError:
            raise inkcardsError("The deck (%s) is empty."%self.options.reardeck)

        for frontcard in frontcards:
            frontcard.attrib[addNS('rear', 'inkcards')] = rearcard.attrib['id']
        if self.options.verbose:
            self.list()

    def effect(self):
        inkcards.effect(self)
        try:
            NSS['inkcards'] = icNS
            {   "add"           : self.add,
                "remove"        : self.remove,
                "list"          : self.list,
                "activate"      : self.activate,
                "changedeck"    : self.changeDeck,
                "shift"         : self.reposition,
                "rear"        : self.associateRear,
            } [re.match('^"?([^"]*)"?$',self.options.function).group(1)]()
            self.clean()
        except inkcardsError as e:
            if self.options.extension:
                e.reportToInkex()
            else:
                raise e

if __name__ == "__main__":
    card = Card()
    card.run()
    # Return the error only if not called from inkscape as inkex is not expected to report errors.
    if not card.options.extension:
        sys.exit(errorCode)

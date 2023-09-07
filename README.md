# Inkcards

Inkcards is an Inkscape extension to create a decks of cards from a single SVG.
You'll need anothe SVG to tile them for printing. The required SVG size is the
same as A single card size from the deck. By activating some layers and
inactivating others, the card shows (in Inkscape). Thus a web game could use a
single SVG as it's card deck. The cards layers are described as inkcards:card
tags. If you want to print the cards, once all cards are drawn, use the
inkcards_tile extension to tile the cards on a page size document. It tile the
cards per page (layers) and let you see the original layers, thought you should
not change them, as they are moved in the defs section of the SVG. There's
currently 2 way to tile cards, basic and book single page, for inspiration on
how to create physical cards using the book single page see [this video](https://youtu.be/DgNJmAkO1_M).

## Install

To install Inkcards, the files src/* should be copied into the Inkscape
extension dir (on Ubuntu: ~/.config/inkscape/extensions). The extension
should then (upon restart) be available in the menu
extensions/🃟 inkcards...

## Usage

Suppose you are creating a smiley based game, where you have some cards
representing different smiley. We can create a *base* layer to give the card
background on top of which we have a *Yellow face* layer containing a single
yellow circle. Then we can draw face element with the *Eyes* and *Mouth* sub layers. We can
then create the smiley cards by choosing the layers to use.

![Card Layers](https://github.com/kristianbenoit/inkcards/blob/4e21ccdbfe2adec54e0f0300f0fa388046c28512/smile.png)

Now using the extension to register the cards by saving the active layers for
each specific card and associate a card as the rear, we have a complete deck
of cards.

![inkcards deck](https://github.com/kristianbenoit/inkcards/blob/4e21ccdbfe2adec54e0f0300f0fa388046c28512/list.png)

Using the `inkcards_tile` extension, from a second, printable sized, *SVG*, we
are copying each layers in the `<def>` section and `<use>` them for each
card making use of it.

![inkcards tile](https://github.com/kristianbenoit/inkcards/blob/4e21ccdbfe2adec54e0f0300f0fa388046c28512/tile.png)

## Tips ##
To prevent from unperfect cuts, you could create a background rectangle the
size of a card and make it's stroke the same color, so that the card bakground
is slighly larger than the card cut locations. Ensure the card extra does not
overlap with the minimal card spacing size.

### Other uses

It could be used to tile any type of cards, let say Decktet Magnate's tokens.
It could also be used to tile instructions you have to follow (origami).

## Future

We could learn with countersheet to edit the text in a card and have a
configuration option to have the text modified. So we could set the text for a
card in the config file.

The step to create a tiled document could be removed, exporting it to *PDF*
directly. ... Create the tiled document according to a given page dimension,
*save a copy* of each page to *PDF* and use *pdfunite* them to create a single *PDF*.

## Credit

I got my base inspiration by ready this [thread](https://boardgamegeek.com/thread/490643/making-cards-youll-never-use-your-old-method-again).
on BoardGameGeek, hence the svg namespace (http://boardgamegeek.com/inkscape/extension/inkcards)

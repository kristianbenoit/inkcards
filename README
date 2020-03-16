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
how to create physical cards using the book single page see (this video)(https://youtu.be/DgNJmAkO1_M).

## Install

To install Inkcards, the files src/* should be copied into the Inkscape
extension dir (on Ubuntu: ~/.config/inkscape/extensions). The extension
should then (upon restart) be available in the menu
extensions/🃟 inkcards...

## Usage

Suppose you are creating a medieval game, where you have some type of cards
like:

- Ennemie
- Spell
- Tresure

You can then create a base layer, one for each of the three type of cards
(which I are refered as deck) and one per card. Modifying a single layer would
then affect all cards using it.

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

I should do it all in the same document, just resize it and move the cards in
defs. I did it this way cause the cards are no longer editable after tiling,
but that seam to add to the complexity...

## Credit

I got my base inspiration by ready this [thread](https://boardgamegeek.com/thread/490643/making-cards-youll-never-use-your-old-method-again).
on BoardGameGeek, hence the svg namespace (http://boardgamegeek.com/inkscape/extension/inkcards)

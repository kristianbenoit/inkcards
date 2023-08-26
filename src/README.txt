See guillotine extension for a way to write png, to be able to generate pdf.

Example of a deck created with inkcards_deck:
# <svg>
#    <defs/>
#    <g id="layer1" inkscape:label="Default_rear"/>
#    <g id="layer2" inkscape:label="Base"/>
#    <g id="layer3" inkscape:label="Specific"/>
#    <inkcards:card id="card1" inkcards:deck="rear" inkcards:cardnb="1">
#       <inkcards:using inkcards:layer="layer1"/>
#    </inkcards:card>
#    <inkcards:card id="card2" inkcards:deck="card" inkcards:cardnb="1" inkcards:rear="card1">
#       <inkcards:using inkcards:layer="layer2">
#       <inkcards:using inkcards:layer="layer3">
#    </inkcards:card>
# </svg>

Converted to a tiled document with inkcards_tile:
# <svg>
#    <defs>
#       <g id="layer10" inkscape:label="inkcards Layers">
#          <!-- Layers are copied in the def section -->
#          <g id="layer1"/>
#          <g id="layer2"/>
#          <g id="layer3"/>
#       </g>
#       <g id="card2" inkcards:deck="card" inkcards:cardnb="1" inkcards:rear="card1">
#          <use xlink:href="#layer2"/>
#          <use xlink:href="#layer3"/>
#       </g>
#       <g id="card1" inkcards:deck="rear" inkcards:cardnb="1">
#          <use xlink:href="#layer3"/>
#       </g>
#    </defs>
#    <g id="layer100" inkscape:label="cut marks">
#        <!-- paths as cut line indications -->
#    </g/>
#    <path id="fold_mark"/> <!-- A line accross the middle page to fold/glue the page (for book1p) -->
#    <g inkscape:label="page1">
#       <use transform="translate(...)" xlink:href="#card2"/>
#       <use transform="translate(...)" xlink:href="#card2"/>
#    </g>
# </svg>


If #run from the terminal add this to be able to import inkex:
 import sys
 sys.path.append("/usr/share/inkscape/extensions/")
 [...]
 import inkex

A way to export multi page doc to PDF:
export each page with "inkscape source.svg --export-filename=out[i].pdf" (changing layers according to the page).
unite them with "pdfunit out*.pdf result.pdf" from poppler.freedesktop.org

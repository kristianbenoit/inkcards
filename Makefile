# Start of Configuration
DPI=600
nb_cards=2
nb_cards_w=2
nb_cards_h=3
SVG_src=testcards.svg
dest=testcards.pdf
conf_file=inkcards.conf
# End of Configuration

# Define vars from the config
cards:=$(shell seq 1 $(nb_cards))
page_layout:=$(nb_cards_w)x$(nb_cards_h)
SVGs:=$(patsubst %, %.svg, $(cards))

# Generate a sequence of pages
cards_per_page:=$(shell echo $$(($(nb_cards_w)*$(nb_cards_h))))
nb_pages:=$(shell echo $$(($(nb_cards) / $(cards_per_page))))
incomplete_page:=$(shell echo $$(($(nb_cards)%$(cards_per_page))))
ifneq ($(incomplete_page),0) 
	nb_pages:=$(shell echo $$(($(nb_pages)+1)))
endif
pages:=$(shell seq 1 $(nb_pages))

# The rules

.phony: clean ALL

ALL: $(dest)

$(dest): $(SVGs)
	montage $^ -tile $(page_layout) -geometry $(DPI) $@

$(SVG_src): ;

%.svg: $(SVG_src)
	python2 ~/dev/inkcards/cards.py --tab=show --page=$(shell echo $@ | head -c -5) --file=$(conf_file) -- $(SVG_src) > $@

clean:
	$(RM) $(dest) $(PDF_pages) $(SVG_pages) $(SVGs)

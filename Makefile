# Start of Configuration
pages=$(shell seq 1 4)
SVG_src=testcards.svg
dest=testcards.pdf
conf_file=inkcards.conf
# End of Configuration

SVG_pages:=$(patsubst %, %.svg, $(pages))
PDF_pages:=$(patsubst %, %.pdf, $(pages))

.phony: clean

$(dest): $(PDF_pages)
	pdfunite $^ $@

$(SVG_src): ;

%.svg: $(SVG_src)
	python2 ~/dev/inkcards/cards.py --tab=show --page=$(shell echo $@ | head -c -5) --file=$(conf_file) -- $(SVG_src) > $@

%.pdf: %.svg
	rsvg-convert -f pdf -o $@ $<

clean:
	$(RM) $(dest) $(PDF_pages) $(SVG_pages)

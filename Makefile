# Configure Here
pages=1 2 3 4
SVG_src=testcards.svg
dest=testcards.pdf
conf_file=inkcards.conf

pages:=$(patsubst %, %.pdf, $(pages))

.phony: clean

$(dest): $(pages)
	pdfunite $^ $@

%.pdf: $(SVG_src)
	python2 ~/dev/inkcards/cards.py --tab=show --page=$(shell echo $@ | head -c -5) --file=$(conf_file) -- $(SVG_src) | rsvg-convert -f pdf -o $@ /dev/stdin

clean:
	-rm $(dest) $(pages)

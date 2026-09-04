# Regenerate publications.md from the publication list in the CV
# (~/git/cv/cv.tex, overridable with CV_TEX).

.PHONY: publications thumbnails check serve

publications:
	python3 scripts/gen_publications.py

# Square, face-centred crops of the photos on people.md, into images/thumbs.
thumbnails:
	python3 scripts/make_thumbnails.py

check:
	python3 scripts/gen_publications.py --check

serve:
	bundle exec jekyll serve

PYTHON ?= python3
BOOK ?=
WORKERS ?= 4

.PHONY: help run delete-preview delete check-book

help:
	@printf "%s\n" \
		"Pipeline commands:" \
		"  make run BOOK=1910.pdf" \
		"  make run BOOK=1910.pdf WORKERS=8" \
		"  make delete-preview BOOK=1910.pdf" \
		"  make delete BOOK=1910.pdf"

run: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --workers "$(WORKERS)"

delete-preview: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --delete --dry-run

delete: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --delete

check-book:
	@test -n "$(BOOK)" || (echo "Set BOOK=book.pdf"; exit 1)

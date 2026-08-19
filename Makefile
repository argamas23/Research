PYTHON ?= python3
BOOK ?=
WORKERS ?= 4

.PHONY: help run graph validation-auto network-analysis salt-analysis corpus-audit citation-verify research-outputs delete-preview delete check-book

help:
	@printf "%s\n" \
		"Pipeline commands:" \
		"  make run BOOK=1910.pdf" \
		"  make run BOOK=1910.pdf WORKERS=8" \
		"  make graph" \
		"  make validation-auto" \
		"  make network-analysis" \
		"  make salt-analysis" \
		"  make corpus-audit" \
		"  make citation-verify" \
		"  make research-outputs" \
		"  make delete-preview BOOK=1910.pdf" \
		"  make delete BOOK=1910.pdf"

run: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --workers "$(WORKERS)"

graph:
	$(PYTHON) Mine/rebuild_graph.py
	$(PYTHON) Mine/salt_recall_audit.py

validation-auto:
	$(PYTHON) Mine/evidence_validate.py

network-analysis:
	$(PYTHON) Mine/network_analysis.py

salt-analysis:
	$(PYTHON) Mine/salt_analysis.py

corpus-audit:
	$(PYTHON) Mine/corpus_audit.py

citation-verify:
	$(PYTHON) Mine/citation_verify.py

research-outputs: corpus-audit citation-verify

delete-preview: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --delete --dry-run

delete: check-book
	$(PYTHON) Mine/pipeline.py --book "$(BOOK)" --delete

check-book:
	@test -n "$(BOOK)" || (echo "Set BOOK=book.pdf"; exit 1)

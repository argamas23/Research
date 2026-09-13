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
	$(PYTHON) pipeline/pipeline.py --book "$(BOOK)" --workers "$(WORKERS)"

graph:
	$(PYTHON) pipeline/rebuild_graph.py
	$(PYTHON) pipeline/audit_salt_recall.py

validation-auto:
	$(PYTHON) pipeline/validate_evidence.py

network-analysis:
	$(PYTHON) pipeline/analyze_network.py

salt-analysis:
	$(PYTHON) pipeline/analyze_salt.py

corpus-audit:
	$(PYTHON) pipeline/audit_corpus.py

citation-verify:
	$(PYTHON) pipeline/verify_citations.py

research-outputs: corpus-audit citation-verify

delete-preview: check-book
	$(PYTHON) pipeline/pipeline.py --book "$(BOOK)" --delete --dry-run

delete: check-book
	$(PYTHON) pipeline/pipeline.py --book "$(BOOK)" --delete

check-book:
	@test -n "$(BOOK)" || (echo "Set BOOK=book.pdf"; exit 1)

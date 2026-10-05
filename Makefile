# Local build. Requires pandoc and `pip install -r requirements.txt`.
PY ?= python3

.PHONY: docx site serve reference lint clean

docx:            ## Word files for all pages -> docs/downloads/
	$(PY) build/build_docx.py

site: docx       ## Static website -> site/
	$(PY) -m mkdocs build

serve: docx      ## Live preview at http://127.0.0.1:8000
	$(PY) -m mkdocs serve

reference:       ## Rebuild the Word style template after editing build/make_reference_docx.py
	$(PY) build/make_reference_docx.py

lint:            ## ASD-STE100 check of the English text
	$(PY) build/ste_check.py

clean:
	rm -rf site docs/downloads

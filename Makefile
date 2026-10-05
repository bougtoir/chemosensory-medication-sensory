PYTHON ?= python3

all: evidence matrices figures

evidence:
	$(PYTHON) scripts/01_pubmed_search.py
	$(PYTHON) scripts/02_bitterdb_scrape.py
	$(PYTHON) scripts/03_pubchem_drug_space.py
	$(PYTHON) scripts/04_curate_evidence.py

matrices:
	$(PYTHON) scripts/05_evidence_graph.py
	$(PYTHON) scripts/06_meta_analysis.py
	$(PYTHON) scripts/07_matrices_predictions.py

figures:
	$(PYTHON) scripts/08_figures.py

test:
	$(PYTHON) -m pytest tests/ -q

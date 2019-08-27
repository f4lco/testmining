
DUMP=travistorrent_8_2_2017.csv

lint:
	pylint testmining tests

notebook:
	pipenv run jupyter notebook -y --notebook-dir notebook

test:
	pipenv run pytest tests

treon: test
	pipenv run python -m tests.notebooks
	
projects:
	PRIO_BASE=output pipenv run python -m testmining.projects -f $(DUMP)

builds:
	PRIO_BASE=output pipenv run python -m testmining.builds -f $(DUMP)

sanity:
	pipenv run python -m testmining.sanity

boxplot:
	PRIO_BASE=output pipenv run python -m testmining.apfd_plot boxes untreated recently-failed matrix-recently-changed optimal-failure

boxplot-open:
	find output -path "*/${PRIO_QUALIFIER:-baseline}-evaluation/*-boxplot.png" | xargs open

ridgeline:
	PRIO_BASE=output pipenv run python -m testmining.apfd_plot ridgelines untreated recently-failed matrix-recently-changed optimal-failure

ridgeline-open:
	find output -path "*/${PRIO_QUALIFIER}-evaluation/*-ridgeline.png" | xargs open

combined:
	PRIO_BASE=output pipenv run python -m testmining.apfd_plot combined --output combined-foo.png untreated random lru recently-failed matrix-conditional-prob matrix-file-similarity matrix-tc-similarity matrix-recently-changed

apfd:
	PRIO_BASE=output pipenv run python -m testmining.apfd_computation

thesis-images-mpl:
	pipenv run python -m testmining.apfd_plot_mpl combined --output all-untreated-optimal.pdf untreated optimal-failure
	pipenv run python -m testmining.apfd_plot_mpl combined --output baseline.pdf untreated random lru recently-failed
	pipenv run python -m testmining.apfd_plot_mpl combined --output baseline-optimal.pdf untreated random lru recently-failed optimal-failure
	pipenv run python -m testmining.apfd_plot_mpl combined --output matrix.pdf recently-failed matrix-conditional-prob matrix-path-similarity matrix-file-similarity matrix-tc-similarity matrix-recently-changed
	pipenv run python -m testmining.apfd_plot_mpl combined --output matrix2.pdf matrix-conditional-prob matrix-path-similarity matrix-file-similarity matrix-tc-similarity matrix-recently-changed
	pipenv run python -m testmining.apfd_plot_mpl combined --output all.pdf untreated random lru recently-failed matrix-conditional-prob matrix-path-similarity matrix-file-similarity matrix-tc-similarity matrix-recently-changed optimal-failure

evaluation: apfd sanity

.PHONY: apfd notebook test

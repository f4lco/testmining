
DUMP=travistorrent_8_2_2017.csv


notebook:
	pipenv run jupyter notebook -y --notebook-dir notebook

test:
	pipenv run pytest tests
	cd notebook && pipenv run treon --threads 1

projects:
	pipenv run python -m testmining.projects -f $(DUMP)

builds:
	PRIO_BASE=output pipenv run python -m testmining.builds -f $(DUMP)

sanity:
	pipenv run python -m testmining.sanity

apfd_plots:
	PRIO_BASE=output pipenv run python -m testmining.apfd_plot boxes untreated recently-failed matrix-recently-changed optimal-failure

apfd_csv:
	PRIO_BASE=output pipenv run python -m testmining.apfd_computation

open_baseline_boxplot:
	find output -path "*/baseline-evaluation/*-boxplot.png" | xargs open

open_baseline_ridgeline:
	find output -path "*/baseline-evaluation/*-ridgeline.png" | xargs open

open_experimental_boxplot:
	find output -path "*/experimental-evaluation/*-boxplot.png" | xargs open

open_experimental_ridgeline:
	find output -path "*/experimental-evaluation/*-ridgeline.png" | xargs open

.PHONY: notebook projects builds \
apfd_plots apfd_csv open_baseline_boxplot \
open_experimental_boxplot


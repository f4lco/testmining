# -*- encoding: utf-8 -*-
import click
import logging

import numpy as np
import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)

# Regular expression for columns containing evaluated heuristics
HEURISTICS = \
    r'^(?!(travisJobId|optimal-failure|optimal-failure-duration|push-.*)$)\w+'


def _check_optimal_failure(df):
    others = df.filter(regex=HEURISTICS)

    def is_invalid(col):
        opt = df['optimal-failure']
        heuristic = df[col]
        valid = (heuristic <= opt) | np.isclose(heuristic, opt)
        return ~valid.any()

    invalid = list(filter(is_invalid, others.columns))
    assert not invalid, "Strategies %s outperformed optimal ordering" % invalid


CHECKS = [
    _check_optimal_failure
]


def _check(project_name, df):
    try:
        for check in CHECKS:
            check(df)
    except AssertionError as e:
        LOG.warning("Validating %s: got error %s", project_name, e)
    else:
        LOG.info("Completed checks without errors")


@click.command()
def main():
    for project_name, project_path in folders.projects():
        df = pd.read_csv(folders.apfd(project_path))
        _check(project_name, df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

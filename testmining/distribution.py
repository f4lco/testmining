# -*- encoding: utf-8 -*-

"""
Plot a distribution chart which shows how many jobs have a certain count of
distinct failing test classes.
"""

import os
import logging

import click

import altair as alt
import pandas as pd

from testmining import folders
from testmining.apfd import read_tests

LOG = logging.getLogger(__file__)


def plot(project_name, project_path):
    LOG.info('Processing %s', project_name)
    df = read_tests(folders.strategy(project_path, 'untreated'))

    def failed_tc(group):
        return pd.Series(len(group[group.red > 0]['testName'].unique()),
                         index=['failed_tc'])

    jobs = df.groupby('travisJobId').apply(failed_tc).reset_index()
    chart = alt.Chart(jobs, title=project_name).mark_bar().encode(
        x=alt.X('failed_tc'),
        y=alt.Y('count()'),
    )
    output = os.path.join(folders.evaluation(project_path),
                          'failed_tc_distribution.png')
    chart.save(output)
    LOG.info('Written %s', output)


@click.command(help=__doc__)
def main():
    for project_name, project_path in folders.projects():
        plot(project_name, project_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

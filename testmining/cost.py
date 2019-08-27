# -*- encoding: utf-8 -*-

"""
Given a duration, how many test classes are there? (bar and scatter plot)
"""

import logging
import os

import click

import altair as alt
import pandas as pd

from testmining import folders


LOG = logging.getLogger(__file__)


def duration_df(file):
    LOG.info('Reading %s', file)
    df = pd.read_csv(file)['duration'].value_counts().to_frame()
    return df.reset_index().rename(columns={
        'index': 'duration',
        'duration': 'count'
    })


def duration_chart(project_name, file):
    return alt.Chart(duration_df(file), title=project_name).mark_bar().encode(
        x=alt.X('duration', bin=alt.BinParams(step=2)),
        y=alt.Y('count', scale=alt.Scale(type='log'),
                axis=alt.Axis(grid=False))
    )


def duration_per_test(project_name, file):
    df = pd.read_csv(file)[['testName', 'duration', 'count']]
    return alt.Chart(df, title=project_name).mark_point(filled=True).encode(
        x='duration',
        y='count',
        tooltip=['testName', 'duration', 'count'],
    )


def save(project_path, chart, name):
    path = os.path.join(folders.evaluation(project_path),
                        'duration-%s.png' % name)
    chart.save(path, scale_factor=2.0)
    LOG.info('Written %s', path)


@click.group(help==__doc__)
def cli():
    logging.basicConfig(level=logging.INFO)


@cli.command()
def distribution():
    for project_name, project_path in folders.projects():
        untreated = folders.strategy(project_path, 'untreated')
        chart = duration_chart(project_name, untreated)
        save(project_path, chart, 'distribution')


@cli.command()
def scatter():
    for project_name, project_path in folders.projects():
        untreated = folders.strategy(project_path, 'untreated')
        chart = duration_per_test(project_name, untreated)
        save(project_path, chart, 'scatter')


if __name__ == '__main__':
    cli()

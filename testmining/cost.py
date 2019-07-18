# -*- encoding: utf-8 -*-
import logging
import os

import click

import altair as alt
import pandas as pd

from tqdm import tqdm
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
        x='count',
        y='duration',
        tooltip=['testName', 'duration', 'count'],
    )


def compute_rbo(project_path):

    def read(strategy):
        df = pd.read_csv(folders.strategy(project_path, strategy))[[
            'travisJobId',
            'testName'
        ]]
        return df, df.groupby('travisJobId').groups

    def rbo_job(job):
        series_a = tests_a.loc[groups_a[job]]
        series_b = tests_b.loc[groups_b[job]]
        assert len(series_a) == len(series_b)
        result = []
        xs = set()
        ys = set()
        for index in range(len(series_a)):
            xs.add(series_a.iloc[index]['testName'])
            ys.add(series_b.iloc[index]['testName'])
            common = len(xs.intersection(ys))
            result.append(common / (index + 1))
        assert len(result) == len(series_a)
        return pd.Series(result).median()

    tests_a, groups_a = read('optimal-failure')
    tests_b, groups_b = read('optimal-failure-duration')

    results = []
    for job in tqdm(list(tests_a['travisJobId'].unique())):
        results.append((job, rbo_job(job)))
    return pd.DataFrame(results, columns=['travisJobId', 'rbo'])


def rbo(project_name, project_path):
    df = compute_rbo(project_path)
    return alt.Chart(df, title=project_name).mark_bar().encode(

        x=alt.X('rbo',
                bin=alt.BinParams(step=0.05),
                scale=alt.Scale(domain=[0, 1])),

        y=alt.Y('count()')
    )


def save(project_path, chart, name):
    path = os.path.join(folders.evaluation(project_path),
                        'duration-%s.png' % name)
    chart.save(path, scale_factor=2.0)
    LOG.info('Written %s', path)


@click.group()
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


@cli.command()
def optimality():
    for project_name, project_path in folders.projects():
        chart = rbo(project_name, project_path)
        save(project_path, chart, 'rbo')


if __name__ == '__main__':
    cli()

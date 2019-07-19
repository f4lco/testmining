# -*- encoding: utf-8 -*-
import logging
import os

import click

import altair as alt
import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)


def collect_apfd():
    frames = []
    for project_name, project_path in folders.projects():
        frames.append(read_trend(project_name, project_path))
    return pd.concat(frames)


def read_trend(project_name, project_path):
    df = pd.read_csv(folders.apfd(project_path))[['untreated']].reset_index()
    df['trend'] = df['untreated'].rolling(50, min_periods=1).mean()
    df['project'] = project_name
    return df


def apfd_line():
    return alt.Chart().mark_line().encode(
        x=alt.X('index'),
        y=alt.Y('trend'),
        color=alt.Color('project'),
    )


def apfd_scatter():
    return alt.Chart().mark_point(filled=True).encode(
        x='index',
        y='untreated',
        color='project',
    )


def collect_tests():
    frames = []
    for project_name, project_path in folders.projects():
        raw = pd.read_csv(folders.strategy(project_path, 'untreated'))
        df = raw.groupby('travisBuildNumber').agg({'count': 'sum'}).reset_index()
        df['project'] = project_name.split('@')[1]
        df['count'] = df['count'].rolling(50, min_periods=1).mean()
        frames.append(df)
    return pd.concat(frames)


def tc_line():
    return alt.Chart().mark_line().encode(
        x='travisBuildNumber',
        y='count',
        color='project',
    )


@click.command()
def main():
    for project_name, project_path in folders.projects():
        df = read_trend(project_name, project_path)
        chart = apfd_line().properties(data=df)
        output = os.path.join(folders.evaluation(project_path), 'apfd-trend.png')
        chart.save(output)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

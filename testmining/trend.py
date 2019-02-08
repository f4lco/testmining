# -*- encoding: utf-8 -*-
import click
import logging
import os

import altair as alt
import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)


@click.group()
def cli():
    pass


@cli.command()
def apfd():
    frames = []
    for project_name, project_path in folders.projects():
        df = pd.read_csv(folders.apfd(project_path))[['untreated']].reset_index()
        df['trend'] = df['untreated'].rolling(50, min_periods=1).mean()
        #df['trend'] = (df['untreated'] / 0.5) * 100
        df['project'] = project_name
        frames.append(df)

    df = pd.concat(frames)


    #scatter = alt.Chart().mark_point(filled=True).encode(
    #    x='index',
    #    y='untreated',
    #)

    line = alt.Chart().mark_line(color='red').encode(
        x=alt.X('index'),
        y=alt.Y('trend'),
        color='project',
    )

    line.properties(data=df).save(os.path.expanduser('~/tmp/schrott.png'))

    #output = os.path.join(folders.evaluation(project_path), 'apfd-trend.png')
    #alt.layer(scatter, line).properties(data=df, title=project_name).save(output)
    #LOG.info('Written %s', output)


@cli.command()
@click.option('--output', required=True)
def tests(output):
    for project_name, project_path in folders.projects():
        df = pd.read_csv(folders.strategy(project_path, 'untreated'))
        df = df[['travisBuildNumber', 'count']]
        df['count'] = df['count'].rolling(50, min_periods=1).mean()
        df['project'] = project_name.split('@')[1]
        output = os.path.join(folders.evaluation(project_path))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()

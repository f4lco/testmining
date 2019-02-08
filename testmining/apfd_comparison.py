# -*- encoding: utf-8 -*-

import click

from collections import defaultdict
from pprint import pprint

from testmining.apfd_plot import read_apfd
from testmining import folders


def thesis1(df):
    return (df['untreated'] > df['random']) or \
           (df['untreated'] > df['lru'])


def thesis2(df):
    return df.idxmax() == 'recently-failed'


def thesis3(df):
    return df['random'] > df['lru']


def thesis4(df):
    return df['lru'] < df['untreated']


def thesis5(df):
    return df['random'] < df['untreated']


@click.group()
def cli():
    pass


@cli.command()
def baseline():
    d = defaultdict(lambda: 0)
    for project_name, project_path in folders.projects():
        df = read_apfd(project_path)[[
            'untreated',
            'random',
            'lru',
            'recently-failed',
        ]].median()

        d['untreated-not-last'] += thesis1(df)
        d['recently-failed-first'] += thesis2(df)
        d['random-beats-lru'] += thesis3(df)
        d['lru-is-worse'] += thesis4(df)
        d['random-is-worse'] += thesis5(df)

    pprint(dict(d))


@cli.command()
def matrix():

    def t1(df):
        return df.idxmax().startswith('matrix')

    def t2(df):
        return df['matrix-path-similarity'] == df['matrix-file-similarity']

    d = defaultdict(lambda: 0)
    for project_name, project_path in folders.projects():
        df = read_apfd(project_path)[[
            'recently-failed',
            'matrix-conditional-prob',
            'matrix-tc-similarity',
            'matrix-path-similarity',
            'matrix-file-similarity',
            'matrix-recently-changed',
        ]].median()

        d['matrix-wins'] += t1(df)
        d['file-path-agreement'] += t2(df)

    pprint(dict(d))


if __name__ == '__main__':
    cli()

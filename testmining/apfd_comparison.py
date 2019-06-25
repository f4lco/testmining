# -*- encoding: utf-8 -*-

import click

import numpy as np

from collections import defaultdict
from pprint import pprint

from testmining.apfd_plot import read_apfd
from testmining import folders

"""
Make simple statements on per-project basis.

For example: we have evidence that on X projects, strategy Y is superior.
There are two groups of statements: one that is only concerned with baseline
heuristics, and another set of statements comparing all matrix-based strategies
to the best baseline heuristic.
"""


STATEMENTS = defaultdict(list)


def baseline(func):
    STATEMENTS['baseline'].append(func)
    return func


def matrix(func):
    STATEMENTS['matrix'].append(func)
    return func


def statements(group):
    for f in STATEMENTS[group]:
        yield f.__name__, f


@baseline
def untreated_not_last(df):
    return (df['untreated'] > df['random']) or \
           (df['untreated'] > df['lru'])


@baseline
def recently_failed_first(df):
    return df.idxmax() == 'recently-failed'


@baseline
def random_beats_lru(df):
    return df['random'] > df['lru']


@baseline
def lru_is_worse(df):
    return df['lru'] < df['untreated']


@baseline
def random_is_worse(df):
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

        for key, func in statements('baseline'):
            d[key] += func(df)

    pprint(dict(d))


@matrix
def recently_changed_first(df):
    return df.idxmax() == 'matrix-recently-changed'


@matrix
def matrix_first(df):
    return df.idxmax().startswith('matrix')


@matrix
def on_par(df):
    return matrix_first(df) or \
           df.filter(regex='matrix*').idxmax() == df['recently-failed']


@matrix
def on_par_close(df):
    if matrix_first(df):
        return True

    second = df.filter(regex='matrix*').idxmax()
    return np.isclose(df['recently-failed'], df[second])


@matrix
def file_path_agreement(df):
    return np.isclose(df['matrix-path-similarity'],
                      df['matrix-file-similarity'])


@cli.command()
def matrix():
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

        for name, func in statements('matrix'):
            d[name] += func(df)

    pprint(dict(d))


if __name__ == '__main__':
    cli()

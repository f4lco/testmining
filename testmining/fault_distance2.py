# -*- encoding: utf-8 -*-
import click
import logging

import altair as alt
import numpy as np
import pandas as pd

from testmining import folders
from testmining.apfd import read_tests

LOG = logging.getLogger(__file__)


def _failure_distance(builds):
    """For every build, determine how many builds the current failures are in the past.

    For example:
     - in build X, test T failed. Last time, T failed 5 builds ago.
     - in build Y, test U failed, as it just did in the build before.

    This allows a finer-grained characterization of "edge changelists". E.g., include
    only edge change lists whose failures are at least 10 builds apart.

    Implementation note: we scan the build numbers in descending order from left-to-right.
    Each increment in the index means one further step into the past.
    """

    build_numbers = builds.index.unique().sort_values(ascending=False)

    def tests_from_index(index):
        build_number = build_numbers[index]
        return set(builds.loc[build_number]['testName'])

    index = 0
    rows = []
    while index < len(build_numbers):
        red_tests = tests_from_index(index)
        prior_index = index + 1
        distance = {}

        while prior_index < len(builds):

            for test in tests_from_index(prior_index):
                if test in red_tests:
                    distance[test] = prior_index - index
                    red_tests.remove(test)

            if not red_tests:
                break
            prior_index += 1

        for test in red_tests:
            distance[test] = np.nan

        rows.append((
            builds.loc[build_numbers[index]]['travisBuildId'],
            min(distance.values())
        ))
        index += 1

    return pd.DataFrame(rows, columns=['travisBuildId', 'distance'])


def _failed_builds(untreated):
    return untreated[untreated['red'] > 0].groupby('travisBuildNumber').agg({
        'travisBuildId': 'first',
        'testName': list,
        'travisJobId': list,
    })


def _build_apfd(project_path, untreated, strategies=None):
    job_to_build = untreated[['travisJobId', 'travisBuildId']].drop_duplicates()

    job_apfd = pd.read_csv(
        folders.apfd(project_path),
        usecols=['travisJobId'] + list(strategies) if strategies else None
    ).melt(
        id_vars=['travisJobId'],
        var_name='strategy',
        value_name='apfd'
    )

    return pd.merge(
        left=job_apfd,
        right=job_to_build,
        on='travisJobId',
        validate='m:1'
    ).groupby(['travisBuildId', 'strategy']).agg({
        'apfd': 'median',
    }).reset_index()


def compute_distances(project_path, strategies):
    untreated = read_tests(folders.strategy(project_path, 'untreated'))
    builds = _failed_builds(untreated)
    apfd = _build_apfd(project_path, untreated, strategies)
    distances = _failure_distance(builds)
    return pd.merge(left=apfd,
                    right=distances,
                    on='travisBuildId',
                    validate='m:1')


def collect_distances(strategies):
    dfs = []
    for project_name, project_path in folders.projects():
        dfs.append(compute_distances(project_path, strategies))
    return pd.concat(dfs)


def _handle_project(project_path):
    df = compute_distances(project_path)


@click.group()
def cli():
    pass


@cli.command()
def scatter():
    for project_name, project_path in folders.projects():
        _handle_project(project_path)


def distance_bar_chart(df):
    return alt.Chart(df).mark_bar(opacity=.85).encode(
        x=alt.X('strategy:O', axis=None),
        y=alt.Y('median(apfd)', scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format='%', grid=False), title='APFD'),
        color='strategy',
        column=alt.Column('distance', bin=alt.BinParams(maxbins=20),
                          title='Fault Distance')
    ).transform_filter("datum.distance != null")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()

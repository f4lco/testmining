# -*- encoding: utf-8 -*-
import logging
import os
import warnings

import click

import altair as alt
import numpy as np
import pandas as pd

from testmining import folders, util
from testmining.apfd import read_tests

LOG = logging.getLogger(__file__)

# pragma pylint: disable=fixme


def _load_builds():
    path = folders.cache()
    with pd.HDFStore(path) as store:
        return store['builds']


BUILDS = _load_builds()


def build_timestamps(project_name):
    builds = BUILDS[BUILDS['gh_project_name'] == util.db_project_name(project_name)]

    end = builds['gh_build_started_at'] + \
        pd.to_timedelta(builds['tr_duration'], unit='s')

    return pd.DataFrame({
        'begin': builds['gh_build_started_at'],
        'end': end,
    }).reset_index().set_index(builds['tr_build_number'])


def _failure_distance(project_name, builds):
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
    build_ts = build_timestamps(project_name).sort_index(ascending=False)

    index = 0
    rows = []

    while index < len(build_numbers):
        build_number = build_numbers[index]
        red_tests = set(builds.loc[build_number]['testName'])
        prior_index = index + 1
        distance = {}
        begin = pd.Series(build_ts.loc[build_number]['begin']).min()  # FIXME

        while prior_index < len(builds):

            prior_build_number = build_numbers[prior_index]
            prior_end = pd.Series(build_ts.loc[prior_build_number]['end']).max()  # FIXME
            # Major problem with TravisTorrent: some build numbers are assigned twice
            # Example: julianhyde/optiq 626
            if prior_end > begin:
                prior_index += 1
                continue

            for test in set(builds.loc[prior_build_number]['testName']):
                if test in red_tests:
                    distance[test] = prior_index - index
                    red_tests.remove(test)

            if red_tests:
                prior_index += 1
            else:
                break

        for test in red_tests:
            distance[test] = np.nan

        rows.append((
            builds.loc[build_number]['travisBuildId'],
            _min_nan(distance.values())
        ))
        index += 1

    return pd.DataFrame(rows, columns=['travisBuildId', 'distance'])


def _min_nan(it):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        return np.nanmin(list(it))


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


def compute_distances(project_name, project_path, strategies):
    untreated = read_tests(folders.strategy(project_path, 'untreated'))
    builds = _failed_builds(untreated)
    apfd = _build_apfd(project_path, untreated, strategies)
    distances = _failure_distance(project_name, builds)
    return pd.merge(left=apfd,
                    right=distances,
                    on='travisBuildId',
                    validate='m:1')


def collect_distances(strategies):
    dfs = []
    for project_name, project_path in folders.projects():
        LOG.info('Processing %s', project_name)
        dfs.append(compute_distances(project_name, project_path, strategies))
    return pd.concat(dfs)


def _handle_project(project_name, project_path, strategies):
    df = compute_distances(project_name, project_path, strategies)
    chart = make_scatter_chart(df).properties(title=project_path)
    output = os.path.join(folders.evaluation(project_path), 'testi2.png')
    chart.save(output)

###############################################################################


def make_scatter_chart(h):
    #return make_scatter() & make_area() & make_area2() & make_support()
    return (make_scatter() & make_support()).properties(data=h)


def make_scatter():
    return alt.Chart().mark_point(filled=True).encode(
        x=alt.X('distance', title='', axis=None), #, scale=alt.Scale(domain=[1, 651])),
        y=alt.Y('apfd', axis=alt.Axis(format='%'), title='APFD'),
        color=alt.Color('strategy', legend=alt.Legend(title='Strategy')),
        tooltip=['strategy', 'apfd', 'travisBuildId'],
    )


def make_area():
    return alt.Chart(height=50).mark_line().encode(
        x=alt.X('distance', title=''),
        y=alt.Y('median(apfd)', title='APFD', axis=alt.Axis(format='%')),
        color='strategy')


def make_area2():
    return alt.Chart(height=50).mark_area(opacity=.3).encode(
        x=alt.X('distance', title='', bin=alt.BinParams(maxbins=8)),
        y=alt.Y('mean(apfd)', title='APFD', stack=None, axis=alt.Axis(format='%')),
        color='strategy')


def make_support():
    return alt.Chart(height=50).mark_bar().encode(
        x=alt.X('distance', title='Failure Distance', bin=alt.BinParams(step=50, anchor=1)),
        y=alt.Y('count()',
                stack='zero',
                title='Count',
                scale=alt.Scale(type='log'),
                axis=alt.Axis(grid=False, ticks=False)),
        color=alt.value('#7a7a7a'),
    )

###############################################################################


@click.group()
def cli():
    pass


@cli.command()
@click.argument('strategies', nargs=-1)
def scatter(strategies):
    for project_name, project_path in folders.projects():
        LOG.info('Processing %s', project_name)
        _handle_project(project_name, project_path, strategies)


@cli.command()
@click.option('--output', required=True)
@click.argument('strategies', nargs=-1)
def scatter_all(output, strategies):
    df = collect_distances(strategies)
    chart = make_scatter_chart(df)
    chart.save(output)


@cli.command()
@click.argument('strategies', nargs=-1)
def comparison(strategies):
    collect_distances(strategies)


def distance_bar_chart(df):
    return alt.Chart(df).mark_bar(opacity=.85).encode(
        x=alt.X('strategy:O', axis=None),
        y=alt.Y('median(apfd)', scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format='%', grid=False), title='APFD'),
        color=alt.Color('strategy', legend=alt.Legend(title='Strategy')),
        column=alt.Column('distance', bin=alt.BinParams(anchor=1, maxbins=20),
                          title='Failure Distance'),
        tooltip=['strategy', 'median(apfd)'],
    ).transform_filter("datum.distance != null")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()

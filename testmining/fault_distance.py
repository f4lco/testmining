# -*- encoding: utf-8 -*-
import click

import altair as alt
import pandas as pd

from testmining import folders

import numpy as np


def failure_distance(builds):
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

        rows.append((build_numbers[index], min(distance.values())))
        index += 1

    return pd.DataFrame(rows, columns=['travisBuildNumber', 'distance'])


def process_project(project_path):
    df = pd.read_csv(folders.strategy(project_path, 'untreated'))
    failed_builds = df[(df['failures'] > 0) | (df['errors'] > 0)].groupby('travisBuildNumber').agg({
        'testName': list,
        'travisJobId': list,
    })
    distances = failure_distance(failed_builds)
    return make_df(project_path, df, distances)
    #chart = make_chart(project_path, df, distances)
    #chart.save(os.path.join(folders.evaluation(project_path), 'testi.png'))


def make_df(project_path, df, distances):
    apfd = pd.read_csv(folders.apfd(project_path))

    f = pd.merge(left=apfd[
        ['travisJobId', 'matrix-recently-changed', 'recently-failed']],
                 right=df[
                     ['travisBuildNumber', 'travisJobId']].drop_duplicates(),
                 on='travisJobId',
                 validate='1:1')

    f = f.groupby('travisBuildNumber').agg({
        'matrix-recently-changed': 'median',
        'recently-failed': 'median',
    }).reset_index()

    g = pd.merge(left=distances,
                 right=f,
                 on='travisBuildNumber',
                 validate='1:1')

    h = pd.melt(g, id_vars=['distance'],
                value_vars=['matrix-recently-changed', 'recently-failed'])

    # q = h['distance'].quantile([0, 0.75])
    # h = h[h['distance'].between(*q.tolist())]
    #h = h[h.distance < 300]
    return h


def make_chart(h):
    return alt.Chart(h).mark_bar(opacity=.85).encode(
        x=alt.X('variable:O', axis=None),
        y=alt.Y('median(value)', scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format='%', grid=False), title='APFD'),
        color='variable',
        column=alt.Column('distance', bin=alt.BinParams(maxbins=20),
                          title='Fault Distance')
    ).transform_filter("datum.distance != null")#.transform_filter("datum.distance < 180")
    #return make_scatter(h) & make_area(h) & make_area2(h) & make_support(h)


def make_scatter(df):
    return alt.Chart(df).mark_point(
        filled=True).encode(
        x=alt.X('distance'),
        y='value',
        color='variable',
        shape='variable')


def make_area(df):
    return alt.Chart(df, height=50).mark_line(interpolate='monotone').encode(
    #return alt.Chart(df, height=50).mark_line().encode(
        x=alt.X('distance', title=''),
        y=alt.Y('mean(value)', title=''),
        color='variable')


def make_area2(df):
    return alt.Chart(df, height=50).mark_area(interpolate='monotone', opacity=.3).encode(
    #return alt.Chart(df, height=50).mark_area(opacity=.3).encode(
        x=alt.X('distance', title=''),
        y=alt.Y('mean(value)', title='', stack=None),
        color='variable')


def make_support(df):
    return alt.Chart(df, height=50).mark_area(opacity=.3).encode(
        x=alt.X('distance', title=''),
        y=alt.Y('count()', title='', stack=None),
        color='variable')


@click.command()
@click.option('--output', required=True)
def main(output):
    dfs = []
    for project_name, project_path in folders.projects():
        dfs.append(process_project(project_path))
    df = pd.concat(dfs)
    chart = make_chart(df)
    chart.save(output)


if __name__ == '__main__':
    main()

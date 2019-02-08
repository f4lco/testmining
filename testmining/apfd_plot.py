# -*- encoding: utf-8 -*-

import click
import logging
import os

import altair as alt
import pandas as pd

from testmining import apfd, folders

# Strategies appear in this order in all plots
STRATEGIES = [
    'untreated',
    'random',
    'lru',
    'recently-failed',
    'matrix-naive',
    'matrix-conditional-prob',
    'matrix-path-similarity',
    'matrix-file-similarity',
    'matrix-tc-similarity',
    'matrix-recently-changed',
    'path-tc-overlap',
    'bloom',
    'optimal-failure',
    'optimal-failure-duration',
]

LOG = logging.getLogger(__file__)


def bar_chart_transform(df):
    median = df.drop(columns='travisJobId').median()
    return median.to_frame().reset_index().rename(columns={
        'index': 'strategy',
        0: 'apfd',
    })


def apfd_bar_chart(title, df):
    return alt.Chart(bar_chart_transform(df), title=title).mark_bar().encode(
        x=alt.X('strategy', sort=STRATEGIES, axis=alt.Axis(labelAngle=-30)),
        y=alt.Y('apfd', scale=alt.Scale(domain=[0, 1])),
        color='strategy:N',
    )


def bars_filename(project_path):
    return os.path.join(folders.evaluation(project_path), 'apfd-bars.png')


def save_bar_chart(project_name, project_path, df):
    chart = apfd_bar_chart(project_name, df)
    filename = bars_filename(project_path)
    chart.save(filename, scale_factor=2.0)
    LOG.info("Written %s", filename)


def boxplot_transform(df):
    return df.drop('travisJobId', axis=1).melt(var_name='strategy',
                                               value_name='apfd')


def apfd_boxplot(boxplot_df, title):
    # Sorting layered charts is broken
    # https://github.com/altair-viz/altair/issues/820
    # Workaround: hide all labels except one, set resolve to 'independent'
    # Base idea taken from https://altair-viz.github.io/gallery/boxplot_max_min.html

    base = alt.Chart(boxplot_df, title=title)

    scale = alt.Scale(domain=[0, 1])

    lower_box = 'q1(apfd):Q'
    lower_whisker = 'min(apfd):Q'
    upper_box = 'q3(apfd):Q'
    upper_whisker = 'max(apfd):Q'
    tick = 'median(apfd):Q'

    lower_plot = base.mark_rule().encode(
        y=alt.Y(lower_whisker,
                scale=scale,
                title='APFD',
                axis=alt.Axis(format='%')),
        y2=lower_box,
        x=alt.X('strategy',
                title='',
                sort=STRATEGIES,
                axis=alt.Axis(labelAngle=-30))
    )

    middle_plot = base.mark_bar(size=5.).encode(
        y=alt.Y(lower_box, scale=scale),
        y2=upper_box,
        x=alt.X('strategy', title='', sort=STRATEGIES,
                axis=alt.Axis(labels=False, ticks=False)),
        tooltip='median(apfd)'
    )

    upper_plot = base.mark_rule().encode(
        y=alt.Y(upper_whisker, scale=scale),
        y2=upper_box,
        x=alt.X('strategy', title='', sort=STRATEGIES,
                axis=alt.Axis(labels=False, ticks=False))
    )

    middle_tick = base.mark_tick(
        color='white',
        size=5.
    ).encode(
        y=alt.Y(tick, scale=scale),
        x=alt.X('strategy:O', title='', sort=STRATEGIES,
                axis=alt.Axis(labels=False, ticks=False)),
    )

    return alt.layer(lower_plot,
                     middle_plot,
                     upper_plot,
                     middle_tick)\
        .resolve_scale(x='independent')


def boxplot_filename(project_path):
    return os.path.join(folders.evaluation(project_path), "apfd-boxplot.png")


def save_box_plot(project_name, project_path, df, output_filename=None):
    filename = output_filename or boxplot_filename(project_path)
    chart = apfd_boxplot(boxplot_transform(df), project_name)
    chart.save(filename, scale_factor=2.0)
    LOG.info("Written %s", filename)


def apfd_ridgeline(project_name, df, interpolate=None):

    def plot(strategy_name, df):
        return alt.layer(area(strategy_name), rule(), data=df).transform_window(
            medianAPFD='median(apfd)',
            frame=[None, None]
        )

    def rule():
        return alt.Chart().mark_rule(color='red', strokeDash=[1, 1]).encode(
                x='medianAPFD:Q')

    def area(strategy_name):
        return alt.Chart(title=strategy_name).mark_area().encode(
            x=alt.X('apfd_bin:Q', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('binrelative:Q')
        ).transform_bin(**{'as': 'apfd_bin',
                           'field': 'apfd',
                           'bin': alt.BinParams(step=0.075)}
                        ).transform_aggregate(
            bincount='count(travisJobId)',
            groupby=['apfd_bin']
        ).transform_window(
            binsum='sum(bincount)',
            frame=[None, None]
        ).transform_calculate(
            binrelative='datum.bincount / datum.binsum'
        )

    charts = []
    for strategy in df.columns[1:]:
        strategy_df = df[['travisJobId', strategy]].rename(columns={
            strategy: 'apfd'
        })
        charts.append(plot(strategy, strategy_df))

    chart = alt.vconcat(*charts)\
        .resolve_scale(y='shared')\
        .properties(title=project_name)

    if interpolate:
        return chart.configure_area(interpolate=interpolate)
    return chart


def ridgeline_filename(project_path):
    return os.path.join(folders.evaluation(project_path), "apfd-ridgeline.png")


def save_ridgeline(project_name,
                   project_path,
                   df,
                   output_filename=None,
                   **kwargs):
    filename = output_filename or ridgeline_filename(project_path)
    chart = apfd_ridgeline(project_name, df, **kwargs)
    chart.save(filename, scale_factor=1)
    LOG.info("Written %s", filename)


def read_apfd(project_path, strategies=None):
    df = pd.read_csv(folders.apfd(project_path))
    if strategies:
        columns = ['travisJobId'] + list(strategies)
        return df[columns]
    else:
        return df


def _main(strategies, plot_method):
    logging.basicConfig(level=logging.INFO)
    for project_name, project_path in folders.projects():
        LOG.info('Processing project %s', project_name)
        df = read_apfd(project_path, strategies)
        plot_method(project_name, project_path, df)


def collect_apfd(strategies):
    df = []
    for project_name, project_path in folders.projects():
        df.append(read_apfd(project_path, strategies))
    return pd.concat(df)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('strategies', nargs=-1)
def bars(strategies):
    _main(strategies, save_bar_chart)


@cli.command()
@click.argument('strategies', nargs=-1)
def boxes(strategies):
    _main(strategies, save_box_plot)


@cli.command()
@click.argument('strategies', nargs=-1)
@click.option('--interpolate', help='values from Altair interpolate enum')
def ridgelines(strategies, interpolate):

    def cmd(*args):
        save_ridgeline(*args,
                       interpolate=interpolate)

    _main(strategies, cmd)


@cli.command()
@click.argument('strategies', nargs=-1)
@click.option('--output', required=True)
def combined(strategies, output):
    projects = []
    for project_name, project_path in folders.projects():
        LOG.info("Processing project %s", project_name)
        project_df = read_apfd(project_path, strategies)
        projects.append(project_df)

    df = pd.concat(projects, sort=False)
    LOG.error(output)
    save_box_plot(project_name='',
                  project_path=None,
                  df=df,
                  output_filename=output)


if __name__ == '__main__':
    cli()

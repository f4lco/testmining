# -*- encoding: utf-8 -*-
import abc
import logging
import os

from functools import partial

import click
import tqdm

import altair as alt
import pandas as pd

from testmining import folders
from testmining.apfd import read_tests

LOG = logging.getLogger(__file__)


def from_project(df, selector):
    per_job = df.groupby('travisJobId').apply(partial(from_job, selector=selector))
    result = per_job.median().to_frame().T
    result['selector'] = selector.name()
    result['parameter'] = selector.parameter()
    return result


def from_job(df, selector):
    assert df['travisJobId'].unique().size == 1
    assert (df['index'].diff()[1:] == 1).all()

    selected = selector.select_from(df)
    return pd.Series([
        _precision(selected),
        _recall(selected, df),
    ], index=['precision', 'recall'])


def _precision(selected):
    count = len(selected)
    return len(selected.query('red > 0')) / count if count > 0 else 1


def _recall(selected, all_tests):
    return len(selected.query('red > 0')) / len(all_tests.query('red > 0'))


class Selector(abc.ABC):

    @abc.abstractmethod
    def select_from(self, df):
        pass

    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def parameter(self):
        pass

    @classmethod
    def upper_bound(cls, df):

        def failed_tc(job):
            return len(job.query('red > 0')['testName'].unique())

        return df.groupby('travisJobId').apply(failed_tc).max()


class FixedOffset(Selector):

    def __init__(self, num_tests):
        self.num_tests = num_tests

    def select_from(self, df):
        return df.iloc[:self.num_tests]

    def name(self):
        return 'fixed'

    def parameter(self):
        return self.num_tests


class GreenTests(Selector):

    def __init__(self, num_tests):
        self.num_tests = num_tests

    def select_from(self, df):
        if self.num_tests == 0:
            return df[:0]

        prev_failures = df['red'].rolling(self.num_tests).sum()

        if prev_failures.count() > 0:
            index = (prev_failures == 0).idxmax()
            return df.loc[:index]

        return df

    def name(self):
        return 'green'

    def parameter(self):
        return self.num_tests


def chart(df):
    lines = alt.Chart().mark_line().encode(
        x=alt.X('recall',
                axis=alt.Axis(format='%'), scale=alt.Scale(domain=[0, 1]),
                title='Recall'),

        y=alt.Y('precision',
                axis=alt.Axis(format='%'),
                scale=alt.Scale(domain=[0, 1]),
                title='Precision'),

        color='selector',
    )

    points = alt.Chart().mark_point(filled=True).encode(
        x=alt.X('recall'),
        y=alt.Y('precision'),
        tooltip=['parameter', 'precision', 'recall'],
        color='selector',
    )

    return (lines + points).properties(data=df)


def iterate(df, selectors):
    for selector_cls in selectors:
        bound = selector_cls.upper_bound(df)
        for num_tests in tqdm.trange(0, int(bound) + 1):
            selector = selector_cls(num_tests)
            yield from_project(df, selector)


@click.command()
@click.option('--selectors', '-s', required=True, multiple=True)
@click.option('--strategy', required=True)
def main(selectors, strategy):
    available = {
        'fixed': FixedOffset,
        'green': GreenTests,
    }

    selector_cls = [available.get(name) for name in selectors]
    selector_names = '~'.join(selectors)

    for project_name, project_path in folders.projects():
        LOG.info('Processing %s', project_name)
        df = read_tests(folders.strategy(project_path, strategy))
        result = pd.concat(iterate(df, selector_cls))
        output = os.path.join(folders.evaluation(project_path),
                              f'pr-{strategy}-{selector_names}.png')
        LOG.info('Writing %s', output)
        chart(result).properties(title=project_name).save(output)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

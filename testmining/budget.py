# -*- encoding: utf-8 -*-
import logging
import os

from functools import partial

import click

import altair as alt
import pandas as pd

from testmining import folders
from testmining.apfd import read_tests

LOG = logging.getLogger(__file__)


def red_percent_budget(budget, job):
    faults = job['red'].sum()
    spent = job['duration'].cumsum()
    executed = spent <= budget
    found = job[executed]['red'].sum()
    return (found / faults) * 100


def faults_detected(tests, budget):
    f = partial(red_percent_budget, budget)
    return tests.groupby('travisJobId').apply(f).rename(budget)


def compute_percent_detected(tests):
    available_budgets = allocate_budgets()
    results = [faults_detected(tests, budget) for budget in available_budgets]
    return pd.concat(results, axis=1)


def allocate_budgets():
    return [0.1, 1.0, 10]


def chart(project_name, tests):
    budgets = compute_percent_detected(tests)
    median_budget = budgets.idxmax(axis=1).median()

    df = pd.melt(budgets,
                 var_name='budget',
                 value_name='faultsDetected')

    median = alt.Chart().mark_line().encode(
        x='budget',
        y=alt.Y('median(faultsDetected)', scale=alt.Scale(domain=[0, 100]))
    )

    title = "%s (Median Budget: %.2f)" % (project_name, median_budget)
    return median.properties(data=df, title=title)


def save_chart(project_name, project_path):
    tests = read_tests(folders.strategy(project_path, 'optimal-failure'))
    if (tests['duration'] == 0).any():
        LOG.warning('Project %s has zero durations', project_name)
        tests['duration'].mask(tests['duration'] == 0, 0.25, inplace=True)
    output = os.path.join(folders.evaluation(project_path), 'budget.png')
    chart(project_name, tests).save(output)
    LOG.info('Written %s', output)


@click.group()
def cli():
    pass


@cli.command()
def main():
    logging.basicConfig(level=logging.INFO)
    for project_name, project_path in folders.projects():
        save_chart(project_name, project_path)


@cli.command()
@click.option('--output', required=True)
def combined(output):
    logging.basicConfig(level=logging.INFO)
    frames = []
    for project_name, project_path in folders.projects():
        tests = read_tests(folders.strategy(project_path, 'optimal-failure'))
        budgets = compute_percent_detected(tests)
        df = pd.melt(budgets, var_name='budget', value_name='faultsDetected')
        df['project'] = project_name
        frames.append(df)

    df = pd.concat(frames)
    alt.Chart(df).mark_bar().encode(
        x='budget:O',
        y='mean(faultsDetected):Q',
        column='project:O'
    ).save(output)

    LOG.info('Written %s', output)


if __name__ == '__main__':
    cli()

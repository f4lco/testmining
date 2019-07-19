# -*- encoding: utf-8 -*-
import os
import logging

import click

import pandas as pd

from testmining import folders, apfd_plot


@click.group()
def cli():
    pass


@cli.command()
def compare_push_strategies():
    pattern = "(travisJobId|recently-failed|matrix-file-similarity|push-matrix-file-similarity)"
    for project_name, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path)).filter(regex=pattern)
        output = os.path.join(folders.evaluation(project_path),
                              'push-%s.png' % project_name)
        apfd_plot.save_box_plot('Push Commit Training %s' % project_name,
                                project_path,
                                apfd,
                                output)


@cli.command()
def compare_one_strategy_to_baseline():
    for project_name, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path))[[
            'travisJobId',
            'random',
            'recently-failed',
            'matrix-recently-changed',
        ]]
        output = os.path.join(folders.evaluation(project_path),
                              'matrix-rc-%s.png' % project_name)
        apfd_plot.save_box_plot('Matrix Recently Changed in %s' % project_name,
                                project_path,
                                apfd,
                                output)


@cli.command('offenders')
def offenders_main():
    for project_name, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path))[[
            'travisJobId',
            'recently-failed',
            'matrix-recently-changed',
        ]]
        offenders = pd.read_csv(folders.offenders(project_path))
        mask = apfd['travisJobId'].isin(offenders['tr_job_id'])
        output = os.path.join(folders.evaluation(project_path), 'offenders-%s.png' % project_name)
        apfd_plot.save_box_plot('Offenders in %s' % project_name,
                                project_path,
                                apfd[mask],
                                output)


@cli.command()
@click.option('--output', required=True)
def offenders_combined(output):
    dfs = []
    for _, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path))[[
            'travisJobId',
            'recently-failed',
            'matrix-recently-changed',
        ]]
        offenders = pd.read_csv(folders.offenders(project_path))
        mask = apfd['travisJobId'].isin(offenders['tr_job_id'])
        dfs.append(apfd[mask])

    df = pd.concat(dfs)
    apfd_plot.save_box_plot('Offenders',
                            None,
                            df,
                            output)


@cli.command()
def pull_requests():
    for project_name, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path))[[
            'travisJobId',
            'recently-failed',
            'matrix-recently-changed',
        ]]
        pr = pd.read_csv(folders.pull_requests(project_path))
        mask = apfd['travisJobId'].isin(pr['tr_job_id'])
        output = os.path.join(folders.evaluation(project_path), 'pr-%s.png' % project_name)
        apfd_plot.save_box_plot('PRs in %s' % project_name,
                                project_path,
                                apfd[mask],
                                output)


@cli.command()
@click.option('--output', required=True)
def pull_requests_combined(output):
    dfs = []
    for _, project_path in folders.projects():
        apfd = pd.read_csv(folders.apfd(project_path))[[
            'travisJobId',
            'recently-failed',
            'matrix-recently-changed',
        ]]
        pr = pd.read_csv(folders.pull_requests(project_path))
        mask = apfd['travisJobId'].isin(pr['tr_job_id'])
        dfs.append(apfd[mask])

    df = pd.concat(dfs)
    apfd_plot.save_box_plot('Pull Requests', None, df, output)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()

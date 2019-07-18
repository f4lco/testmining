# -*- encoding: utf-8 -*-
import click
import logging

from collections import OrderedDict

from testmining import loader, cache

KEY_BUILDS = 'builds'


def group_by_build(data):
    return data.groupby('tr_build_id')


def build_statistics(data):
    df = data.copy()

    # Important: count only failures of tests which actually ran
    df['test_failures'] = df['tr_log_bool_tests_ran'] & df['tr_log_bool_tests_failed']

    groups = group_by_build(df)

    aggregations = OrderedDict([

        # Presumably identical for all jobs in this build
        ('tr_build_number', 'first'),
        ('gh_project_name', 'first'),
        ('gh_lang', 'first'),
        ('gh_pull_req_num', 'first'),
        ('gh_is_pr', 'all'),
        ('git_branch', 'first'),
        ('git_all_built_commits', 'sum'),
        ('gh_build_started_at', 'first'),

        # True aggregates
        ('test_failures', 'any'),
        ('tr_duration', 'sum'),
        ('tr_log_testduration', 'sum'),
        ('tr_log_buildduration', 'sum'),
    ])

    return groups.agg(aggregations)


@click.command()
@click.option('-f', '--filename', help='Location of TravisTorrent CSV', required=True)
def main(filename):
    data = loader.read_dump(filename)
    statistics = build_statistics(data)
    cache.write(KEY_BUILDS, statistics)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

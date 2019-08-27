# -*- encoding: utf-8 -*-

"""
Read TravisTorrent CSV, and cache per-project aggregates in the cache.
"""

import logging

import click

import pandas as pd

from testmining import cache, loader

KEY_PROJECTS = 'projects'


def project_names(data):
    """Get a frame of unique project names."""
    names = data['gh_project_name'].unique()
    return pd.DataFrame({'gh_project_name': names})


def group_by_project(data):
    """Partition dataset by project."""
    return data.groupby('gh_project_name')


def jobs(group):
    """How many jobs were submitted for this project?"""
    return group.size


def builds(group):
    """How many builds are associated to this project?"""
    return len(group['tr_build_id'].unique())


def max_test_failures(group):
    """At most, how many tests failed together?"""
    return group['tr_log_num_tests_failed'].max()


def test_failures(group):
    """How many jobs of this project failed?

    Tests which never ran are marked as failure, and should not contribute to failure counts.
    """
    tests_ran = group[group['tr_log_bool_tests_ran']]
    return tests_ran['tr_log_bool_tests_failed'].sum()


def language(group):
    """What is the primary programming language for this project?"""
    languages = group['gh_lang'].unique()
    assert len(languages) == 1, 'Project has multiple programming languages assigned'
    return languages[0]


def average_test_duration(group):
    """On average of all jobs, how long did the tests take?

    May not be very conclusive. Maybe the following answer deviate:
    * For all jobs of this project, how long was the test duration on average? vs
    * For all builds (= aggregated jobs), how long was the test duration on average?"""
    return group['tr_log_testduration'].mean()


def average_duration(group):
    """On average, how long did the tests take per job?

    Same caveats apply as for test_duration."""
    return group['tr_log_buildduration'].mean()


def project_statistics(data):
    groups = group_by_project(data)
    projects = pd.DataFrame({
        'jobs': groups.apply(jobs),
        'builds': groups.apply(builds),
        'max_test_failures': groups.apply(max_test_failures),
        'test_failures': groups.apply(test_failures),
        'gh_lang': groups.apply(language),
        'avg_test_duration': groups.apply(average_test_duration),
        'avg_build_duration': groups.apply(average_duration),
    })

    projects['relative_failed_jobs'] = projects['test_failures'] / projects['jobs']
    return projects


@click.command(help=__doc__)
@click.option('--filename', '-f', required=True)
def main(filename):
    data = loader.read_dump(filename)
    statistics = project_statistics(data)
    cache.write(KEY_PROJECTS, statistics)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

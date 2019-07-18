# -*- encoding: utf-8 -*-
import click

import pandas as pd

from testmining import folders
from testmining.util import connection


def report_simple(project_path):
    df = pd.read_csv(folders.strategy(project_path, 'untreated'))
    tc = len(df[(df['errors'] > 0) | (df['failures'] > 0)]['testName'].unique())
    print('Distinct failing TC %.2f' % tc)


def report_tests(project_name, project_path):
    df = pd.read_csv(folders.strategy(project_path, 'untreated'))
    with connection() as conn:
        jobs = job_count(conn, project_name)
        red = red_job_count(df)
        print('Ratio: %.2f' % (red / float(jobs)))
        #tests(df)
        #failed_count(df)
        #failed_job_count_per_build(conn, project_name)


def red_job_count(df):
    count = df['travisJobId'].unique().size
    print('Red Job count: %d' % count)
    return count


def tests(df):
    test_selectors = df.groupby('travisJobId').agg({'count': 'sum'}).median()
    test_classes = df.groupby('travisJobId').size().median()
    print('%d test classes, yielding %d test methods' % (test_classes, test_selectors))


def failed_count(df):

    def failed(it):
        return ((it.failures > 0) | (it.errors > 0)).sum()

    #print(df.groupby('travisJobId').apply(failed).value_counts())
    failed = df.groupby('travisJobId').apply(failed).median()
    print('Failing TC: %s' % failed)


def failed_job_count_per_build(conn, project_name):
    with conn.cursor() as c:
        c.execute("""
        SELECT AVG(jobs_with_test)
        FROM (
            SELECT tt.tr_build_id, COUNT(tt.tr_job_id) as jobs_with_test
            FROM travistorrent_8_2_2017 tt
            WHERE tt.gh_project_name = %s
            AND EXISTS  (
                SELECT 1 FROM tr_test_result tr
                WHERE tr.tr_job_id = tt.tr_job_id
            )
            GROUP BY tt.tr_build_id
        ) AS build_to_test_jobs
        """, (project_name.replace('@', '/'),))

        avg = next(c)[0]
        print('Average test jobs per build: %f' % avg)


def job_count(conn, project_name):
    with conn.cursor() as c:
        c.execute("""
        SELECT COUNT(tr_job_id)
        FROM travistorrent_8_2_2017
        WHERE gh_project_name = %s
        """, (project_name.replace('@', '/'), ))
        count = next(c)[0]
        print('Job count: %d' % count)
        return count


def report_changesets(project_path):
    df = pd.read_csv(folders.patches(project_path))
    #number_of_commits(df)
    #commit_size(df)
    #commits_dist(df)
    distinct_files(df)


def number_of_commits(df):
    count = df['sha'].unique().size
    print('Number of commits: %d' % count)


def commit_size(df):
    count = df.groupby('sha').size().median()
    print('Avg. files per commit: %d' % count)


def commits_dist(df):
    counts = df.groupby('sha').size().value_counts().sort_index()
    print(counts.head(10))


def distinct_files(df):
    count = df['name'].unique().size
    print('Number of unique files: %d' % count)


@click.command()
def main():
    projects = list(folders.projects())

    def _key(project):
        title, _ = project
        return title.split('@')[1].lower()

    projects.sort(key=_key)

    for project_name, project_path in projects:
        print(project_name)
        report_simple(project_path)
        #report_tests(project_name, project_path)
        #report_changesets(project_path)
        print('-' * 30)


if __name__ == '__main__':
    main()

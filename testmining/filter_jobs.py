# -*- encoding: utf-8 -*-

"""
Given the database, use SQL to extract different types of jobs.

- offenders: the preceding build was green.
- pull requests: this build is part of a pull request.

The queries can be expensive; therefore, store a CSV for use with notebooks.
"""

import logging
import os

import click

import pandas as pd

from testmining.util import connection
from testmining import folders, util

LOG = logging.getLogger(__file__)


@click.group()
def main():
    pass


@main.command('offenders')
def offenders_main():
    with connection() as conn:
        for project_name, project_path in folders.projects():
            offenders = folders.offenders(project_path)
            if not os.path.exists(offenders):
                handle_offenders(conn, project_name, project_path)
            else:
                LOG.warning("Skipped %s", project_name)


def handle_offenders(conn, project_name, project_path):
    LOG.info('Starting offenders query for project %s', project_name)
    jobs = query_offenders(conn, project_name)
    filename = folders.offenders(project_path)
    jobs.to_csv(filename, index=False)
    LOG.info('Written %s', filename)


def query_offenders(conn, project):
    with conn.cursor() as c:
        c.execute("""
        SELECT tt1.tr_job_id FROM travistorrent_8_2_2017 as tt1
        WHERE tt1.gh_project_name = %s
        AND EXISTS (
          SELECT 1 FROM tr_test_result as tr1 
          WHERE tr1.tr_job_id = tt1.tr_job_id
          AND (tr1.failures > 0 OR tr1.errors > 0)
        ) AND NOT EXISTS (
          SELECT 1 FROM travistorrent_8_2_2017 as tt2
          WHERE  tt2.gh_project_name = tt1.gh_project_name
          AND tt1.tr_build_number = tt2.tr_build_number + 1
          AND NOT EXISTS (
            SELECT 1 FROM tr_test_result AS tr2
            WHERE tr2.tr_job_id = tt2.tr_job_id
            AND (tr2.failures > 0 OR tr2.errors > 0)
          )
        );
        """, (util.db_project_name(project),))
        return pd.DataFrame(c.fetchall(), columns=['tr_job_id'])


@main.command()
def pull_requests():
    with connection() as conn:
        for project_name, project_path in folders.projects():
            pr = folders.pull_requests(project_path)
            if not os.path.exists(pr):
                handle_pull_requests(conn, project_name, project_path)
            else:
                LOG.warning("Skipped %s", project_name)


def handle_pull_requests(conn, project_name, project_path):
    LOG.info('Starting pull requests query for project %s', project_name)
    jobs = query_pull_requests(conn, project_name)
    filename = folders.pull_requests(project_path)
    jobs.to_csv(filename, index=False)
    LOG.info('Written %s', filename)


def query_pull_requests(conn, project):
    with conn.cursor() as c:
        c.execute('''
        SELECT tt.tr_job_id FROM travistorrent_8_2_2017 tt
        WHERE tt.gh_is_pr = '1' AND tt.gh_project_name = %s
        AND EXISTS (
          SELECT 1 FROM tr_test_result as tr
          WHERE tr.tr_job_id = tt.tr_job_id
          AND (tr.failures > 0 OR tr.errors > 0)
        )
        ''', (util.db_project_name(project),))
        return pd.DataFrame(c.fetchall(), columns=['tr_job_id'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

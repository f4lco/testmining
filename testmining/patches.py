# -*- encoding: utf-8 -*-

"""
Select subsets of the raw patches table.

This selects a subset of rows (only changelists for selected projects) as well
as a subset of columns (exclude the full diff, for example).
The queries are by intention point queries and *not* a join. According to the
Postgres query plan, point queries show the best index utilization.
Postgres employs a heuristic such as "if query selectivity is below n percent,
sequential scanning is cheaper than using a index". Give raw patches, this
is hindering: the table is quite big, sequential scanning takes several days,
and the index (commit checksums in a tree) already reaches 1 TB in size.
"""

import logging
import os
import sys

import click

import pandas as pd

from tqdm import tqdm
from testmining.util import connection

LOG = logging.getLogger(__file__)


def commits(conn, project):
    with conn.cursor() as c:
        c.execute("""
        SELECT DISTINCT commits.sha
        FROM tr_all_built_commits commits, travistorrent_8_2_2017 tt
        WHERE commits.tr_job_id = tt.tr_job_id
        AND tt.gh_project_name = %s
        """, (project,))

        return [row[0] for row in c.fetchall()]


def patches(conn, commit_ids):
    results = []
    with conn.cursor() as c:
        for commit in tqdm(commit_ids):
            c.execute(
                'SELECT "sha", "name" FROM "raw_patches" WHERE "sha" = %s',
                (commit,))
            results.append(pd.DataFrame(c.fetchall(), columns=['sha', 'name']))

    return pd.concat(results).reset_index(drop=True)


def write_patches(conn, project, output):
    commit_ids = commits(conn, project)
    patch = patches(conn, commit_ids)
    safe_project_name = project.replace('/', '@')
    filename = os.path.join(output, '%s-patches.csv' % safe_project_name)
    patch.to_csv(filename, index=False)
    LOG.info('Written %s', filename)


@click.command(help=__doc__)
@click.option("--output")
def main(output):
    with connection() as conn:
        for line in sys.stdin:
            project = line.strip()
            write_patches(conn, project, output)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

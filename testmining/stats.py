# -*- encoding: utf-8 -*-
import json
import logging
import os

import click

import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)


def process(cache, project_path):
    df = pd.read_csv(folders.apfd(project_path))['travisJobId'].unique()
    rows = []
    for job_id in df:
        m = os.path.join(cache, str(job_id) + ".json")
        if not os.path.exists(m):
            LOG.warning(job_id)
            continue

        with open(m) as fd:
            matrix = json.load(fd)

        tc = set()
        files = set()

        for index in range(0, len(matrix['matrix']), 2):
            key = matrix['matrix'][index]
            tc.add(key['testName'])
            files.add(key['fileName'])

        rows.append((matrix['jobId'], len(files), len(tc)))

    return pd.DataFrame(rows, columns=['travisJobId', 'fileCount', 'testCount'])


@click.command()
@click.option('--cache', required=True)
def main(cache):
    logging.basicConfig(level=logging.INFO)
    values = []
    for project_name, project_path in folders.projects():
        LOG.info('Processing %s', project_name)
        df = process(cache, project_path)
        value = df['testCount'] / df['fileCount']
        values.append(value)
        print(value.median())
    print("Overall median: %f" % pd.concat(values).median())


if __name__ == '__main__':
    main()

# -*- encoding: utf-8 -*-

"""
Compare the similarity of test plans resulting from cost-cognizant and
non-cost-cognizant prioritization using Rank-biased Overlap (RBO).
"""

import logging
import os

import click
import rbo

import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)


def report_rbo(project_path):
    df1 = read_test_names(project_path, 'optimal-failure')
    df1_groups = df1.groupby('travisJobId').groups

    df2 = read_test_names(project_path, 'optimal-failure-duration')
    df2_groups = df2.groupby('travisJobId').groups

    assert df1_groups.keys() == df2_groups.keys()

    result = []
    for job_id in df1_groups.keys():
        series1 = df1.loc[df1_groups[job_id]]['testName'].drop_duplicates()
        series2 = df2.loc[df2_groups[job_id]]['testName'].drop_duplicates()
        rbo_ext = rbo.RankingSimilarity(series1.values, series2.values).rbo_ext()
        result.append([job_id, rbo_ext])

    df = pd.DataFrame(result, columns=['travisJobId', 'rbo'])
    write(df, project_path)
    return df['rbo']


def read_test_names(project_path, strategy):
    cols = ['travisJobId', 'testName']
    return pd.read_csv(folders.strategy(project_path, strategy),
                       usecols=cols)[cols]


def write(df, project_path):
    output = os.path.join(folders.evaluation(project_path), 'rbo.csv')
    df.to_csv(output, index=False)
    #LOG.info('Written %s', output)


@click.command(help=__doc__)
def main():
    rbo_values = []
    for project_name, project_path in folders.projects():
        rbo_value = report_rbo(project_path)
        rbo_values.append(rbo_value)
        print("%-20s %.3f" % (project_name, rbo_value.median()))
    all_rbo = pd.concat(rbo_values)
    #import numpy as np
    #all_rbo.where(all_rbo != 1.0, np.nan, inplace=True)
    print('General Median: %f' % all_rbo.median())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

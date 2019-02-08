# -*- encoding: utf-8 -*-
import click
import logging
import os

import pandas as pd

from testmining import folders, apfd

LOG = logging.getLogger(__file__)


def process_project(project_name, project_folder):
    results = []
    strategies = []
    for name, path in folders.strategies(project_folder):
        strategies.append(name)
        results.append(apfd.from_file(path))
    df = pd.concat(results, axis=1, keys=strategies)
    write(project_name, project_folder, df)


def write(project_name, project_folder, df):
    filename = '%s-apfd.csv' % project_name
    path = os.path.join(folders.evaluation(project_folder), filename)
    df.to_csv(path)
    LOG.info('Written %s', path)


@click.command()
def main():
    logging.basicConfig(level=logging.INFO)
    for name, folder in folders.projects():
        process_project(name, folder)


if __name__ == '__main__':
    main()

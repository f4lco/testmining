# -*- encoding: utf-8 -*-
import click
import numpy as np
import pandas as pd


def read_tests(filename):
    tests = pd.read_csv(filename)
    tests['red'] = tests['failures'] + tests['errors']
    return tests


def apfd_plot(tests):
    assert len(tests['travisJobId'].unique()) == 1
    assert (np.diff(tests['index']) == 1).all()

    def leftpadzero(xs):
        return pd.Series([0]).append(xs)

    executed_sum = leftpadzero(tests['count'].cumsum())
    red_sum = leftpadzero(tests['red'].cumsum())
    return pd.DataFrame({
        'executed': executed_sum / executed_sum.max(),
        'red': red_sum / red_sum.max(),
    })


def apfd(plot):
    return np.trapz(x=plot['executed'], y=plot['red'])


def from_file(filename):
    tests = read_tests(filename)
    jobs = tests.groupby('travisJobId')
    return jobs.apply(lambda job: apfd(apfd_plot(job)))


def file_apfd(filename):
    tests = read_tests(filename)
    return df_apfd(tests)


def df_apfd(tests):
    jobs = tests.groupby('travisJobId')
    return jobs.apply(lambda job: apfd(apfd_plot(job))).median()


@click.command()
@click.argument('filename')
def cli(filename):
    print(file_apfd(filename))


if __name__ == '__main__':
    cli()

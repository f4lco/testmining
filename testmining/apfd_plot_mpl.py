#! -*- encoding: utf-8 -*-
import os
import click
import logging
import matplotlib.pyplot as plt

from matplotlib.ticker import PercentFormatter

from testmining import folders
from testmining.apfd_plot import read_apfd, collect_apfd

LOG = logging.getLogger(__name__)


def save_boxplot(title, df, strategies, filename):
    plt.figure(figsize=(1.5 * len(strategies), 5))
    plt.gcf().set_dpi(800)
    if title:
        plt.title(title)

    plt.boxplot(
        [df[x] for x in strategies],
        labels=labels(strategies, df),
        widths=0.25)

    plt.ylabel('APFD')
    plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1.0))

    plt.savefig(filename,
                bbox_inches='tight')
    plt.clf()


def labels(strategies, df):
    med = df.median()
    formatter = PercentFormatter(xmax=1, decimals=2)

    def shorten(name):
        return name[name.startswith('matrix-') and len('matrix-'):]

    return ["%s\n%s" % (shorten(name), formatter.format_pct(med[name], 1.0))
            for name in strategies]


@click.group()
def cli():
    pass


@cli.command()
@click.argument('strategies', nargs=-1)
def boxplot(strategies):
    for project_name, project_path in folders.projects():
        df = read_apfd(project_path, strategies)
        output = os.path.join(folders.evaluation(project_path), 'boxplot.pdf')
        save_boxplot(project_name, df, strategies, output)


@cli.command()
@click.option('--output', required=True)
@click.argument('strategies', nargs=-1)
def combined(strategies, output):
    df = collect_apfd(strategies)
    save_boxplot(None, df, strategies, output)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()

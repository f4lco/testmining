# -*- encoding: utf-8 -*-

import argparse
import logging
import os

import pandas as pd


logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', help='Location of TravisTorrent CSV', required=True)
    parser.add_argument('-s', '--store', help='Result store', default='output/store.hd5')
    return parser


def exporter(args):
    directory = os.path.dirname(args.store)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        LOG.info("Created directory '%s'", directory)

    def writer(name, df):
        LOG.info("Begin writing DF '%s' to '%s'", name, args.store)
        with pd.HDFStore(args.store) as store:
            store[name] = df
        LOG.info("Completed writing DF '%s' to '%s'", name, args.store)

    return writer

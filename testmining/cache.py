# -*- encoding: utf-8 -*-
import logging
import pandas as pd

from testmining import folders

LOG = logging.getLogger(__file__)

__all__ = [
    'read',
    'write',
]


def read(key):
    filename = folders.cache()
    LOG.info("Reading DF '%s' from '%s'", key, filename)
    with pd.HDFStore(folders.cache()) as store:
        df = store[key]
        LOG.info("Completed reading DF '%s' from '%s'", key, filename)
        return df


def write(key, df):
    filename = folders.cache()
    LOG.info("Begin writing DF '%s' to '%s'", key, filename)
    with pd.HDFStore(filename) as store:
        store[key] = df
    LOG.info("Completed writing DF '%s' to '%s'", key, filename)

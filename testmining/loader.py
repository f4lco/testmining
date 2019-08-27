# -*- encoding: utf-8 -*-

"""
Load the TravisTorrent CSV, and coerce datatypes for certain columns.
"""

import logging

import pandas as pd


MergeMethod = pd.Categorical(values=['merge_button',
                                     'commits_in_master',
                                     'unknown',
                                     'fixes_in_commit'])

DATE_FIELDS = [
    'gh_pr_created_at',
    'gh_first_commit_created_at',
    'gh_pushed_at',
    'gh_build_started_at',
]

DTYPES = {
    'git_merged_with': MergeMethod.dtype,
    'tr_virtual_merged_into': object,  # Commit ID or NaN - raises warning
    'tr_log_bool_tests_failed': float,  # contains NaNs
}

PARSERS = {
    'git_all_built_commits': lambda value: value.split('#'),
}

LOG = logging.getLogger(__name__)


def read_dump(filename):
    LOG.info("Begin reading '%s'", filename)
    jobs = pd.read_csv(filename,
                       engine='c',
                       dtype=DTYPES,
                       parse_dates=DATE_FIELDS,
                       converters=PARSERS)
    LOG.info("Completed reading '%s'", filename)
    return jobs

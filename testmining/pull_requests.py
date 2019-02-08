# -*- encoding: utf-8 -*-
import pandas as pd


def group_by_pull_request(data):
    pull_requests = data['gh_is_pr']
    return data[pull_requests].groupby(['gh_project_name', 'gh_pull_req_num'])


def has_failed_tests(groups):
    """Did any build of this PR fail due to tests?"""
    return groups['tr_log_bool_tests_failed'].any()


def failed_tests(groups):
    """How many builds of this PR failed due to tests?"""
    return groups['tr_log_bool_tests_failed'].sum()


def pull_request_statistics(data):
    groups = group_by_pull_request(data)
    pull_requests = pd.DataFrame({
        'has_failed_tests': has_failed_tests(groups),
        'failed_tests': failed_tests(groups),
        'builds': groups.size(),
    })
    pull_requests['relative_failed_tests'] = pull_requests['failed_tests'] / pull_requests['builds']
    return pull_requests

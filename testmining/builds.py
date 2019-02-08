# -*- encoding: utf-8 -*-
from collections import OrderedDict


def group_by_build(data):
    return data.groupby('tr_build_id')


def build_statistics(data):
    df = data.copy()

    # Important: count only failures of tests which actually ran
    df['test_failures'] = df['tr_log_bool_tests_ran'] & df['tr_log_bool_tests_failed']

    groups = group_by_build(df)

    aggregations = OrderedDict([

        # Presumably identical for all jobs in this build
        ('gh_project_name', 'first'),
        ('gh_lang', 'first'),
        ('gh_pull_req_num', 'first'),
        ('gh_is_pr', 'all'),
        ('git_branch', 'first'),
        ('git_all_built_commits', 'sum'),

        # True aggregates
        ('test_failures', 'any'),
        ('tr_duration', 'sum'),
        ('tr_log_testduration', 'sum'),
        ('tr_log_buildduration', 'sum'),
    ])

    return groups.agg(aggregations)


def main():
    from testmining.loader import read_dump
    from testmining.cli import argument_parser, exporter

    args = argument_parser().parse_args()
    data = read_dump(args.filename)
    statistics = build_statistics(data)
    exporter(args)('builds', statistics)


if __name__ == '__main__':
    main()

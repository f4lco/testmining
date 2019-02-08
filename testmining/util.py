# -*- encoding: utf-8 -*-
import os
import psycopg2
import pandas as pd


def find_files(base_dir, file_regex, converter=str):
    """Find files according to a regex and select the single matched group.

    :param base_dir: The directory in which the files are found (not recursive)
    :param file_regex: The regex (single group)
    :param converter: the conversion function, e.g., `str` or `int` for numerics
    :return: a list of pairs (group, absolute pathname)
    """
    filenames = []
    for f in os.listdir(base_dir):
        match = file_regex.findall(f)
        if match:
            assert len(match) == 1, f
            key = converter(match[0])
            absolute_path = os.path.join(base_dir, f)
            filenames.append((key, absolute_path))
    return filenames


def print_df(df):
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#available-options
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.max_colwidth', -1,
                           'display.width', None):
        print(df)


def connection():
    return psycopg2.connect(host='localhost',
                            port=4242,
                            user='ma',
                            password=os.getenv('PRIO_PW'),
                            database='github')


def db_project_name(project_name):
    """
    Convert project names from filesystem-safe form (without slash) to the
    original GitHub project name, which separates owner and repository with '/'
    """
    return project_name.replace('@', '/')


def fs_project_name(project_name):
    """
    Convert a project name from GitHub to a variant safe for use in file and
    directory names, using '@' as separator.
    """
    return project_name.replace('/', '@')


def strip_prefixes(series, sep):
    """
    Strip common prefixes of strings with a certain delimiter.

    Try to find short names for strings like file paths by assigning the
    filename to the first occurrence of the path. If the filename repeats, but
    the path is different, add more path elements right-to-left to generate a
    unique name. If the same fully qualified path reappears, assign the same
    short name as to its first occurrence.

    Because we do not want new names which only differ in their separator count,
    empty string and strings containing repeated separators will raise
    AssertionError.

    :param series: the Pandas series to treat
    :param sep: the separator, e.g., '/' for paths, '.' for qualified names
    :return: a function suitable for pd.apply
    """
    values = sorted(series.unique(), key=len)
    mapping = {}

    for value in values:
        parts = value.split(sep)
        assert all(parts), parts
        index = len(parts) - 1
        while True:
            assert index >= 0, (value, mapping)
            candidate = sep.join(parts[index:])
            if candidate in mapping.values():
                index -= 1
                continue
            mapping[value] = candidate
            break

    return series.map(mapping)

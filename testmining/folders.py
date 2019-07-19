# -*- encoding: utf-8 -*-
import os
import re
from testmining.util import find_files

ENV_BASE_FOLDER = 'PRIO_BASE'

ENV_QUALIFIER = 'PRIO_QUALIFIER'

STRATEGY_PATTERN = re.compile('^.*@([.\\w-]+).csv$')


def base_folder():
    return os.getenv(ENV_BASE_FOLDER) or '../output'


def qualifier():
    return os.getenv(ENV_QUALIFIER) or 'baseline'


def projects():
    base = base_folder()
    for item in os.listdir(base):
        path = os.path.join(base, item)
        if os.path.isdir(path):
            yield item, path


def strategies(project_path):
    folder = os.path.join(project_path, qualifier())
    return find_files(folder, STRATEGY_PATTERN)


def strategy(project_path, strategy_name):
    repository = _name(project_path).split('@', maxsplit=2)[1]
    filename = '%s@%s.csv' % (repository, strategy_name)
    return os.path.join(project_path, qualifier(), filename)


def evaluation(project_path):
    path = os.path.join(project_path, '%s-evaluation' % qualifier())
    return _ensure_exists(path)


def apfd(project_path):
    project_name = _name(project_path)
    return os.path.join(evaluation(project_path), '%s-apfd.csv' % project_name)


def offenders(project_path):
    project_name = _name(project_path)
    return os.path.join(project_path, '%s-offenders.csv' % project_name)


def pull_requests(project_path):
    project_name = _name(project_path)
    return os.path.join(project_path, '%s-pr.csv' % project_name)


def patches(project_path):
    project_name = _name(project_path)
    return os.path.join(project_path, '%s-patches.csv' % project_name)


def cache():
    return os.path.join(base_folder(), 'cache.hd5')


def _ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _name(project_path):
    return os.path.split(project_path)[1]

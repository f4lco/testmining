# -*- encoding: utf-8 -*-


def kpi(builds, project_name):
    project_builds = builds[builds['gh_project_name'] == project_name]
    return {
        'Number of builds': len(project_builds),
        'Has test failures': project_builds['test_failures'].any(),
    }

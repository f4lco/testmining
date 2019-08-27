# -*- encoding: utf-8 -*-
import pytest

import pandas as pd

from testmining import pr

# pragma pylint: disable=redefined-outer-name


@pytest.fixture()
def one_job():
    return pd.DataFrame([
        (1, 'ATest', 0, 0),
        (1, 'BTest', 1, 1),
        (1, 'CTest', 2, 65),
        (1, 'DTest', 3, 0),
        (1, 'ETest', 3, 0),
        (1, 'FTest', 3, 0),
        (1, 'GTest', 3, 3),
    ], columns=['travisJobId', 'testName', 'index', 'red'])


@pytest.fixture()
def multiple_jobs():
    return pd.DataFrame([
        (1, 'ATest', 0, 0),
        (1, 'BTest', 1, 0),
        (2, 'ATest', 0, 0),
        (2, 'BTest', 1, 65),
    ], columns=['travisJobId', 'testName', 'index', 'red'])


def test_fixed_upper_bound(multiple_jobs):
    bound = pr.FixedOffset.upper_bound(multiple_jobs)

    assert bound == 1


def test_fixed(one_job):
    selector = pr.FixedOffset(1)

    assert len(selector.select_from(one_job)) == 1


def test_green_upper_bound(multiple_jobs):
    bound = pr.GreenTests.upper_bound(multiple_jobs)

    assert bound == 1


def test_green0(one_job):
    selector = pr.GreenTests(0)

    assert len(selector.select_from(one_job)) == 0  # pylint: disable=len-as-condition


def test_green1(one_job):
    selector = pr.GreenTests(1)

    actual = selector.select_from(one_job)

    assert len(actual) == 1


def test_green2(one_job):
    selector = pr.GreenTests(2)

    actual = selector.select_from(one_job)

    assert len(actual) == 5


def test_green3(one_job):
    selector = pr.GreenTests(3)

    actual = selector.select_from(one_job)

    assert len(actual) == 6


def test_green_too_many(one_job):
    selector = pr.GreenTests(500)

    actual = selector.select_from(one_job)

    assert len(actual) == len(one_job)

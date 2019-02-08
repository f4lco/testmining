# -*- encoding: utf-8 -*-
import pandas as pd

from testmining import util


def test_strip_prefixes_with_repetition():
    s = pd.Series([
        'a/b/Foo.java',
        'a/c/Foo.java',
        'a/b/Foo.java',
    ])

    actual = util.strip_prefixes(s, '/')

    assert list(actual) == [
        'Foo.java',
        'c/Foo.java',
        'Foo.java',
    ]


def test_strip_prefixes_ladder_ascending():
    s = pd.Series([
        'Bar',
        'three.Bar',
        'two.three.Bar',
        'one.two.three.Bar',
    ])

    actual = util.strip_prefixes(s, '.')

    assert list(actual) == list(s)


def test_strip_prefixes_ladder_descending():
    s = pd.Series([
        'test.Bar',
        'Bar',
    ])

    actual = util.strip_prefixes(s, '.')

    assert list(actual) == list(s)

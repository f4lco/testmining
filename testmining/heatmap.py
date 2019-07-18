# -*- encoding: utf-8 -*-
import json

import altair as alt
import pandas as pd

from testmining.util import strip_prefixes


def load_json(f):
    with open(f) as fd:
        return json.load(fd)


def json_to_df(j):
    rows = []
    for index in range(0, len(j['matrix']), 2):
        key, value = j['matrix'][index:index+2]
        rows.append((key['fileName'], key['testName'], value))
    df = pd.DataFrame(rows, columns=['fileName', 'testName', 'failureCount'])
    df['shortFileName'] = strip_prefixes(df['fileName'], sep='/')
    df['shortTestName'] = strip_prefixes(df['testName'], sep='.')
    return df


def load_matrix(path, limit):
    df = json_to_df(load_json(path))
    if limit:
        df = df.head(limit)
    return df


def heatmap(path, limit=None):
    return heatmap_chart(load_matrix(path, limit))


def heatmap_chart(df):
    return alt.Chart(df).mark_rect().encode(
      x=alt.X('shortFileName:O', title=''),
      y=alt.Y('shortTestName:O', title=''),
      color=alt.Color('failureCount:Q', scale=alt.Scale(scheme='blues'),
                      title='Failures'))


def bubbly_heatmap(path, limit=None):
    return bubbly_heatmap_chart(load_matrix(path, limit))


def bubbly_heatmap_chart(df):
    return alt.Chart(df).mark_point(filled=True).encode(
      x=alt.X('shortFileName:O', title=''),
      y=alt.Y('shortTestName:O', title=''),
      size='failureCount:Q',
      tooltip=['shortFileName', 'shortTestName', 'failureCount'])

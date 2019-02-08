# -*- encoding: utf-8 -*-
import altair as alt
import vega_datasets


def iris_data():
    return vega_datasets.data.iris()


def make_chart(data):
    return alt.Chart(data).mark_point().encode(
        x='petalLength',
        y='petalWidth',
        color='species')

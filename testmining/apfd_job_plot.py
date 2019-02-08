# -*- encoding: utf-8 -+-

import altair as alt
import pandas as pd

from testmining.apfd import read_tests, apfd_plot, apfd


def job_plot(df, use_title=True):
    assert len(df['travisJobId'].unique()) == 1
    df_plot = apfd_plot(df)
    percent = apfd(df_plot) * 100
    chart = alt.Chart(df_plot).mark_line().encode(

        x=alt.X('executed',
                title='Percentage of Tests Executed',
                axis=alt.Axis(format='%')),

        y=alt.Y('red',
                title='Percentage of Faults Detected',
                axis=alt.Axis(format='%')))

    if use_title:
        return chart.properties(title='APFD: %.0f%%' % percent)
    return chart


def job_plot_test(use_title):
    df = read_tests('../output/square@okhttp/baseline/okhttp@untreated.csv')
    return job_plot(df[df['travisJobId'] == 24460338], use_title)


def distribution(df):

    def plot(df):
        return alt.layer(area(), rule(), data=df).transform_window(
            a='median(apfd)', frame=[None, None])

    def area():
        return alt.Chart().mark_line().encode(

            x=alt.X('apfd_bin:Q',
                    scale=alt.Scale(domain=[0, 1.0]),
                    title='APFD',
                    axis=alt.Axis(format='%')),

            y=alt.Y('binrelative:Q',
                    title='Percentage of Test Sessions',
                    axis=alt.Axis(format='%'))

        ).transform_bin(**{'as': 'apfd_bin',
                           'field': 'apfd',
                           'bin': alt.BinParams(step=0.075)}
                        ).transform_aggregate(
            bincount='count(travisJobId)',
            groupby=['apfd_bin']
        ).transform_window(
            binsum='sum(bincount)',
            frame=[None, None]
        ).transform_calculate(
            binrelative='datum.bincount / datum.binsum'
        )

    def rule():
        return alt.Chart().mark_rule(color='red', strokeDash=[1, 1]).encode(
            x='a:Q')

    return plot(df[['travisJobId', 'untreated']].rename(columns={'untreated': 'apfd'}))


def distribution_test():
    df = pd.read_csv('../output/square@okhttp/experimental-evaluation/square@okhttp-apfd.csv')
    return distribution(df)

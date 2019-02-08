# -*- encoding: utf-8 -*-
import altair as alt
import sys


def setup_notebook():
    # Provision 'testmining' module from parent directory
    sys.path.insert(0, '..')

    # Enable Altair notebook output
    alt.renderers.enable('notebook')

    # Disable Altair Max Row Count
    # Be careful, some data is too large to render in browser. Take care, and
    # truncate unnecessary columns etc, but cutting it at N rows is unreasonable
    alt.data_transformers.enable('default', max_rows=None)

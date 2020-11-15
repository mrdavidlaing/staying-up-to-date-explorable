#%%
from datetime import datetime
from datetime import timedelta
from distutils.version import LooseVersion
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd

from upgrade_model import k8s_releases_loader
from upgrade_model import upgrade_cycle

from app import app
app.set_default_plotly_template()

#%%

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Population metrics"))),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        Assume you develop a Kubernetes distribution and have 100 organisations as customers.

        Let's use the concepts discussed thus far to make some predictions at the population level, including:
        
        * How many clusters should you expect to be running a specific version of Kubernetes in 6 months time?  What about one year?  Two years?
        * How long after a new release should you expect a majority of cluster to be using it?  
        * How many clusters / customers are likely to be running out of support versions in 2 years time?
        ''')
    ])),
    dbc.Card([
        
        dbc.CardBody([
            dbc.Row(
                dbc.Col(dcc.Loading(children=[dcc.Graph(
                    id='graph1',
                    animate=False, #False ensures the axes are redrawn when the graph content changes
                )]), width=12)
            ),
        ])
    ])
])
# %%
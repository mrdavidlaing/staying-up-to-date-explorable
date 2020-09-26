import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Upgrade effort"))),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        [WIP] explain the effort required to upgrade each cluster using the analogy of lifting buckets of water 
        '''),  
        html.Img(src="/assets/upgrade_buckets.png"), 
    ])),
])

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Upgrade cycle"))),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        [WIP] map the upgrade steps to a calendar; showing the impact of various variables 
        '''),  
        html.Img(src="/assets/upgrade_cycle.png"), 
    ])),
])

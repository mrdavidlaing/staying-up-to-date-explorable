#%%
from datetime import datetime
from datetime import timedelta
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly.express as px
import pandas as pd

from upgrade_model import upgrade_cycle
from app import app

def add_weekend_markers(fig, start_date, end_date, fillcolor="LightGray"):
    for day in pd.date_range(start_date, end_date):
        if day.weekday() == 5: # Sat
            fig.add_shape(xref="x", x0=day, x1=day + timedelta(days=2), #highlight the whole weekend
                          yref="paper", y0=0, y1=1,
                          type="rect", fillcolor=fillcolor, opacity=0.5,
                          layer="below", line_width=0,
            )

df_upgrade_steps_single = upgrade_cycle.compute_next_upgrade_cycle(
    start_date = datetime.fromisoformat('2020-01-01'),
    environment_groups = [
        upgrade_cycle.EnvironmentGroup(
        'Group 1',[
            upgrade_cycle.Environment('Cluster 1')
        ])
    ]
)

fig_single = px.timeline(df_upgrade_steps_single, x_start="start_date", x_end="finish_date", y="phase", color="step")
fig_single.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
add_weekend_markers(fig_single, min(df_upgrade_steps_single.start_date), max(df_upgrade_steps_single.finish_date))

def generate_upgrade_steps(environment_groups):
    df_upgrade_steps_many = upgrade_cycle.compute_next_upgrade_cycle(
        start_date = datetime.fromisoformat('2020-01-01'),
        environment_groups = environment_groups
    )

    fig_many = px.timeline(df_upgrade_steps_many, x_start="start_date", x_end="finish_date", y="phase", color="step")
    fig_many.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    add_weekend_markers(fig_many, min(df_upgrade_steps_many.start_date), max(df_upgrade_steps_many.finish_date))

    return fig_many

#%%
layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Upgrade cycle"))),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        [WIP] map the upgrade steps to a calendar; showing the impact of various variables 
        '''),  
        html.Img(src="/assets/upgrade_cycle.png"), 
    ])),
    dbc.Row(
        dbc.Col(dcc.Graph(
            id='upgrade-cycle-single',
            figure=fig_single,
            animate=True,
            animation_options= { 'frame': { 'redraw': True, } },
        ), width=12)
    ),
    dbc.Row([
        dbc.Col([
            html.Label('Start trigger'),
            dcc.Dropdown(
                id="start_trigger",
                options=[
                    {'label': 'Current version nears end-of-support', 'value': '30-days-until-end-of-support'},
                    {'label': 'Current version out-of-support', 'value': 'out-of-support'},
                    {'label': 'New version is released', 'value': 'new_version'},
                ],
                value='30-days-until-end-of-support'
            ),
            html.Label('Chance of pre-work'),
            dcc.Dropdown(
                id="prework_percentage",
                options=[
                    {'label': 'Likely but small', 'value': '80,1'},
                    {'label': 'Unlikely but large', 'value': '20,7'},
                ],
                value='80,1'
            ),
            html.Label('Chance of upgrade failure'),
            dcc.Slider(
                id="upgrade_failure_percent",
                min=10, max=90,
                marks={i: f'{i}%' for i in [10,25,50,75,90]},
                value=25,
            ),
        ], width=5),
        dbc.Col([
            html.Label('Groups'),
            html.Br(),
            html.Label('Clusters / group')
        ], width=2),
        dbc.Col([
            dcc.Input(
                id="environment_groups", type="number", min=1, max=25, value=3,
            ),
            html.Br(),
            dcc.Input(
                id="environments_per_group", type="number", min=1, max=25, value=3,
            ),
        ], width=3)
    ]),
    dbc.Row(
        dbc.Col(dcc.Graph(
            id='upgrade-cycle-many',
            animate=False, #False ensures the axes are redrawn when the graph content changes
        ), width=12)
    ),
])

@app.callback(
    Output(component_id='upgrade-cycle-many', component_property='figure'),
    [
        Input(component_id='environment_groups', component_property='value'),
        Input(component_id='environments_per_group', component_property='value'),
    ]
)
def update_output(environment_group_count, environments_per_group):
    return generate_upgrade_steps(
        environment_groups=[
            upgrade_cycle.EnvironmentGroup(f'Group {i+1}', [
                upgrade_cycle.Environment(f'Cluster {j+1}') for j in range(environments_per_group) 
            ]) for i in range(environment_group_count) 
        ]
    )
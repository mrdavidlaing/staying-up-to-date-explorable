#%%
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from datetime import datetime
from datetime import timedelta

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

df_upgrade_steps_many = upgrade_cycle.compute_next_upgrade_cycle(
    start_date = datetime.fromisoformat('2020-01-01'),
    environment_groups = [
        upgrade_cycle.EnvironmentGroup(
        'Group 1',[
            upgrade_cycle.Environment('Cluster 1'),
            upgrade_cycle.Environment('Cluster 2'),
            upgrade_cycle.Environment('Cluster 3'),
        ]),
        upgrade_cycle.EnvironmentGroup(
        'Group 2',[
            upgrade_cycle.Environment('Cluster 4'),
            upgrade_cycle.Environment('Cluster 5'),
            upgrade_cycle.Environment('Cluster 6'),
        ]),
        upgrade_cycle.EnvironmentGroup(
        'Group 3',[
            upgrade_cycle.Environment('Cluster 7'),
            upgrade_cycle.Environment('Cluster 8'),
            upgrade_cycle.Environment('Cluster 9'),
            upgrade_cycle.Environment('Cluster 10'),
        ]),
    ]
)

fig_many = px.timeline(df_upgrade_steps_many, x_start="start_date", x_end="finish_date", y="phase", color="step")
fig_many.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
add_weekend_markers(fig_many, min(df_upgrade_steps_many.start_date), max(df_upgrade_steps_many.finish_date))

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
    dbc.Row(
        dbc.Col(dcc.Graph(
            id='upgrade-cycle-many',
            figure=fig_many,
            animate=True,
            animation_options= { 'frame': { 'redraw': True, } },
        ), width=12)
    ),
])
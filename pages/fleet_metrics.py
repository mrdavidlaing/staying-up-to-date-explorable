import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from upgrade_model import remain_on_latest
from upgrade_model import k8s_releases_loader

from app import app
app.set_default_plotly_template()

def draw_bucket(fig, x, y):
    fig.add_shape(
        xsizemode="pixel", ysizemode="pixel", 
        xanchor=x, yanchor=y,
        type="path", opacity=0.6,
        path="M 15 30 L 20 10 L 40 10 L 43 30 Z"
    )
    fig.add_shape(
        xsizemode="pixel", ysizemode="pixel", 
        xanchor=x, yanchor=y,
        type="path", fillcolor='rgb(75, 89, 213)', opacity=0.8,
        path="M 19 25 L 23 13 L 37 13 L 39 25 Z"
    )

def add_wip_postit(fig): 
    fig.add_layout_image(
        dict(
            source="/assets/work_in_progress_postit.png",
            xref="x domain", yref="y domain",
            xanchor="left", yanchor="top",
            x=0, y=1,
            sizex=0.4, sizey=0.4,
            # sizing="stretch", opacity=0.5,
            # layer="below",
        )
    )

k8s_releases = k8s_releases_loader.load()
k8s_releases_date_range = pd.date_range(k8s_releases.release_date.min(),k8s_releases.end_of_support_date.max(), freq='1M').to_list()
current_date_slider_marks = { i:d.strftime('%Y-%m') if i%6==0 else "" for i, d in enumerate(k8s_releases_date_range) }

release_age_measurement_figure = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version")
release_age_measurement_figure.add_shape(x0=0.5, y0=0, x1=0.5, y1=1, line=dict(color="Black", width=3), type="line", xref="paper", yref="paper",)
release_age_measurement_figure.update_layout(annotations=[dict(x=0.5, y=1.05, showarrow=False, text="TODAY", xref="paper", yref="paper" )])
release_age_measurement_figure.update_xaxes(range=['2018-05-01','2019-05-01'])
release_age_measurement_figure.update_yaxes(range=[7,9])
release_age_measurement_figure.add_annotation(
    axref='x', ax=k8s_releases.at[8,'release_date'], x=k8s_releases.at[8,'release_date'] + relativedelta(months=+4),
    ayref='y', ay=k8s_releases.at[8,'version'], y=k8s_releases.at[8,'version'],
    showarrow=True, arrowhead=4, arrowsize=2)
release_age_measurement_figure.add_annotation(
    x = k8s_releases.at[8,'release_date'] + relativedelta(months=+2),
    y = k8s_releases.at[8,'version'], yref="y",
    showarrow=True, arrowhead=1, arrowsize=0.3, text="release age = 123 days")
draw_bucket(release_age_measurement_figure, x=k8s_releases.at[8,'release_date'] + relativedelta(months=+4), y=k8s_releases.at[8,'version'])
add_wip_postit(release_age_measurement_figure)

remain_on_latest_env_state = remain_on_latest.compute('remain-on-latest-cluster', start_date=k8s_releases.release_date.min(), end_date=k8s_releases.end_of_support_date.max())
release_age_remain_on_latest_figure = px.line(remain_on_latest_env_state, x="at_date", y="release_age")
add_wip_postit(release_age_remain_on_latest_figure)

layout = html.Div([
    dbc.Row(dbc.Col(html.H1("Fleet Metrics"))),
    dbc.Row(dbc.Col(dcc.Markdown('''
        How can we measure how "far" up/along the support escalator cluster any specific cluster is?
        
        The visulisation below shows two (related) metrics useful for measuring this: 
        
        * Release Age - the number of days between the current date and the release date
        * Days until End Of Support - the number of days until the current version's end of support date

    '''), width="auto")),
    dbc.Card(body=True, children=[
        dbc.Row(
            dbc.Col(dcc.Graph(
                id='release-age-measurement-graph',
                figure = release_age_measurement_figure
            ), width=12)
        ),
    ]),
    dbc.Row(dbc.Col(dcc.Markdown('''
         ## Change over time

        The visualisation below shows how these metrics change over time.  
        
        Notice:

        * How _release age_ increases every day
        * How _days until end of support_ decreases every day
        * The impact of an upgrade on both these measures
        * What happens to _days until end of support_ if a cluster is using a version past its end of support date
        * What happens to _release age_ if a cluster is not upgraded to the latest release
    '''), width="auto")),
    dbc.Card(body=True, children=[
        dbc.Row(children=[
            dbc.Col(dcc.Graph(
                id='release-age-measurement-animated-graph',
                figure = release_age_measurement_figure
            ), width=7),
            dbc.Col(dcc.Graph(
                id='release-age-remain-on-latest-graph',
                figure = release_age_remain_on_latest_figure,
                animate=True,
                animation_options= { 'frame': { 'redraw': True, }, 'transition': { 'duration': 750, 'easing': 'linear', }, },
            ), width=5)
        ]),
        dbc.Row(
            dbc.Col(children=[ dcc.Slider(
                id='release-age-date-slider',
                min=0,
                max=len(k8s_releases_date_range),
                value=6,
                marks=current_date_slider_marks,
                step=None
            ),dcc.Interval(
                id='advance-release-age-date-slider-interval',
                interval=3*1000, # in milliseconds
                n_intervals=6,
                max_intervals=100
            )], width=12)
        ),
    ]),
    
])

@app.callback(Output('release-age-date-slider', 'value'),
              [Input('advance-release-age-date-slider-interval', 'n_intervals')])
def advance_release_age_slider(n_intervals):
    return (n_intervals+1) % len(k8s_releases_date_range)
    
@app.callback(
    Output('release-age-remain-on-latest-graph', 'figure'),
    [Input('release-age-date-slider', 'value')])
def update_release_age_graph(current_mid_date_index):
    mid_date = k8s_releases_date_range[current_mid_date_index]
    fig = go.Figure(release_age_remain_on_latest_figure)
    fig.update_xaxes(range=[mid_date + relativedelta(months=-6), mid_date])
    return fig

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
from upgrade_model import upgrade_every_x_days
from upgrade_model import k8s_releases_loader

from app import app
app.set_default_plotly_template()

def add_wip_postit(fig): 
    fig.add_layout_image(
        dict(
            source="/assets/work_in_progress_postit.png",
            xref="paper", yref="paper",
            xanchor="left", yanchor="top",
            x=0, y=1,
            sizex=0.4, sizey=0.4,
        )
    )

k8s_releases = k8s_releases_loader.load()
env_state = upgrade_every_x_days.compute(
    id='cluster1', 
    start_date='2018-07-01', end_date=k8s_releases.end_of_support_date.max(),
    first_version='1.10.0', 
    upgrade_every=180
)
k8s_releases_date_range = pd.date_range(env_state.at_date.min(),k8s_releases.end_of_support_date.max(), freq='1M').to_list()
current_date_slider_marks = { i:d.strftime('%Y-%m') if i%6==0 else "" for i, d in enumerate(k8s_releases_date_range) }

release_age_measurement_figure = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version")
release_age_measurement_figure.add_shape(x0=0.5, y0=0, x1=0.5, y1=1, line=dict(color="Black", width=3), type="line", xref="paper", yref="paper",)
release_age_measurement_figure.update_layout(annotations=[dict(x=0.5, y=1.05, showarrow=False, text="TODAY", xref="paper", yref="paper" )])
release_age_measurement_figure.update_xaxes(range=['2018-05-01','2019-05-01'])
release_age_measurement_figure.update_yaxes(range=[7,9])
release_age_measurement_figure.add_annotation(
    axref='x', ax=k8s_releases.at[8,'release_date'], x=k8s_releases.at[8,'release_date'] + relativedelta(days=125),
    ayref='y', ay=k8s_releases.at[8,'version'], y=k8s_releases.at[8,'version'],
    showarrow=True, arrowhead=4, arrowsize=2, arrowside='end+start')
release_age_measurement_figure.add_annotation(
    x = k8s_releases.at[8,'release_date'] + relativedelta(months=+2),
    y = k8s_releases.at[8,'version'], yref="y",
    showarrow=True, arrowhead=1, arrowsize=0.3, text="Release Age = 125 days")
release_age_measurement_figure.add_annotation(
    axref='x', ax=k8s_releases.at[8,'end_of_support_date'], x=k8s_releases.at[8,'end_of_support_date'] + relativedelta(days=-145),
    ayref='y', ay=k8s_releases.at[8,'version'], y=k8s_releases.at[8,'version'],
    showarrow=True, arrowhead=4, arrowsize=2, arrowside='end+start')
release_age_measurement_figure.add_annotation(
    x = k8s_releases.at[8,'end_of_support_date'] + relativedelta(months=-2),
    y = k8s_releases.at[8,'version'], yref="y",
    showarrow=True, arrowhead=1, arrowsize=0.3, text="Days until End of Support = 145 days")
add_wip_postit(release_age_measurement_figure)

release_age_remain_on_latest_figure = px.line(
    pd.melt(env_state, id_vars=['at_date'], value_vars=['release_age','days_until_end_of_support']),
    x="at_date", y="value", facet_row="variable"
)
add_wip_postit(release_age_remain_on_latest_figure)

layout = html.Div([
    dbc.Row(dbc.Col(html.H1("Fleet Metrics"))),
    dbc.Row(dbc.Col(dcc.Markdown('''
        How can we measure how "far" up/along the support escalator cluster any specific cluster is?
        
        The visulisation below shows two (related) metrics useful for measuring this: 
        
        * Release Age - the number of days between the current date and the release date
        * Days until End of Support - the number of days until the current version's end of support date

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
        dbc.Row([
            dbc.Col(dcc.Graph(
                id='release-age-measurement-animated-graph',
                figure = release_age_measurement_figure
            ), width=6),
            dbc.Col(dcc.Graph(
                id='release-age-remain-on-latest-graph',
                animate=True,
                animation_options= { 'frame': { 'redraw': True, }, 'transition': { 'duration': 750, 'easing': 'linear', }, },
            ), width=6)
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
    fig.update_layout(
        yaxis = {'range':[-270, 270]}, 
        yaxis2= {'range':[0,540], 'matches': 'y2', }
    )
    return fig

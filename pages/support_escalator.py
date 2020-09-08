import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from upgrade_model import remain_on_latest
from upgrade_model import k8s_releases_loader

from app import app

k8s_releases = k8s_releases_loader.load()
k8s_releases_date_range = pd.date_range(k8s_releases.release_date.min(),k8s_releases.end_of_support_date.max(), freq='1M').to_list()
current_date_slider_marks = { i:d.strftime('%Y-%m') if i%6==0 else "" for i, d in enumerate(k8s_releases_date_range) }

k8s_support_escalator_figure = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version")
k8s_support_escalator_figure.add_shape(x0=0.5, y0=0, x1=0.5, y1=1, line=dict(color="Black", width=3), type="line", xref="paper", yref="paper",)
k8s_support_escalator_figure.update_layout(annotations=[dict(x=0.5, y=1.05, showarrow=False, text="TODAY", xref="paper", yref="paper" )])

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("The support escalator"))),
    dbc.Row(dbc.Col(dcc.Markdown('''
        The Kubernetes project releases a new minor version (with new features) approximately every quarter and follows an N-2 support policy. 
        This means that each minor version (eg; v1.10) is supported until 3 newer versions have been released (eg; v1.13).
        
        The chart visualises the time periods for which each version is supported - plotting horizontal bar for each version starting 
        on the date the version is released and ending when that version is no longer supported.  Each bar stretches over approximately 9 months.

        At any point in time there are 3 versions of Kubernetes which are supported.  This is shown by the intersection of the vertical TODAY line
        and 3 of the horizontal version lines.
    '''), width="auto")),
    dbc.Row(
        dbc.Col(dcc.Graph(
            id='support-escalator-graph',
            animate=True,
            animation_options= { 'frame': { 'redraw': True, }, 'transition': { 'duration': 750, 'easing': 'linear', }, },
        ), width=12)
    ),
    dbc.Row(
        dbc.Col(children=[ dcc.Slider(
            id='current-date-slider',
            min=0,
            max=len(k8s_releases_date_range),
            value=6,
            marks=current_date_slider_marks,
            step=None
        ),dcc.Interval(
            id='advance-current-date-slider-interval',
            interval=3*1000, # in milliseconds
            n_intervals=6,
            max_intervals=100
        )], width=12)
    ),
    dbc.Row(dbc.Col(dcc.Markdown('''
        Time, however, does not stand still - as visualised by the animation of the chart above.  
        
        Every passing month brings the release of the next version closer and - due to the N-2 support policy - 
        so too the end of support for the existing versions.

        The result is what we call the "support escalator".  In the same way that you need to constantly be taking steps up an escalator if you wanted to 
        stay still; so to do you constantly need to be planning and executing your next Kubernetes upgrade is you want to stay running a supported version. 
    '''), width="auto")),
    dbc.Row(children=[
        dbc.Col(html.Br(), width=8),
        dbc.Col(dcc.Link('Measuring where we are using release age...', href='/pages/release_age'), width=4),
    ])
])
   
@app.callback(Output('current-date-slider', 'value'),
            [Input('advance-current-date-slider-interval', 'n_intervals')])
def advance_slider(n_intervals):
    return (n_intervals+1) % len(k8s_releases_date_range)

@app.callback(
    Output('support-escalator-graph', 'figure'),
    [Input('current-date-slider', 'value')])
def update_graph(current_mid_date_index):
    mid_date = k8s_releases_date_range[current_mid_date_index]
    fig = go.Figure(k8s_support_escalator_figure)
    fig.update_xaxes(range=[mid_date + relativedelta(months=-6), mid_date + relativedelta(months=+6)])
    fig.update_yaxes(range=[
        max(0, k8s_releases.set_index('release_date').index.get_loc(mid_date, method='nearest') - 4),
        min(len(k8s_releases), k8s_releases.set_index('end_of_support_date').index.get_loc(mid_date, method='nearest') + 4)
    ])
    return fig
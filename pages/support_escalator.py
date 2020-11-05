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
app.set_default_plotly_template()

k8s_releases = k8s_releases_loader.load()
k8s_releases_date_range = pd.date_range(k8s_releases.release_date.min(),k8s_releases.end_of_support_date.max(), freq='1M').to_list()
current_date_slider_marks = { i:d.strftime('%Y-%m') if i%6==0 else "" for i, d in enumerate(k8s_releases_date_range) }

k8s_support_escalator_figure = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version")
k8s_support_escalator_figure.add_shape(x0=0.5, y0=0, x1=0.5, y1=1, line=dict(color="Black", width=3), type="line", xref="paper", yref="paper",)
k8s_support_escalator_figure.update_layout(
    annotations=[dict(x=0.5, y=1.05, showarrow=False, text="TODAY", xref="paper", yref="paper" )],
    updatemenus=[dict(type="buttons", xanchor="left", yanchor="bottom", x=0.5, y=-0.25,
        buttons=[dict(label="Play", method="animate",
            args=[None, 
            {"frame": {"duration": 30000, 'redraw': True },
            "fromcurrent": True, "transition": {"duration": 30000, "easing": "linear"}}],
        )]
    )],
)
k8s_support_escalator_figure.update_xaxes(range=[
    k8s_releases.release_date.min(),
    k8s_releases.release_date.min() + relativedelta(years=+1)
])
k8s_support_escalator_figure.update_yaxes(range=[0,5])
k8s_support_escalator_figure['frames'] = [go.Frame(layout=go.Layout(
    xaxis=dict(range=[
        k8s_releases.end_of_support_date.max() + relativedelta(years=-1),
        k8s_releases.end_of_support_date.max()
    ]),
    yaxis=dict(range=[
        len(k8s_releases)-6,
        len(k8s_releases)
    ]),
))]

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
    dbc.Card([
        dbc.CardBody([
            dbc.Row(
                dbc.Col(dcc.Graph(
                    id='support-escalator-graph',
                    figure=k8s_support_escalator_figure,
                    animate=True,
                    animation_options= { 'frame': { 'redraw': True, } },
                ), width=12)
            ),
        ]),
        dbc.CardFooter([
            dbc.Row(dbc.Col(children=[
                    html.Blockquote(children=[
                        html.Img(src="/assets/said_the_Red_Queen.png", width=86, height=100, style={"float":"left", "margin-right":"1rem"}),
                        html.P("Now, here, you see, it takes all the running you can do, to keep in the same place.  If you want to get somewhere else, you must run at least twice as fast as that!"),
                        html.Footer("Lewis Carol", className="blockquote-footer")
                    ], className="blockquote"),
                ])
            )
        ])
    ]),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
            Like the [Red Queen asserts to Alice](https://en.wikipedia.org/wiki/Red_Queen_hypothesis), this isn't a static system.  Click Play to observe to how the passing of time impacts the chart above.  

            As you can see, every passing month brings the release of the next version closer and - due to the N-2 support policy - 
            so too the end of support for the existing versions.

            The result is what we call the "support escalator".  In the same way that you need to constantly be taking steps up an escalator if you wanted to 
            stay still; so too do you constantly need to be planning and executing your next Kubernetes upgrade if you want to stay on a supported version. 
        ''')
        ])
    ),
    dbc.Row(dbc.Col(
        dcc.Link('What steps are involved in an upgrade? How long does it take?  Read on...', href='/pages/upgrade_cycle', style={"display":"block", "text-align":"right"})
    ))
])
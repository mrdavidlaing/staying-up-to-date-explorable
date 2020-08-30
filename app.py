import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])

k8s_releases = pd.read_csv("./k8s-releases.csv", parse_dates=['release_date','end_of_support_date'] )

fig = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version")

app.layout = dbc.Container(children=[
    dbc.NavbarSimple(
        children=[],
        brand="Staying up-to-date with Kubernetes",
        brand_href="#",
        # fixed="top",
        color="primary",
        dark=True,
    ),

    html.Div(
        [
            dbc.Row(dbc.Col(html.H1("The support escalator"))),
            dbc.Row(dbc.Col(html.Div(children='''
                Descriptive paragraph here
            '''), width="auto")),
            dbc.Row(
                dbc.Col(dcc.Graph(
                    id='example-graph',
                    figure=fig
                ), width="auto")
            ),
        ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
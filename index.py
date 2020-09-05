import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.io as pio
import plotly.graph_objects as go

from app import app
app.set_default_plotly_template()
server = app.server #underlying Flask server - will be used when running via gunicorn

from pages import support_escalator
from pages import release_age

app.layout = dbc.Container(children=[
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Support Escalator", href="/pages/support_escalator")),
            dbc.NavItem(dbc.NavLink("Release Age", href="/pages/release_age")),
        ],
        brand="Staying up-to-date with Kubernetes",
        brand_href="/",
        sticky="top",
        color="primary",
        dark=True,
    ),
    html.Br(),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pages/support_escalator':
        return support_escalator.layout
    elif pathname == '/pages/release_age':
        return release_age.layout
    else:
        return html.Div([
            dbc.Row(dbc.Col(dcc.Markdown('''
                If you've ever developed a popular software package with multiple releases over a number of years; you may have been dismayed to discover 
                that many of your users "fall behind" and continue to use old versions that you no longer support.

                This [Explorable Explanation](https://explorabl.es/) attempts to explain why...
                '''), width="auto")),
            dbc.Row(children=[
                dbc.Col(html.Br(), width=8),
                dbc.Col(dcc.Link('Get started learning about the support escalator...', href='/pages/support_escalator'), width=4),
            ])
        ])

if __name__ == '__main__':
    app.run_server(debug=True)

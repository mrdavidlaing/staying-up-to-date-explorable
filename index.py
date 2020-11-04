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
from pages import upgrade_effort
from pages import upgrade_cycle
from pages import thanks

app.title = "Staying up-to-date with K8s"

app.layout = dbc.Container(children=[
    dcc.Location(id='url', refresh=False),
    html.Header(dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Support Escalator", href="/pages/support_escalator")),
            dbc.NavItem(dbc.NavLink("Upgrade Cycle", href="/pages/upgrade_cycle")),
            dbc.NavItem(dbc.NavLink("Release Age", href="/pages/release_age")),
            dbc.NavItem(dbc.NavLink("Upgrade Effort", href="/pages/upgrade_effort")),
        ],
        brand="Staying up-to-date with Kubernetes",
        brand_href="/",
        sticky="top",
        color="primary",
        dark=True,
    )),
    html.Br(),
    html.Div(id='page-content'),
    dbc.Container(children=[dcc.Markdown('''
      [Thanks & Credits](/pages/thanks) | Copyright &copy; 2020 [David Laing](https://www.linkedin.com/in/mrdavidlaing/) | 
      [Source code](https://github.com/mrdavidlaing/staying-up-to-date-explorable) licensed under [MIT](https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/LICENSE)
    ''', className="text-muted")], className="footer")
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pages/support_escalator':
        return support_escalator.layout
    elif pathname == '/pages/release_age':
        return release_age.layout
    elif pathname == '/pages/upgrade_effort':
        return upgrade_effort.layout
    elif pathname == '/pages/upgrade_cycle':
        return upgrade_cycle.layout
    elif pathname == '/pages/thanks':
        return thanks.layout
    else:
        return html.Div([
            dcc.Markdown('''
                If you've ever developed a popular software package with multiple releases over a number of years; you may have been dismayed to discover 
                that many of your users "fall behind" and continue to use old versions that you no longer support.

                This [Explorable Explanation](https://explorabl.es/) attempts to explain why...
            '''),
            dcc.Link('Get started learning about the support escalator...', href='/pages/support_escalator', style={"display":"block", "text-align":"right"})
        ])

if __name__ == '__main__':
    app.run_server(debug=True)

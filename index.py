import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.io as pio
import plotly.graph_objects as go

from app import app
app.set_default_plotly_template()
server = app.server #underlying Flask server - will be used when running via gunicorn

from pages import home
from pages import support_escalator
from pages import upgrade_cycle
from pages import fleet_metrics
from pages import thanks

app.title = "Staying up-to-date with K8s"

app.layout = dbc.Container(children=[
    dcc.Location(id='url', refresh=False),
    html.Header(dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Support Escalator", href="/pages/support_escalator")),
            dbc.NavItem(dbc.NavLink("Upgrade Cycle", href="/pages/upgrade_cycle")),
            dbc.NavItem(dbc.NavLink("Fleet Metrics", href="/pages/fleet_metrics")),
        ],
        brand="Staying up-to-date with Kubernetes",
        brand_href="/",
        sticky="top",
        color="primary",
        dark=True,
    )),
    html.Br(),
    html.Div(id='page-content'),
    dbc.Container(children=[dcc.Markdown(id='footer', className="text-muted")], className="footer")
])
def generate_footer_markdown(github_page_ref):
    return f'''
Feedback for this [page]({github_page_ref})/[project](https://github.com/users/mrdavidlaing/projects/1) | 
[Thanks & Credits](/pages/thanks) | Copyright &copy; 2020 [David Laing](https://www.linkedin.com/in/mrdavidlaing/) | 
[Source code](https://github.com/mrdavidlaing/staying-up-to-date-explorable) licensed under [MIT](https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/LICENSE)
    '''

@app.callback([Output('page-content', 'children'),
               Output('footer', 'children')],
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pages/support_escalator':
        return support_escalator.layout, generate_footer_markdown('https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/pages/support_escalator.py')
    elif pathname == '/pages/upgrade_cycle':
        return upgrade_cycle.layout, generate_footer_markdown('https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/pages/upgrade_cycle.py')
    elif pathname == '/pages/fleet_metrics':
        return fleet_metrics.layout, generate_footer_markdown('https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/pages/fleet_metrics.py')
    elif pathname == '/pages/thanks':
        return thanks.layout, generate_footer_markdown('https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/pages/thanks.py')
    else:
        return home.layout, generate_footer_markdown('https://github.com/mrdavidlaing/staying-up-to-date-explorable/blob/main/pages/home.py')

if __name__ == '__main__':
    app.run_server(debug=True)

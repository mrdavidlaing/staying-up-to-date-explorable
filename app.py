import dash
import dash_bootstrap_components as dbc
import plotly.io as pio
import plotly.graph_objects as go

app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.SKETCHY],
    suppress_callback_exceptions=True
)
server = app.server #underlying Flask server - will be used when running via gunicorn

def set_default_plotly_template():
    pio.templates["sketchy"] = go.layout.Template()
    pio.templates["sketchy"].layout = go.Layout(font=dict(family='Neucha, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'))
    pio.templates.default = "ggplot2+sketchy"

app.set_default_plotly_template = set_default_plotly_template
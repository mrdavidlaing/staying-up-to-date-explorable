import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

layout = dbc.Container([
     dcc.Markdown('''
        If you've ever developed a popular software package with multiple releases over a number of years; you may have been dismayed to discover 
        that many of your users "fall behind" and continue to use old versions that you no longer support.

        This [Explorable Explanation](https://explorabl.es/) attempts to explain why...
    '''),
    dcc.Link('Get started learning about the support escalator...', href='/pages/support_escalator', style={"display":"block", "text-align":"right"}) 
])
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Thanks"))),
    dbc.Row(dbc.Col(dcc.Markdown('''
        This explorable wouldn't have existed without the ideas and support of these great people:

        * [Scott Muc](http://scottmuc.com/) - for introducing me to [explorabl.es](https://explorabl.es) and fanning the flames of the idea from its infancy
        * [Marie Cosgrove-Davis](https://www.linkedin.com/in/mariecosgrovedavies/) - for pointing out the similarity between the Support Escalator and the [Red Queen hypothesis](https://en.wikipedia.org/wiki/Red_Queen_hypothesis)
    '''), width="auto")), 
])

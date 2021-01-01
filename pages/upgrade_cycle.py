# %%
from datetime import datetime
from datetime import timedelta
from distutils.version import LooseVersion

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

from app import app
from upgrade_model import k8s_releases_loader
from upgrade_model import upgrade_cycle

app.set_default_plotly_template()

k8s_releases = k8s_releases_loader.load()


def k8s_versions_sorted():
    return sorted(k8s_releases.version, key=lambda v: LooseVersion(v))


def versions_greater_than(version):
    return filter(
        lambda v: LooseVersion(v) > LooseVersion(version),
        k8s_versions_sorted()
    )


def k8s_releases_between(start_version, end_version):
    return filter(
        lambda v: LooseVersion(v) >= LooseVersion(start_version) and LooseVersion(v) <= LooseVersion(end_version),
        k8s_versions_sorted()
    )


def add_weekend_markers(fig, start_date, end_date, fillcolor="LightGray"):
    for day in pd.date_range(start_date, end_date):
        if day.weekday() == 5:  # Sat
            fig.add_shape(xref="x", x0=day, x1=day + timedelta(days=2),  # highlight the whole weekend
                          yref="paper", y0=0, y1=1,
                          type="rect", fillcolor=fillcolor, opacity=0.5,
                          layer="below", line_width=0,
                          )
    return


def generate_upgrade_steps(environment_groups, upgrade_failure_percentage, maintenance_window):
    df_upgrade_steps = upgrade_cycle.compute_next_upgrade_cycle(
        start_date=datetime.fromisoformat('2020-03-01'),
        environment_groups=environment_groups,
        upgrade_failure_percentage=upgrade_failure_percentage,
        maintenance_window=maintenance_window
    )

    fig_upgrade_steps = px.timeline(df_upgrade_steps, x_start="start_date", x_end="finish_date", y="phase", color="step")
    fig_upgrade_steps.update_yaxes(title=None)
    add_weekend_markers(fig_upgrade_steps, df_upgrade_steps.start_date.min(), df_upgrade_steps.finish_date.max())
    cycle_start = df_upgrade_steps.start_date.min()
    cycle_end = df_upgrade_steps.finish_date.max()
    fig_upgrade_steps.update_layout(
        title_text=f"Upgrade cycle: {cycle_start.date()} to {cycle_end.date()} = {(cycle_end - cycle_start).days} days", title_x=0.01,
    )

    return fig_upgrade_steps


# %%

layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Upgrade cycle"))),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        We define an upgrade cycle as the calendar time that passes between when all of an organisation's clusters start running a specific version
        until ALL clusters are upgraded to be running the next version.

        Each cycle contains a set of "global" steps:

        * An "ignore" step - no upgrade activity is considered or performed.  Eventually something will trigger the organisation to start upgrading to the next version - this could be the release of a new version or perhaps 
        the nearing of the end-of-support date for the version being run. 
        * A "planning" step - details about the new version are researched and schedules on when each cluster will be upgraded are drawn up.
        * A "pre-work" step - occasionally some pre-upgrade work will need to be done - often in response to a breaking change or a deprecated feature in the new version

        For each group of clusters the following steps are performed:
        * "waiting" for the next available maintenance window.  For organisations where upgrades are only done over the weekend; this would be the the number of days until the next weekend
        * "upgrading" - the time that passes doing the actual upgrade.  Multiple clusters in the same group are often upgraded in parallel
        * "recovering" - the time it takes to recover from (and re-attempt) a failed upgrade.  High performing organisations typically see upgrade failure rates around 5 - 15%.  Many organisations experience upgrade failure rates in excess of 50%

        The chart below visualises each of these steps:
        ''')
    ])),
    dbc.Card(body=True, children=[
        dbc.Row(
            dbc.Col(dcc.Graph(
                id='upgrade-cycle-single',
                figure=generate_upgrade_steps(
                    environment_groups=[
                        upgrade_cycle.EnvironmentGroup('Test', [
                            upgrade_cycle.Environment('TST-EAST'),
                            upgrade_cycle.Environment('TST-WEST')
                        ]),
                        upgrade_cycle.EnvironmentGroup('Production', [
                            upgrade_cycle.Environment('PROD-EAST'),
                            upgrade_cycle.Environment('PROD-WEST')
                        ])
                    ],
                    upgrade_failure_percentage=0.5,
                    maintenance_window='weekends'
                ),
                animate=True,
                animation_options={'frame': {'redraw': True, }},
            ), width=12)
        ),
    ]),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        ## Impact of different factors

        Change the settings below to visualise the impact of different factors on the length of an upgrade cycle.

        What happens when:
        * The number of groups and clusters changes?
        * The chance of an upgrade failure changes?
        * Maintenance window restrictions are lifted?
        ''')
    ])),
    dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.Table([
                        html.Tr([
                            html.Th([html.Label('Start trigger (TODO)')]),
                            html.Td([dcc.Dropdown(
                                id="start_trigger", style={'width': "18em"},
                                options=[
                                    {'label': 'Current version nears end-of-support', 'value': '30-days-until-end-of-support'},
                                    {'label': 'Current version out-of-support', 'value': 'out-of-support'},
                                    {'label': 'New version is released', 'value': 'new_version'},
                                ],
                                value='30-days-until-end-of-support'
                            )
                            ])
                        ]),
                        html.Tr([
                            html.Th([html.Label('Chance of pre-work (TODO)')]),
                            html.Td([dcc.Dropdown(
                                id="prework_percentage",
                                options=[
                                    {'label': 'Likely but small', 'value': '80,1'},
                                    {'label': 'Unlikely but large', 'value': '20,7'},
                                ],
                                value='80,1'
                            )
                            ])
                        ]),
                        html.Tr([
                            html.Th([html.Label('Maintenance windows')]),
                            html.Td([dcc.Dropdown(
                                id="maintenance_window",
                                options=[
                                    {'label': 'No restrictions', 'value': 'none'},
                                    {'label': 'Weekends', 'value': 'weekends'},
                                ],
                                value='weekends'
                            )
                            ])
                        ]),
                        html.Tr([
                            html.Th([html.Label('Chance of upgrade failure')], colSpan=2),
                        ]),
                        html.Tr([
                            html.Td([dcc.Slider(
                                id="upgrade_failure_percentage",
                                min=10, max=90,
                                marks={i: f'{i}%' for i in [10, 25, 50, 75, 90]},
                                value=25,
                            )
                            ], colSpan=2)
                        ]),
                    ])
                ], width=8),
                dbc.Col([
                    html.Table([
                        html.Tr([
                            html.Th([html.Label('Groups')]),
                            html.Td([dcc.Input(
                                id="environment_groups", type="number", min=1, max=25, value=3, style={'width': '3rem'}, debounce=True,
                            ),
                            ])
                        ]),
                        html.Tr([
                            html.Th([html.Label('Clusters / group')]),
                            html.Td([dcc.Input(
                                id="environments_per_group", type="number", min=1, max=25, value=3, style={'width': '3rem'}, debounce=True,
                            ),
                            ])
                        ]),
                        html.Tr([
                            html.Td([html.Button('Re-calculate', id='recalc-button')], colSpan=2)
                        ])
                    ])
                ], width=4)
            ]),
        ]),
        dbc.CardBody([
            dbc.Row(
                dbc.Col(dcc.Loading(children=[dcc.Graph(
                    id='upgrade-cycle-many',
                    animate=False,  # False ensures the axes are redrawn when the graph content changes
                )]), style={'min-height': '300px'}, width=12)
            )
        ])
    ]),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        ## Staying on the Support Escalator

        As discussed previously; staying up-to-date is a moving target.  As soon as an upgrade-cycle is completed the next cycle begins.

        The visualisation below shows back-to-back upgrade cycles overlayed on the support escalator.

        Can you see:
        * Which clusters were running K8s v1.15.0 past its end of support date?
        ''')
    ])),
    dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.Table([
                        html.Tr([
                            html.Th([html.Label('Start version')]),
                            html.Td([dcc.Dropdown(
                                id="start_version", style={'width': "5em", 'margin-right': '0.75em'},
                                options=[
                                    {'label': version, 'value': version} for version in k8s_versions_sorted()
                                ],
                                value='1.15.0'
                            )
                            ]),
                            html.Th([html.Label('Target version')]),
                            html.Td([dcc.Dropdown(
                                id="target_version", style={'width': "5em", 'margin-right': '0.75em'},
                                options=[
                                    {'label': version, 'value': version} for version in versions_greater_than('1.15.0')
                                ],
                                value='1.18.0'
                            )
                            ]),
                            html.Td([html.Button('Re-calculate', id='recalc-button-with-support-escalator')])
                        ]),
                    ])
                ], width="auto"),
            ]),
        ]),
        dbc.CardBody([
            dbc.Row(
                dbc.Col(dcc.Loading(children=[dcc.Graph(
                    id='upgrade-cycle-many-with-support-escalator',
                    animate=False,  # False ensures the axes are redrawn when the graph content changes
                )]), width=12)
            ),
        ])
    ]),
    dbc.Row(dbc.Col(width="auto", children=[
        dcc.Markdown('''
        As you've just discovered; all the details in the visualisation above makes it difficult to see at a glance 
        "where" each cluster is in relation to the beginning and end of the each release lifecycle.
        
        The [next section](/pages/fleet_metrics) introduces two metrics that help track how 
        "far" up/along the support escalator any specific K8s cluster is.
        ''')
    ])),
])


@app.callback(
    Output(component_id='upgrade-cycle-many', component_property='figure'),
    [
        Input(component_id='environment_groups', component_property='value'),
        Input(component_id='environments_per_group', component_property='value'),
        Input(component_id='upgrade_failure_percentage', component_property='value'),
        Input(component_id='maintenance_window', component_property='value'),
        Input(component_id='recalc-button', component_property='n_clicks'),
    ]
)
def update_output(environment_group_count, environments_per_group, upgrade_failure_percentage, maintenance_window, recalc_counter):
    return generate_upgrade_steps(
        environment_groups=[
            upgrade_cycle.EnvironmentGroup(f'Group {i + 1}', [
                upgrade_cycle.Environment(f'Cluster {(i) * environments_per_group + (j + 1)}') for j in range(environments_per_group)
            ]) for i in range(environment_group_count)
        ],
        upgrade_failure_percentage=upgrade_failure_percentage / 100,
        maintenance_window=maintenance_window
    )


# EXPERIMENTAL: This visualisation might be a bit busy
def generate_upgrade_steps_with_support_elevator(start_date, start_version, target_version, environment_groups, upgrade_failure_percentage,
                                                 maintenance_window):
    df_upgrade_steps = pd.DataFrame()
    next_start_date = start_date
    upgrade_version_sequence = list(k8s_releases_between(start_version, target_version))

    for current_version, next_version in zip(upgrade_version_sequence, upgrade_version_sequence[1:]):  # loops through version pairs
        df_next_upgrade_steps = upgrade_cycle.compute_next_upgrade_cycle(
            start_date=next_start_date,
            environment_groups=environment_groups,
            upgrade_failure_percentage=upgrade_failure_percentage,
            maintenance_window=maintenance_window
        )
        df_next_upgrade_steps.phase = f"{current_version} -> {next_version}: " + df_next_upgrade_steps.phase
        df_upgrade_steps = pd.concat([df_upgrade_steps, df_next_upgrade_steps], sort=False)
        next_start_date = df_upgrade_steps.finish_date.max()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig_upgrade_steps = px.timeline(
        df_upgrade_steps, x_start="start_date", x_end="finish_date", y="phase", color="step"
    )
    fig_support_escalator = px.timeline(k8s_releases, x_start="release_date", x_end="end_of_support_date", y="version",
                                        color_discrete_sequence=["LightGray"], opacity=0.5)

    fig_upgrade_steps.update_traces(yaxis="y2")
    fig.add_traces(fig_upgrade_steps.data + fig_support_escalator.data)
    add_weekend_markers(fig, df_upgrade_steps.start_date.min(), df_upgrade_steps.finish_date.max())
    fig.update_layout(fig_upgrade_steps.layout)

    fig.update_xaxes(range=[
        df_upgrade_steps.start_date.min() - timedelta(days=7),
        df_upgrade_steps.finish_date.max() + timedelta(days=7)
    ])
    # Format the (left) upgrade steps axis
    fig.update_yaxes(
        secondary_y=True, side='left',
        categoryorder='array', categoryarray=df_upgrade_steps.phase.unique().tolist()
    )
    # Format the (right) support escalator axis
    fig.update_yaxes(secondary_y=False, side='right', visible=False, range=[
        k8s_releases.version[k8s_releases.version == start_version].index[0],
        k8s_releases.version[k8s_releases.version == target_version].index[0],
    ])

    cycle_start = df_upgrade_steps.start_date.min()
    cycle_end = df_upgrade_steps.finish_date.max()
    fig.update_layout(
        title_text=f"{start_version} -> {target_version}: ({cycle_start.date()} to {cycle_end.date()}) = {(cycle_end - cycle_start).days} days",
        title_x=0.01,
        height=700,
    )

    return fig


@app.callback(
    Output(component_id='target_version', component_property='options'),
    [
        Input(component_id='start_version', component_property='value'),
    ]
)
def update_target_version_dropdown(start_version):
    if not start_version:
        raise PreventUpdate

    return [
        {'label': version, 'value': version} for version in versions_greater_than(start_version)
    ]


@app.callback(
    Output(component_id='upgrade-cycle-many-with-support-escalator', component_property='figure'),
    [
        Input(component_id='environment_groups', component_property='value'),
        Input(component_id='environments_per_group', component_property='value'),
        Input(component_id='upgrade_failure_percentage', component_property='value'),
        Input(component_id='maintenance_window', component_property='value'),
        Input(component_id='start_version', component_property='value'),
        Input(component_id='target_version', component_property='value'),
        Input(component_id='recalc-button-with-support-escalator', component_property='n_clicks'),
    ]
)
def update_output_with_support_escalator(environment_group_count, environments_per_group, upgrade_failure_percentage, maintenance_window,
                                         start_version, target_version, recalc_counter):
    if 'recalc-button-with-support-escalator' not in [p['prop_id'] for p in dash.callback_context.triggered][0]:
        raise PreventUpdate

    return generate_upgrade_steps_with_support_elevator(
        start_date=datetime.fromisoformat('2020-03-01'),
        start_version=start_version,
        target_version=target_version,
        environment_groups=[
            upgrade_cycle.EnvironmentGroup(f'Group {i + 1}', [
                upgrade_cycle.Environment(f'Cluster {(i) * environments_per_group + (j + 1)}') for j in range(environments_per_group)
            ]) for i in range(environment_group_count)
        ],
        upgrade_failure_percentage=upgrade_failure_percentage / 100,
        maintenance_window=maintenance_window
    )
# %%

import os
from dash.development.base_component import _check_if_has_indexable_children
from dash_bootstrap_components._components.Card import Card
from dash_bootstrap_components._components.Col import Col
from dash_bootstrap_components._components.Row import Row
from dash_bootstrap_components._components.Spinner import Spinner
from dash_html_components.Div import Div
from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import psycopg2
from psycopg2.extras import RealDictCursor
from app.dashapp.sensors import JSONS, Database

axis_color = {"dark": "#EBF0F8", "light": "#506784"}
marker_color = {"dark": "#f2f5fa", "light": "#2a3f5f"}


PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


def get_navbar():
    return dbc.Navbar(
        dbc.Container(
            fluid=True,
            children=
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                            dbc.Col(dbc.NavbarBrand("Badanie częstości łączeń silnika", className="ml-2")),
                        ],
                        align="center",
                        no_gutters=False,
                    ),
                    href="/",
                ),
                dbc.NavbarToggler(id="navbar-toggler2"),
                dbc.Collapse(
                    dbc.Nav(
                        [dbc.NavItem(dbc.NavLink("Home", href="/")),
                         dbc.NavItem(dbc.NavLink("History", href="/history"))],
                        className="ml-auto", navbar=True
                    ),
                    id="navbar-collapse2",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-5",
    )

###################### HOME ############################
def test_info():
    return dbc.Row([
            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        html.H5("Test ID"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(id="test-id"),
                    )
                )
            ]),
            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        html.H5("Started"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(id="test-started"),
                    )
                )
            ]),
            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        html.H5("Finished"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(id="test-finished"),
                    )
                )
            ]),
            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        html.H5("Terminated"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(id="test-status"),
                    )
                )
            ]),
        ])

def onoff_setting_div():
    return dbc.Card(
        className="onoff-settings-tab",
        children=[
            dbc.Col(
                className="Title",
                children=[
                    html.H3(
                        "Power", id="power-title"
                    ),
                    dbc.Row(
                        className="onoff-buttons",
                        children=[
                            dbc.Col(
                                lg=4,
                                xs=12,
                                children=[
                                    dbc.Row(
                                        dbc.Col(
                                            daq.LEDDisplay(
                                                id='testno',
                                                size=20,
                                                label="Test No",
                                                labelPosition="top",
                                            )
                                        )
                                    )
                                ]),
                            dbc.Col(
                                lg=4,
                                xs=6,
                                children=[
                                    dbc.Row(
                                        dbc.Col(
                                            daq.Indicator(
                                                id='running-indicator',
                                                label="Running",
                                                color="#FFB5B5"
                                            )
                                        )
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Button('START',
                                                       id='start',
                                                       color="warning",
                                                       size="sm",
                                                       block=True
                                                       )
                                        )
                                    )
                            ]),
                            dbc.Col(
                                lg=4,
                                xs=6,
                                children=[
                                    dbc.Row(
                                        dbc.Col(
                                            daq.Indicator(
                                                id='stoped',
                                                label="Stoped",
                                                color="#FFB5B5"
                                            )
                                        )
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Button('STOP',
                                                       id='stop',
                                                       color="danger",
                                                       size="sm",
                                                       block=True
                                                       )
                                        )
                                    )
                                ])
                        ])
                ])
        ]
    )

def time_setting_div(timenow):
    return dbc.Card(
        className="time-settings-tab",
        children=[
            dbc.Col(
                className="Title",
                children=[html.H3(
                    "Time", id="time-title"
                ),
                    dbc.Row(
                    className="timeset-buttons",
                    children=[
                        dbc.Col([
                            dbc.Row(
                                dbc.Col(
                                    daq.LEDDisplay(
                                        id='timeconf-knob-output',
                                        value=timenow,
                                        size=15,
                                        label="Test duration",
                                        labelPosition="top",
                                        className="led-displays"
                                    )
                                )
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Input(
                                        id="time-input",
                                        value=timenow,
                                        min=0,
                                        max=59,
                                        step=1,
                                        type="time",
                                        className="time-inputs",
                                    )

                                )
                            )
                        ]),
                        dbc.Col([
                            dbc.Row(
                                dbc.Col(
                                    daq.LEDDisplay(
                                        id='testtime-now',
                                        value="0:00:00",
                                        size=20,
                                        label="Test now",
                                        labelPosition="top",
                                    )
                                )
                            ),
                            dbc.Row(
                                dbc.Button(                               
                                    [dbc.Spinner(size="sm")],
                                    id='output',
                                    color="primary",
                                    disabled=True,
                                    block=True
                                )
                            )
                        ]
                        )
                    ]
                )
            ])
        ]
    )

def connections_setting_div(onconf, offconf):
    return dbc.Card(
        className="connections-settings-tab",
        children=[
            dbc.Col(
                children=[html.H3("Function", id="connections-title"),
                    dbc.Row(
                    className="connections-buttons",
                    children=[
                        dbc.Col(
                            xs=6,
                            children=[
                                dbc.Row(
                                    dbc.Col(
                                        daq.Knob(
                                            value=onconf,
                                            id="onconf-input",
                                            label="ON Config (s)",
                                            labelPosition="bottom",
                                            size=90,
                                            max=10,
                                            min=0.1,
                                        )
                                    )
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        daq.LEDDisplay(
                                            id="onconf-display",
                                            size=15,
                                            value=onconf,
                                            label="ON Config (s)",
                                            labelPosition="bottom",
                                        )
                                    )
                                )
                            ]),
                        dbc.Col(
                            xs=6,
                            children=[
                                dbc.Row(
                                    dbc.Col(
                                        daq.Knob(
                                            value=offconf,
                                            id="offconf-input",
                                            label="OFF Config (s)",
                                            labelPosition="bottom",
                                            size=90,
                                            max=10,
                                            min=0.1,
                                        )
                                    )
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        daq.LEDDisplay(
                                            id="offconf-display",
                                            size=15,
                                            value=offconf,
                                            label="OFF Config (s)",
                                            labelPosition="bottom",
                                        )
                                    )
                                )
                            ])
                    ]
                )
                ])
        ]
    )

def home():
    data = JSONS().readconfjson()
    onconf = data['onconf']
    offconf = data['offconf']
    timenow = data['timeconf']
    return dbc.Row(
        children=[
            # LEFT PANEL - TEST SETTINGS
            dbc.Col(
                className="left-panel",
                md=4,
                xs=12,
                children=[
                    onoff_setting_div(),
                    time_setting_div(timenow),
                    connections_setting_div(onconf, offconf),
                ],
            ),
            # RIGHT PANEL - TEST INFO
            dbc.Col(
                className="right-panel",
                md=8,
                xs=12,
                children=[
                    dbc.Card(
                        children=[
                        dbc.Col(html.H3("Test info", id="test-title")),
                        test_info(),
                        dbc.Col(html.H3("Graph", id="graph-title")),
                        dbc.Row(
                        className="right-panel-graph",
                        children=[dbc.Col(id="time_series_chart_col_now"),
                        dcc.Interval(id='interval', interval=500),
                        ],
                        ),
                    ])
                ],
            ),
        ]
    ),

##################### HISTORY #########################
def get_sensor_types():
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            id || ' - Started: ' || to_char(started, 'DD-MM-YYYY HH24:MI:SS') as label,
            id as value
        FROM tests
        ORDER BY id DESC;
    """
    with Database() as db:
        types = db.query(sql)
        db.close
        return types

def history():
    types = get_sensor_types()
    return dbc.Row(
        className="history",
        children=[
            dbc.Col([
                html.H3("Graph", id="graph-title"),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                                id='demo-dropdown',
                                options=types,
                                value=types[0]["value"]
                            )
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Spinner(
                            spinner_style={"width": "30rem", "height": "30rem"},
                            color="success",
                            type="border",
                            children=[
                                html.Div(id="dd-output-container"),
                                html.Div(id="time_series_chart_col"),
                            ]
                        )
                    )
                ]),
            ])
        ]
    )

###################### MAIN ###########################
def get_layout():
    """Function to get Dash's "HTML" layout"""

    return dbc.Container(
                fluid=True,
                className="main",
                    children=[
                    dcc.Location(id='url', refresh=False),
                    get_navbar(),
                    dbc.Col(
                        id='page-content')
                    ])

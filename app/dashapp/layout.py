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
from app.dashapp.sensors import Database
import redis


r=redis.Redis()

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
                            dbc.Col(dbc.NavbarBrand("Badanie czestosci laczen silnika", className="ml-2")),
                        ],
                        align="center",
                        no_gutters=False,
                    ),
                    href="/",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [dbc.NavItem(dbc.NavLink("Home", href="/")),
                         dbc.NavItem(dbc.NavLink("History", href="/history"))],
                        className="ml-auto flex-nowrap mt-3 mt-md-0", navbar=True
                    ),
                    id="navbar-collapse",
                    navbar=True
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
                        html.Div(id="test-id", className="test-info"),
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
                        html.Div(id="test-started", className="test-info"),
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
                        html.Div(id="test-finished", className="test-info"),
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
                        html.Div(id="test-status", className="test-info"),
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
                            dbc.Row(html.Div(id='output', className='hidden')),
                            dbc.Row(html.Div(id='pidout', className='hidden')),
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

def time_setting_div(timenow, pidstatus):
    if pidstatus == 1:
        pid = True
    elif pidstatus == 0:
        pid = False
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
                            dbc.Row(className="center",
                                    children=daq.ToggleSwitch(
                                        id='autopid',
                                        value=pid,
                                        label="Auto"
                                    )
                            )
                        ]
                        )
                    ]
                )
            ])
        ]
    )

def connections_setting_div(onconf, offconf, maxtemp):
    return dbc.Card(
        className="connections-settings-tab",
        children=[
            dbc.Col(
                children=[html.H3("Function", id="connections-title"),
                    dbc.Row(
                    className="connections-buttons",
                    children=[
                        dbc.Col(
                            xs=4,
                            children=[
                                dbc.Row(
                                    dbc.Col(className="centerslider",
                                    children=daq.Slider(
                                            value=onconf,
                                            id="onconf-input",
                                            # label="ON Config (s)",
                                            # labelPosition="bottom",
                                            size=160,
                                            max=10,
                                            min=0.05,
                                            # scale={'start':0.05, 'labelInterval': 5, 'interval': 1}
                                            step=0.01,
                                            vertical=True,
                                            updatemode="drag",
                                            marks={i: '{}'.format(1.0 * i) for i in range(11)},
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
                            xs=4,
                            children=[
                                dbc.Row(
                                    dbc.Col(className="centerslider",
                                    children=daq.Slider(
                                            value=offconf,
                                            id="offconf-input",
                                            # label="OFF Config (s)",
                                            # labelPosition="bottom",
                                            size=160,
                                            max=10,
                                            min=0.05,
                                            # scale={'start':0.05, 'labelInterval': 5, 'interval': 1}
                                            step=0.01,
                                            vertical=True,
                                            updatemode="drag",
                                            marks={i: '{}'.format(1.0 * i) for i in range(11)},

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
                            ]),
                            dbc.Col(
                            xs=4,
                            children=[
                                dbc.Row(
                                    dbc.Col(className="centerslider",
                                    children=daq.Slider(
                                            value=maxtemp,
                                            id="maxtemp-input",
                                            # label="Max temp (C)",
                                            # labelPosition="bottom",
                                            size=160,
                                            min=20,
                                            max=100,
                                            # scale={'start':20, 'labelInterval': 10, 'interval': 10}
                                            step=0.1,
                                            vertical=True,
                                            updatemode="mouseup",
                                            marks={
                                                20: {'label': '20°C', 'style': {'color': '#77b0b1'}},
                                                30: {'label': '30°C', 'style': {'color': '#77b0b1'}},
                                                40: {'label': '40°C'},
                                                50: {'label': '50°C'},
                                                60: {'label': '60°C', 'style': {'color': '#ffd000'}},
                                                70: {'label': '70°C', 'style': {'color': '#ffd000'}},
                                                80: {'label': '80°C', 'style': {'color': '#ffd000'}},
                                                90: {'label': '90°C', 'style': {'color': '#f50'}},
                                                100: {'label': '100°C', 'style': {'color': '#f50'}},
                                                },

                                        )
                                    )
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        daq.LEDDisplay(
                                            id="maxtemp-display",
                                            size=15,
                                            value=offconf,
                                            label="Max Temp (C)",
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
    onconf = float(r.get("onconf").decode())
    offconf = float(r.get("offconf").decode())
    maxtemp = float(r.get("maxtemp").decode())
    timenow = str(r.get("timeconf").decode())
    pidstatus = int(r.get("autopid").decode())
    return dbc.Row(
        children=[
            # LEFT PANEL - TEST SETTINGS
            dbc.Col(
                className="left-panel",
                md=4,
                xs=12,
                children=[
                    onoff_setting_div(),
                    time_setting_div(timenow, pidstatus),
                    connections_setting_div(onconf, offconf, maxtemp),
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
                        dcc.Interval(id='interval', interval=1000),
                        ],
                        ),
                    ])
                ],
            ),
        ]
    ),

##################### HISTORY #########################
def get_sensor_datas():
    sql = """
        SELECT 
            distinct 
            id || ' - Started: ' || to_char(started, 'DD-MM-YYYY HH24:MI:SS') || ' - Finished: ' || to_char(finished, 'DD-MM-YYYY HH24:MI:SS')as label,
            id as value
        FROM tests
        ORDER BY id DESC;
    """
    with Database() as db:
        types = db.query(sql)
        db.close
        return types

def history():
    types = get_sensor_datas()
    return dbc.Row(
        className="history",
        children=[
            dbc.Col([
                html.H3("Graph", id="graph-title"),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                                id='history-dropdown',
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
                                dbc.Row(id="time_series_chart_col"),
                            ]
                        )
                    )
                ]),
            ])
        ]
    )

###################### MAIN ###########################
def get_layout():
    return dbc.Container(
                fluid=True,
                className="main",
                    children=[
                    dcc.Location(id='url', refresh=False),
                    get_navbar(),
                    dbc.Col(
                        id='page-content')
                    ])

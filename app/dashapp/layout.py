import os
from dash_bootstrap_components._components.Col import Col
from dash_bootstrap_components._components.Row import Row
from dash_html_components.Div import Div
from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import psycopg2
from psycopg2.extras import RealDictCursor
from app.dashapp.sensors import JSONS, Database
from dash_daq import DarkThemeProvider

axis_color = {"dark": "#EBF0F8", "light": "#506784"}
marker_color = {"dark": "#f2f5fa", "light": "#2a3f5f"}

theme = {
    "dark": False,
    "primary": "#447EFF",
    "secondary": "#D3D3D3",
    "detail": "#D3D3D3",
    }
    
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


def get_sensor_types():
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            id as label,
            id as value
        FROM tests
        ORDER BY id DESC;
    """
    with Database() as db:
        types = db.query(sql)
        db.close 
        return types

def get_navbar():
    return dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Logo", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://plot.ly",
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

def test_info():
    return html.Div(
        children=[

            html.Table([
                html.Tr([
                    html.Th("Started:"),
                    html.Th("Finished:"),
                    html.Th("Terminated:"),
                ]),
                html.Tr([
                    html.Td(id="test-started"),
                    html.Td(id="test-finished"),
                    html.Td(id="test-status"),
                ]),
            ]),
        ],
    )


###################################################                
def niepotrzebne():
    return html.Div([
                html.Div(id='output'),
                html.Div(id='placeholder'),
    ])
###################################################                




def onoff_setting_div(testno):
    return dbc.Row(
        className="onoff-settings-tab",
        children=[
            # Title
            dbc.Col(
                className="Title",
                children=[html.H3(
                    "Power", id="power-title", style={"color": theme["primary"]}
                ),
            # Power Controllers
            dbc.Row(children=
                [
                    dbc.Col(
                        dbc.Row([
                            dbc.Col(
                                daq.LEDDisplay(
                                    id='testno',
                                    value=testno,
                                    size=10,
                                    label="Test No",
                                    labelPosition="top",
                                    color=theme["primary"],
                                    ),
                            )
                        ])
                    ),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(
                                daq.Indicator(
                                    id='my-indicator',
                                    label="Running",
                                    )
                            ),
                        ]),
                        dbc.Row([
                            dbc.Col(
                                daq.StopButton(
                                    buttonText='start',
                                    id='start',
                                    )
                            ),
                        ]),
                    ]),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(
                                daq.Indicator(
                                    id='stoped',
                                    label="Stoped",
                                    )
                            ),
                        ]),
                        dbc.Row([
                            dbc.Col(
                                daq.StopButton(
                                    buttonText='stop',
                                    id='stop',
                                    )
                            ),
                        ]),
                    ]),
                ],
            ),
        ]),
        ],
    )


def time_setting_div(timenow, h,m,s):
    return dbc.Row(
        className="time-settings-tab",
        children=[
            # Title
            dbc.Col(
                className="Title",
                children=[html.H3(
                    "Time", id="time-title", style={"color": theme["primary"]}
                ),
            # Power Controllers
            dbc.Row(
                children=[
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                daq.LEDDisplay(
                                    id='timeconf-knob-output',
                                    value=timenow,
                                    size=15,
                                    label="Test duration",
                                    labelPosition="top",
                                    color=theme["primary"],
                                    className="led-displays"
                                    ),
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                daq.NumericInput(
                                    id="hours-input",
                                    value=h,
                                    min=0,
                                    max=24,
                                    className="time-inputs",
                                    ),
                            ]),
                            dbc.Col([
                                daq.NumericInput(
                                    id="minutes-input",
                                    value=m,
                                    min=0,
                                    max=59,
                                    className="time-inputs",
                                    ),

                            ]),
                            dbc.Col([
                                daq.NumericInput(
                                    id="seconds-input",
                                    value=s,
                                    min=0,
                                    max=59,
                                    className="time-inputs",
                                    ),
                            ]),
                        ]),
                    ]),
                    dbc.Col(
                        dbc.Row([
                            dbc.Col([
                                daq.LEDDisplay(
                                    id='testtime-now',
                                    value="0:00:00",
                                    size=15,
                                    label="Test now",
                                    labelPosition="top",
                                    color=theme["primary"],
                                    className="four columns"
                                    ),
                            ]),
                        ])
                    ),
                ],
            ),
        ]),
        ],
    )



def connections_setting_div(onconf, offconf):
    return dbc.Row(
        className="row connections-settings-tab",
        children=[
            dbc.Col(
                className="Title",
                children=[html.H3(
                    "Function", id="function-title", style={"color": theme["primary"]}
                    ),
            dbc.Row(className="confiigtime-buttons",
                children=[
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                daq.Knob(
                                    value=onconf,
                                    id="onconf-input",
                                    label="ON Config (s)",
                                    labelPosition="bottom",
                                    size=50,
                                    color=theme["primary"],
                                    max=10,
                                    min=0.1,
                                    style={"backgroundColor": "transparent"},
                                    className="five columns",
                                ),
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                daq.LEDDisplay(
                                    id="onconf-display",
                                    size=10,
                                    value=onconf,
                                    label="ON Config (s)",
                                    labelPosition="bottom",
                                    color=theme["primary"],
                                    className="five columns",
                                ),
                            ]),
                        ]),
                    ]),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                daq.Knob(
                                    value=offconf,
                                    id="offconf-input",
                                    label="OFF Config (s)",
                                    labelPosition="bottom",
                                    size=50,
                                    color=theme["primary"],
                                    max=10,
                                    min=0.1,
                                    className="five columns",
                                ),
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                daq.LEDDisplay(
                                    id="offconf-display",
                                    size=10,
                                    value=offconf,
                                    label="OFF Config (s)",
                                    labelPosition="bottom",
                                    color=theme["primary"],
                                    className="five columns",
                                ),
                            ]),
                        ]),
                    ]),
                ]
            ),
        ]),
        ],
    )

def home():
    data = JSONS().readconfjson()
    onconf = data['onconf']
    offconf = data['offconf']
    timenow = data['timeconf']
    testno = JSONS().readtestjson()['testID']
    (h, m, s) = timenow.split(':')
    return dbc.Row(
            className="row",
            children=[
                # LEFT PANEL - TEST SETTINGS
                dbc.Col(
                    width=4,
                    children=[
                        onoff_setting_div(testno),
                        time_setting_div(timenow, h,m,s),
                        connections_setting_div(onconf, offconf),
                        niepotrzebne(),
                    ],
                ),
                # RIGHT PANEL - TEST INFO
                dbc.Col(
                    width=8,
                    children=[
                        dbc.Row(
                            className="right-panel",
                            children=[
                                    dbc.Col(
                                        className="Title",
                                        children=html.H3(
                                            "Graph", id="graph-title", style={"color": theme["primary"]}
                                        ),
                                    ),
                                ],
                        ),

                        dbc.Row(
                            className="right-panel-graph",
                            children=[
                                dbc.Col([test_info()]),
                            ],
                        ),
                        dbc.Row(
                                dbc.Col(id="time_series_chart_col_now"),
                        )
                    ],
                ),
            dcc.Interval(id='interval', interval=500),
            ],
        ),
   
   
def history():
    types = get_sensor_types()
    return dbc.Col(
            width=12,
            children=[
                dbc.Row(
                    className="right-panel",
                    children=[
                            dbc.Col(
                                className="Title",
                                children=html.H3(
                                    "Graph", id="graph-title", style={"color": theme["primary"]}
                                ),
                            ),
                        ],
                ),

                dbc.Row(
                    className="right-panel-graph",
                    children=[
                        dbc.Col([
                            dcc.Dropdown(
                                id='demo-dropdown',
                                options=types,
                                value=types[0]["label"]
                            ),

                        ]),
                    ],
                ),
                dbc.Row([
                        html.Div(id="time_series_chart_col"),
                ]
                )
            ],
        ),


def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return html.Div([
    dcc.Location(id='url', refresh=False),
    get_navbar(),
    html.Div(id='page-content')
])
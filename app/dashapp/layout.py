import os
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
    return html.Div(
            id="header",
            className="banner row",
            children=[
                # Logo and Title
                html.Div(
                    className="banner-logo-and-title",
                    children=[
                        html.Img(
                            # src=app.get_asset_url("dash-logo-white.png"),
                            className="logo",
                        ),
                        html.H2(
                            "Pomiar częstości łączeń silnika"
                        ),
                    ],
                ),
                html.Div(
                    className="row toggleDiv",
                    children=daq.ToggleSwitch(
                        id="toggleTheme", size=40, value=False, color="#00418e"
                    ),
                ),
            ],
        )


def power_setting_div(jsontimeconf, h,m,s):
    return html.Div(
        className="row power-settings-tab",
        children=[
            # Title
            html.Div(
                className="Title",
                children=html.H3(
                    "Power", id="power-title", style={"color": theme["primary"]}
                ),
            ),
            # Power Controllers
            html.Div(
                className="power-controllers",
                children=[
                    html.Div(
                        [
                        daq.Indicator(
                            id='my-indicator',
                            label="ON",
                        ),
                        html.Button('start', id='start'),
                        dcc.Interval(id='interval', interval=500),
                        html.Button('stop', id='stop'),
                        html.Div(id='lock'),
                        html.Div(id='output'),
                        html.Div(id='placeholder'),
                        ],
                        className="six columns",
                    ),
                    html.Div(
                        [
                            daq.NumericInput(
                                id="hours-input",
                                value=h,
                                min=0,
                                max=24,
                                className="four columns",
                            ),
                            daq.NumericInput(
                                id="minutes-input",
                                value=m,
                                min=0,
                                max=59,
                                className="four columns",
                            ),
                            daq.NumericInput(
                                id="seconds-input",
                                value=s,
                                min=0,
                                max=59,
                                className="four columns",
                            ),
                            # html.Div(id='timeconf-knob-output'),
                            daq.LEDDisplay(
                                id='timeconf-knob-output',
                                value=jsontimeconf,
                                size=20,
                                label="Test duration",
                                labelPosition="top",
                                color=theme["primary"],
                                className="four columns"
                            ) 
                        ],
                        className="six columns",
                    ),
                ],
            ),
        ],
    )



def knobs(onconf, offconf):
    return html.Div(
        [
            daq.Knob(
                value=onconf,
                id="onconf-input",
                label="ON Config (s)",
                labelPosition="bottom",
                size=70,
                color=theme["primary"],
                max=10,
                min=0.1,
                style={"backgroundColor": "transparent"},
                className="four columns",
            ),
            daq.Knob(
                value=offconf,
                id="offconf-input",
                label="OFF Config (s)",
                labelPosition="bottom",
                size=70,
                color=theme["primary"],
                max=10,
                min=0.1,
                className="four columns",
            ),
        ],
        className="knobs",
    )

def led_displays(onconf, offconf):
    return html.Div(
        [
            daq.LEDDisplay(
                id="onconf-display",
                size=10,
                value=onconf,
                label="ON Config (s)",
                labelPosition="bottom",
                color=theme["primary"],
                className="four columns",
            ),
            daq.LEDDisplay(
                id="offconf-display",
                size=10,
                value=offconf,
                label="OFF Config (s)",
                labelPosition="bottom",
                color=theme["primary"],
                className="four columns",
            ),
        ],
        className="led-displays",
    )

def function_setting_div(onconf, offconf):
    data = JSONS().readconfjson()
    onconf = data['onconf']
    offconf = data['offconf']
    return html.Div(
        className="row power-settings-tab",
        children=[
            html.Div(
                className="Title",
                style={"color": theme["primary"]},
                children=html.H3("Function", id="function-title"),
            ),
            html.Div(
                children=[
                    # Knobs
                    knobs(onconf, offconf),
                    # LED Displays
                    led_displays(onconf, offconf),
                ]
            ),
        ],
    )

def tab1():
    data = JSONS().readconfjson()
    onconf = data['onconf']
    offconf = data['offconf']
    jsontimeconf = data['timeconf']
    (h, m, s) = jsontimeconf.split(':')
    return html.Div(
            className="row",
            children=[
                # LEFT PANEL - SETTINGS
                html.Div(
                    className="five columns",
                    children=[
                        html.Div(
                            id="left-panel",
                            children=[
                                html.Div(
                                    id="dark-theme-components",
                                    className="left-panel-controls",
                                    style={"height": 705},
                                    children=DarkThemeProvider(
                                        theme=theme,
                                        children=[
                                            power_setting_div(jsontimeconf, h,m,s),
                                            function_setting_div(onconf, offconf),
                                        ],
                                    ),
                                )
                            ],
                        )
                    ],
                ),
                # RIGHT PANEL - OSCILLATIONS
                html.Div(
                    className="seven columns",
                    children=[
                        html.Div(
                            id="right-panel",
                            className="right-panel",
                            children=[
                                html.Div(
                                    id="card-right-panel-info",
                                    className="light-card",
                                    children=[
                                        html.Div(
                                            [html.H3("Graph", id="graph-title")],
                                            style={"color": theme["primary"]},
                                            className="Title",
                                        ),
                                        dcc.Tabs(
                                            id="tabs",
                                            children=[
                                                dcc.Tab(label="Run #1", value="1")
                                            ],
                                            value="1",
                                            className="oscillator-tabs",
                                        ),
                                        html.Div(
                                            className="row oscope-info",
                                            children=[
                                                html.Div(
                                                    id="div-graph-info",
                                                    className="graph-param",
                                                    children=html.Div(
                                                        id="graph-info", children="-"
                                                    ),
                                                ),
                                                html.Button(
                                                    "+",
                                                    id="new-tab",
                                                    n_clicks=0,
                                                    type="submit",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="card-graph",
                                    className="light-card",
                                    children=html.Div(id="time_series_chart_col_now"),
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
   

def tab2():
    types = get_sensor_types()
    return html.Div(
            className="row",
            children=[
                html.Div(
                    className="twelve columns",
                    children=[
                        html.Div(
                            id="right-panel",
                            className="right-panel",
                            children=[
                                html.Div(
                                    id="card-right-panel-info",
                                    className="light-card",
                                    children=[
                                        html.Div(
                                            [html.H3("Graph", id="graph-title")],
                                            style={"color": theme["primary"]},
                                            className="Title",
                                        ),
                                        dcc.Tabs(
                                            id="tabs",
                                            children=[
                                                dcc.Tab(label="Run #1", value="1")
                                            ],
                                            value="1",
                                            className="oscillator-tabs",
                                        ),
                                        html.Div(
                                            className="row oscope-info",
                                            children=[
                                                html.Div(
                                                    id="div-graph-info",
                                                    className="graph-param",
                                                    children=html.Div(
                                                        id="graph-info", children="-"
                                                    ),
                                                ),
                                                html.Button(
                                                    "+",
                                                    id="new-tab",
                                                    n_clicks=0,
                                                    type="submit",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),

                                dcc.Dropdown(
                                        id='demo-dropdown',
                                        options=types,
                                        value=types[0]["label"]
                                    ),
                                html.Div(
                                    id="card-graph",
                                    className="light-card",
                                    children=html.Div(id="time_series_chart_col"),
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),



def layout():
    return html.Div(
        id="main-page",
        children=[
            get_navbar(),
            html.Div(
                [
                dcc.Tabs(id='main-page-tabs', value='tab-1',children=[
                    dcc.Tab(label='Dashboard', value='tab-1'),
                    dcc.Tab(label='History', value='tab-2'),
                ], colors={
                    "border": "white",
                    "primary": "gold",
                    "background": "cornsilk"
                }
            ),
                html.Div(id='main-page-content')
            ]
        )
    ],
)


def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return html.Div(
        [
            # Just the navigation bar at the top for now...
            # Stay tuned for part 3!
            layout(),
        ], 
    )
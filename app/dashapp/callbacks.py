from app.dashapp.layout import home, history, onoff_setting_div, connections_setting_div
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app.dashapp.sensors import Semaphore, JSONS, Tests, Database
from subprocess import call
import datetime
from dash.exceptions import PreventUpdate
from app.dashapp.motor import task1, task2
import threading
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

semaphore = Semaphore()

axis_color = {"dark": "#EBF0F8", "light": "#506784"}
marker_color = {"dark": "#f2f5fa", "light": "#2a3f5f"}

##################### Motor loger ############################
def run_motor():
    if semaphore.is_locked():
        raise Exception("aaa")
    semaphore.lock()
    Tests().create_test()
    JSONS().writestatus("on", True)
    task1(True)
    JSONS().writestatus("on", False)
    Tests().finish_test()
    semaphore.unlock()
    return datetime.datetime.now()

##################### History chart ###########################
def get_sensor_time_series_data(test_id):
    sql = f"""
        SELECT 
            time_bucket('00:00:01'::interval, time) as time,
            test_id,
            avg(temperature) as temperature,
            avg(onconf) as cpu
        FROM sensor_data
        WHERE test_id = {test_id}
        GROUP BY 
            time_bucket('00:00:01'::interval, time), 
            test_id
        ORDER BY 
            time_bucket('00:00:01'::interval, time), 
            test_id;
    """
    with Database() as db:
        rows = db.query(sql)
        columns = [str.lower(x[0]) for x in db.cursor.description]
        db.close 
        df = pd.DataFrame(rows, columns=columns)
    # print("rows",rows)
    # print("columns",columns)
    return df

def get_graph(trace, title):
    return dcc.Graph(
        # Disable the ModeBar with the Plotly logo and other buttons
        config=dict(
            displayModeBar=True
        ),
        figure=go.Figure(
            data=[trace],
            layout=go.Layout(
                title=title,
                plot_bgcolor="white",
                xaxis=dict(
                    autorange=True,
                    # Time-filtering buttons above chart
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                label="1d",
                                step="day",
                                stepmode="backward"),
                            dict(count=7,
                                label="7d",
                                step="day",
                                stepmode="backward"),
                            dict(count=1,
                                label="1m",
                                step="month",
                                stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    type = "date",
                    # Alternative time filter slider
                    rangeslider = dict(
                        visible = True
                    )
                )
            )
        )
    )

###################### History now ############################
def get_now_graph(trace, title):
    return dcc.Graph(
        # Disable the ModeBar with the Plotly logo and other buttons
        config=dict(
            displayModeBar=False
        ),
        figure=go.Figure(
            data=[trace],
            layout=go.Layout(
                title=title,
                plot_bgcolor="white",
                xaxis=dict(
                    autorange=True,
                    # Time-filtering buttons above chart
                    type = "date",
                    # Alternative time filter slider
                )
            )
        )
    )

def now_data():
    lasttest = JSONS().readtestjson()["testID"]
    sql = f"""
        SELECT 
            time_bucket('00:00:01'::interval, time) as time,
            test_id,
            avg(temperature) as temperature,
            avg(onconf) as cpu
        FROM sensor_data
        WHERE test_id = {lasttest}
        GROUP BY 
            time_bucket('00:00:01'::interval, time), 
            test_id
        ORDER BY 
            time_bucket('00:00:01'::interval, time), 
            test_id;
    """
    with Database() as db:
        rows = db.query(sql)
        columns = [str.lower(x[0]) for x in db.cursor.description]
        db.close 
        df = pd.DataFrame(rows, columns=columns)
    # print("rows",rows)
    # print("columns",columns)
    return df

############# REGISTER CALLBACKS ##############################
def register_callbacks(dash_app):

##################### test info ###############################
    @dash_app.callback(
        Output('running-indicator', 'value'),
        Input('interval', 'n_intervals'))
    def display_status(n_intervals):
        return True if semaphore.is_locked() else False

    @dash_app.callback(
        Output('testtime-now', 'value'),
        Input('interval', 'n_intervals'))
    def display_test_info(n_intervals):
        timeconfig = JSONS().readtestjson()
        nowtime = datetime.datetime.now() - datetime.datetime.strptime(timeconfig['started'], '%Y-%m-%d %H:%M:%S')
        finished_time = datetime.datetime.strptime(timeconfig['finished'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(timeconfig['started'], '%Y-%m-%d %H:%M:%S')
        now = str(nowtime)[:7]
        fin = str(finished_time)[:7]
        if semaphore.is_locked():
            return now
        else:
            return fin
        
    @dash_app.callback(
        Output('output', 'children'),
        Input('start', 'n_clicks'))
    def run_loging_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return run_motor()

    @dash_app.callback(
        Output('stoped', 'value'),
        Input('stop', 'n_clicks'))
    def stop_loging_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        JSONS().writestatus("on", False)
        return True, task1(False)

##################### config ################################
    @dash_app.callback(
        Output('timeconf-knob-output', 'value'),
        [Input('time-input', 'value'),])
    def update_testtime(value):
        if value is None:
            raise PreventUpdate
        JSONS().writestatus("timeconf", str(value))
        return str(value)

    @dash_app.callback(
        Output('onconf-display', 'value'),
        [Input('onconf-input', 'value'),])
    def update_oncof(value):
        if value is None:
            raise PreventUpdate
        JSONS().writestatus("onconf", value)
        return value

    @dash_app.callback(
        Output('offconf-display', 'value'),
        [Input('offconf-input', 'value'),])
    def update_offconf(value):
        if value is None:
            raise PreventUpdate
        JSONS().writestatus("offconf", value)
        return value

    @dash_app.callback([
        Output('test-started', 'children'),
        Output('test-finished', 'children'),
        Output('test-status', 'children'),
        Output('test-id', 'children'),
        Output('testno', "value")
        ],
        Input('interval', 'n_intervals'))
    def display_testinfo(n_intervals):
        data = JSONS().readtestjson()
        started_value = str(data['started'])
        finished_value = str(data['finished'])
        status_value = str(data['status'])
        testno = str(data['testID'])
        return started_value, finished_value, status_value, testno, testno

##################### chart #################################
    @dash_app.callback(
        Output('dd-output-container', 'children'),
        [Input('demo-dropdown', 'value')])
    def update_output(value):
        return 'You have selected "{}"'.format(value)

    @dash_app.callback(
            Output("time_series_chart_col", "children"),
            [Input("demo-dropdown", "value")],
        )
    def get_time_series_chart(sensors_dropdown_value):
        df = get_sensor_time_series_data(sensors_dropdown_value)
        x = df["time"]
        y1 = df["temperature"]
        y2 = df["cpu"]
        title = f"Location: {sensors_dropdown_value} - Type: {sensors_dropdown_value}"

        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Temp"
        )
        trace2 = go.Scatter(
            x=x,
            y=y2,
            name="CPU"
        )

        # Create two graphs using the traces above
        graph1 = get_graph(trace1, title)
        graph2 = get_graph(trace2, title)

        return dbc.Col(
            [
                dbc.Row(dbc.Col(graph1)),
                dbc.Row(dbc.Col(graph2)),
            ]
        )

    @dash_app.callback(
            Output("time_series_chart_col_now", "children"),
            [Input("interval", "n_intervals")],
        )
    def get_time_series_chart_now(n_intervals):
        df = now_data()
        x = df["time"]
        y1 = df["temperature"]
        # y2 = df["cpu"]
        title = f"Now"

        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Temp"
        )
        # trace2 = go.Scatter(
        #     x=x,
        #     y=y2,
        #     name="CPU"
        # )

        # Create two graphs using the traces above
        graph1 = get_now_graph(trace1, title)
        # graph2 = get_now_graph(trace2, title)

        return html.Div(
            [
                dbc.Row(dbc.Col(graph1)),
                # dbc.Row(dbc.Col(graph2)),
            ]
        )

##################### main page #############################
    @dash_app.callback(dash.dependencies.Output('page-content', 'children'),
                [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/history':
            return history()
        else:
            return home()

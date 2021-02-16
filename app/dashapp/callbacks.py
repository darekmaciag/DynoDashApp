from os import name
from app.dashapp.layout import home, history, onoff_setting_div, connections_setting_div
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app.dashapp.sensors import Semaphore, Tests, Database
from subprocess import call
import datetime
from dash.exceptions import PreventUpdate
from app.dashapp.motor import task1, task2
import threading
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.tools as tls
from dateutil import parser
import redis


r=redis.Redis()
semaphore = Semaphore()


##################### Motor logger ##########################
def run_motor():
    if semaphore.is_locked():
        raise Exception("aaa")
    semaphore.lock()
    Tests().create_test()
    r.set("power", "on")
    task1(True)
    r.set("power", "off")
    Tests().finish_test()
    semaphore.unlock()
    return datetime.datetime.now()

##################### History chart #########################
def get_sensor_time_series_data(test_id):
    sql = f"""
        SELECT 
            time_bucket('00:00:01'::interval, time) as time,
            test_id,
            avg(temperature) as temperature,
            avg(onconf+temperature)/2 as cpu,
            offconf,
            onconf
        FROM sensor_data
        WHERE test_id = {test_id}
        GROUP BY 
            time_bucket('00:00:01'::interval, time), 
            test_id,
            offconf,
            onconf
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
        config=dict(
            displayModeBar=True
        ),
        figure=go.Figure(
            data=trace,
            layout=go.Layout(
                title=title,
                plot_bgcolor="white",
                xaxis=dict(
                    autorange=True,
                    type = "date",
                    rangeslider = dict(
                        visible = True
                    )
                )
            )
        )
    )

###################### Current chart ########################
def now_data():
    lasttest = int(r.get("testID").decode())
    sql = f"""
        SELECT 
            time_bucket('00:00:01'::interval, time) as time,
            test_id,
            avg(temperature) as temperature,
            avg(onconf+temperature)/2 as cpu,
            offconf,
            onconf
        FROM sensor_data
        WHERE test_id = {lasttest}
        GROUP BY 
            time_bucket('00:00:01'::interval, time), 
            test_id,
            offconf,
            onconf
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

def get_current_graph(trace, title):
    return dcc.Graph(
        config=dict(
            displayModeBar=False
        ),
        figure=go.Figure(
            data=trace,
            layout=go.Layout(
                title=title,
                plot_bgcolor="white",
                xaxis=dict(
                    autorange=True,
                    type = "date",
                )
            )
        )
    )



############# REGISTER CALLBACKS ############################
def register_callbacks(dash_app):

##################### test info #############################
    @dash_app.callback(
        Output('running-indicator', 'value'),
        Input('interval', 'n_intervals'))
    def display_status(n_intervals):
        return True if semaphore.is_locked() else False

    @dash_app.callback(
        Output('testtime-now', 'value'),
        Input('interval', 'n_intervals'))
    def display_test_info(n_intervals):
        nowtime = datetime.datetime.now() - parser.parse(str(r.get("started").decode()))
        finished_time = parser.parse(str(r.get("finished").decode())) - parser.parse(str(r.get("started").decode()))
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
        r.set("power", "off")
        return True, task1(False)

##################### config ################################
    @dash_app.callback(
        Output('timeconf-knob-output', 'value'),
        [Input('time-input', 'value'),])
    def update_testtime(value):
        if value is None:
            raise PreventUpdate
        r.set("timeconf", str(value))
        return str(value)

    @dash_app.callback(
        Output('onconf-display', 'value'),
        [Input('onconf-input', 'value'),])
    def update_oncof(value):
        if value is None:
            raise PreventUpdate
        r.set("onconf", value)
        return value

    @dash_app.callback(
        Output('offconf-display', 'value'),
        [Input('offconf-input', 'value'),])
    def update_offconf(value):
        if value is None:
            raise PreventUpdate
        r.set("offconf", value)
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
        (a,b,c,d) = r.mget("started", "finished", "status", "testID")
        started_value = str(a.decode())
        finished_value = str(b.decode())
        status_value = str(c.decode())
        testno = str(d.decode())
        return started_value, finished_value, status_value, testno, testno

##################### chart history #########################
    @dash_app.callback(
        Output('dd-output-container', 'children'),
        [Input('demo-dropdown', 'value')])
    def update_output(value):
        return 'Test No. : "{}"'.format(value)

    @dash_app.callback(
            Output("time_series_chart_col", "children"),
            [Input("demo-dropdown", "value")],
        )
    def get_time_series_chart(sensors_dropdown_value):
        df = get_sensor_time_series_data(sensors_dropdown_value)
        x = df["time"]
        y1 = df["temperature"]
        y2 = df["cpu"]
        y3 = df["onconf"]
        y4 = df["offconf"]
        title = f"Location: {sensors_dropdown_value} - Type: {sensors_dropdown_value}"
        fig = make_subplots()
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
        trace3 = go.Bar(
            x=x,
            y=y3,
            name="onconf",
        )

        trace4 = go.Bar(
            x=x,
            y=y4,
            name="offconf",
        )

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.add_trace(trace4)
        graph1 = get_graph(fig, title)
        graph2 = get_graph(trace2, title)

        return dbc.Col(
            [
                dbc.Row(dbc.Col(graph1)),
                dbc.Row(dbc.Col(graph2)),
            ]
        )

##################### Chart now #############################
    @dash_app.callback(
            Output("time_series_chart_col_now", "children"),
            [Input("interval", "n_intervals")],
        )
    def get_time_series_chart_now(n_intervals):
        df = now_data()
        x = df["time"]
        y1 = df["temperature"]
        y2 = df["cpu"]
        y3 = df["onconf"]
        y4 = df["offconf"]

        title = f"Now"
        fig = make_subplots()


        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Sensor 1"
        )

        trace2 = go.Scatter(
            x=x,
            y=y2,
            name="Sensor 2"
        )
        
        trace3 = go.Bar(
            x=x,
            y=y3,
            name="onconf",
        )

        trace4 = go.Bar(
            x=x,
            y=y4,
            name="offconf",
        )

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.add_trace(trace4)
        fig.update_layout(showlegend=False)

        graph1 = get_current_graph(fig, title)

        return html.Div(
            [
                dbc.Row(dbc.Col(graph1)),
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

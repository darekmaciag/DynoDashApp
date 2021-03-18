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
from app.dashapp.motor import task1, task2, task3
import threading
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.tools as tls
from dateutil import parser
import redis
import asyncio


r=redis.Redis()
semaphore = Semaphore()

##################### Motor logger ##########################
async def some_func():
    t1 = asyncio.create_task(task1())
    t2 = asyncio.create_task(task2())
    pidtaskstatus = int(r.get("autopid").decode())
    if pidtaskstatus == 1:
        t3 = asyncio.create_task(task3())
    timedel = gettimedelta()
    end = datetime.datetime.now() + timedel
    now = datetime.datetime.now()
    await asyncio.sleep((end - now).total_seconds())
    print('loop stopped since')
    t1.cancel()
    t2.cancel()
    if pidtaskstatus == 1:
        t3.cancel

async def cancel(task):
    while True:
        power_status = str(r.get("power").decode())
        if power_status == "off":
            return task.cancel()
        await asyncio.sleep(0.5)

def gettimedelta():
    timeconfig = str(r.get("timeconf").decode())
    (h, m, s) = timeconfig.split(':')
    timedelda = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    return timedelda  

async def run_motor():
    global func_task
    if semaphore.is_locked():
        raise Exception("aaa")
    semaphore.lock()
    Tests().create_test()
    r.set("power", "on")
    # print(f"Callback: {threading.current_thread().name}")
    func_task = asyncio.create_task(some_func())
    cancel_task = asyncio.ensure_future(cancel(func_task))
    try:
        await func_task
    except asyncio.CancelledError:
        print('Task cancelled as expected')
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
            avg(temperature1) as temperature1,
            avg(temperature2) as temperature2,
            avg(temperature3) as temperature3,
            avg(temperature4) as temperature4,
            avg(temperature5) as temperature5,
            avg(temperature6) as temperature6,
            avg(avg_temp) as avg_temp,
            avg(maxtemp) as maxtemp,
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
    return df

def get_graph(trace):
    return dcc.Graph(
        config=dict(
            displayModeBar=True,
            displaylogo= False,
            responsive=True,
            modeBarButtonsToAdd= [
                'drawline' , 
                'drawopenpath' , 
                'drawclosedpath' , 
                'drawcircle' , 
                'drawrect' , 
                'eraseshape' 
                ]
        ),
        figure=go.Figure(
            data=trace,
        )
    )

###################### Current chart ########################
def now_data():
    lasttest = int(r.get("testID").decode())
    sql = f"""
        SELECT 
            time_bucket('00:00:01'::interval, time) as time,
            test_id,
            avg(temperature1) as temperature1,
            avg(temperature2) as temperature2,
            avg(temperature3) as temperature3,
            avg(temperature4) as temperature4,
            avg(temperature5) as temperature5,
            avg(temperature6) as temperature6,
            avg(avg_temp) as avg_temp,
            avg(maxtemp) as maxtemp,
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

def get_current_graph(trace):
    return dcc.Graph(
        config=dict(
            displayModeBar=False,
            displaylogo=False,
            responsive=True
        ),
        figure=go.Figure(
            data=trace,
        )
    )


############# REGISTER CALLBACKS ############################
def register_callbacks(dash_app):

##################### test info #############################
    @dash_app.callback([
        Output('testtime-now', 'value'),
        Output('running-indicator', 'value'),
    ],
        Input('interval', 'n_intervals'))
    def display_test_info(n_intervals):
        nowtime = datetime.datetime.now() - parser.parse(str(r.get("started").decode()))
        now = str(nowtime)[:7]
        if semaphore.is_locked():
            return now, True
        else:
            return "00:00:00", False

    @dash_app.callback([
        Output('onconf-input', 'value'),
        Output('offconf-input', 'value'),
    ],
        Input('interval', 'n_intervals'))
    def update_inputs(n_intervals):
        onconf = float(r.get("onconf").decode())
        offconf = float(r.get("offconf").decode())
        return onconf, offconf

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

        
    @dash_app.callback(
        Output('output', 'children'),
        Input('start', 'n_clicks'))
    def run_loging_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return asyncio.run(run_motor())

    @dash_app.callback(
        Output('stoped', 'value'),
        Input('stop', 'n_clicks'))
    def stop_loging_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        r.set("power", "off")
        return True

    @dash_app.callback(
        Output('pidout', 'children'),
        Input('autopid', 'value')
    )
    def update_pid(value):
        if value is None:
            raise PreventUpdate
        if value is True:
            r.set("autopid", 1)
        elif value is False:
            r.set("autopid", 0)
        return 'The switch is {}.'.format(value)

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

    @dash_app.callback(
        Output('maxtemp-display', 'value'),
        [Input('maxtemp-input', 'value'),])
    def update_offconf(value):
        if value is None:
            raise PreventUpdate
        r.set("maxtemp", value)
        return value

##################### chart history #########################
    @dash_app.callback(
        Output('dd-output-container', 'children'),
        [Input('history-dropdown', 'value')])
    def update_output(value):
        return 'Test No. : "{}"'.format(value)

    @dash_app.callback(
            Output("time_series_chart_col", "children"),
            [Input("history-dropdown", "value")],
        )
    def get_time_series_chart(sensors_dropdown_value):
        df = get_sensor_time_series_data(sensors_dropdown_value)
        x = df["time"]
        y1 = df["temperature1"]
        y2 = df["temperature2"]
        y3 = df["temperature3"]
        y4 = df["temperature4"]
        y5 = df["temperature5"]
        y6 = df["temperature6"]
        y7 = df["avg_temp"]
        y8 = df["maxtemp"]
        y9 = df["onconf"]
        y10 = df["offconf"]
        fig = make_subplots()
        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Temp1",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        trace2 = go.Scatter(
            x=x,
            y=y2,
            name="Temp2",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        trace3 = go.Scatter(
            x=x,
            y=y3,
            name="Temp3",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
        )

        trace4 = go.Scatter(
            x=x,
            y=y4,
            name="Temp4",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        
        trace5 = go.Scatter(
            x=x,
            y=y5,
            name="Temp5",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
            
        )
        
        trace6 = go.Scatter(
            x=x,
            y=y6,
            name="Temp6",
            legendgroup="temp",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        
        trace7 = go.Scatter(
            x=x,
            y=y7,
            name="avg_temp",
            line = dict(color='royalblue', width=3)

        )
        
        trace8 = go.Scatter(
            x=x,
            y=y8,
            name="maxtemp",
            line = dict(color='red', width=3)

        )
        
        trace9 = go.Bar(
            x=x,
            y=y9,
            legendgroup="connections",
            name="onconf",
        )
        
        trace10 = go.Bar(
            x=x,
            y=y10,
            legendgroup="connections",
            name="offconf",
        )
        

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.add_trace(trace4)
        fig.add_trace(trace5)
        fig.add_trace(trace6)
        fig.add_trace(trace7)
        fig.add_trace(trace8)
        fig.add_trace(trace9)
        fig.add_trace(trace10)
        fig.update_layout(
            showlegend=True,
            autosize=True,
            height=600,
            margin=dict(
                l=1,
                r=1,
                b=1,
                t=30,
                pad=0),
            legend=dict(
                orientation="h",
                xanchor="center",
                x=0.5
            )
            )
        graph1 = get_graph(fig)

        return dbc.Col(
            [
                dbc.Row(dbc.Col(graph1)),
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
        y1 = df["temperature1"]
        y2 = df["temperature2"]
        y3 = df["temperature3"]
        y4 = df["temperature4"]
        y5 = df["temperature5"]
        y6 = df["temperature6"]
        y7 = df["avg_temp"]
        y8 = df["maxtemp"]
        y9 = df["onconf"]
        y10 = df["offconf"]
        fig = make_subplots()
        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Temp1",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        trace2 = go.Scatter(
            x=x,
            y=y2,
            name="Temp2",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        trace3 = go.Scatter(
            x=x,
            y=y3,
            name="Temp3",
            line = dict(color='lightblue', width=3, dash='dot')
        )

        trace4 = go.Scatter(
            x=x,
            y=y4,
            name="Temp4",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        
        trace5 = go.Scatter(
            x=x,
            y=y5,
            name="Temp5",
            line = dict(color='lightblue', width=3, dash='dot')
            
        )
        
        trace6 = go.Scatter(
            x=x,
            y=y6,
            name="Temp6",
            line = dict(color='lightblue', width=3, dash='dot')
        )
        
        trace7 = go.Scatter(
            x=x,
            y=y7,
            name="avg_temp",
            line = dict(color='royalblue', width=3)

        )
        
        trace8 = go.Scatter(
            x=x,
            y=y8,
            name="maxtemp",
            line = dict(color='red', width=3)

        )
        
        trace9 = go.Bar(
            x=x,
            y=y9,
            name="onconf",
        )
        
        trace10 = go.Bar(
            x=x,
            y=y10,
            name="offconf",
        )
        

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.add_trace(trace4)
        fig.add_trace(trace5)
        fig.add_trace(trace6)
        fig.add_trace(trace7)
        fig.add_trace(trace8)
        fig.add_trace(trace9)
        fig.add_trace(trace10)
        fig.update_layout(
            showlegend=False,
            autosize=True,
            height=534,
            margin=dict(
            l=5,
            r=5,
            b=5,
            t=5,
            pad=0),
            )

        graph1 = get_current_graph(fig)

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

    @dash_app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
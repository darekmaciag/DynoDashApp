from app.dashapp.layout import tab1, tab2, power_setting_div, function_setting_div
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
from dash_daq import DarkThemeProvider
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

semaphore = Semaphore()

axis_color = {"dark": "#EBF0F8", "light": "#506784"}
marker_color = {"dark": "#f2f5fa", "light": "#2a3f5f"}

theme = {
    "dark": False,
    "primary": "#447EFF",
    "secondary": "#D3D3D3",
    "detail": "#D3D3D3",
}

########### Motor loger###########
def run_motor():
    if semaphore.is_locked():
        raise Exception('Resource is locked')
    semaphore.lock()
    Tests().create_test()
    JSONS().writestatus("on", True)
    task1(True)
    JSONS().writestatus("on", False)
    Tests().finish_test()
    semaphore.unlock()
    return datetime.datetime.now()

############# History chart #####################

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
##############################################################


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



def register_callbacks(dash_app):
    """Register the callback functions for the Dash app, within the Flask app"""        

##################### config ############################
    @dash_app.callback(
        Output('my-indicator', 'value'),
        Input('interval', 'n_intervals'))
    def display_status(n_intervals):
        return True if semaphore.is_locked() else False

    @dash_app.callback(
        Output('placeholder', 'children'),
        Input('stop', 'n_clicks'))
    def stop_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        JSONS().writestatus("on", False)
        return 'Stop', task1(False)

    @dash_app.callback(
        Output('timeconf-knob-output', 'value'),
        [Input('hours-input', 'value'),
        Input('minutes-input', 'value'),
        Input('seconds-input', 'value')])
    def update_testtime(inhours, inminutes, inseconds):
        inputtime = datetime.timedelta(hours=int(inhours), minutes=int(inminutes), seconds=int(inseconds))
        if inhours is None and inminutes is None and inseconds is None:
            raise PreventUpdate
        JSONS().writestatus("timeconf", str(inputtime))
        return str(inputtime)

    @dash_app.callback(
        Output('output', 'children'),
        Input('start', 'n_clicks'))
    def run_process(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return 'Finished at {}'.format(run_motor())

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

################### chart #####################
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

        return html.Div(
            [
                dbc.Row(dbc.Col(graph1)),
                dbc.Row(dbc.Col(graph2)),
            ]
        )

######################################################

    @dash_app.callback(
            Output("time_series_chart_col_now", "children"),
            [Input("interval", "n_intervals")],
        )
    def get_time_series_chart_now(n_intervals):
        df = now_data()
        x = df["time"]
        y1 = df["temperature"]
        y2 = df["cpu"]
        title = f"Now"

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

        return html.Div(
            [
                dbc.Row(dbc.Col(graph1)),
                dbc.Row(dbc.Col(graph2)),
            ]
        )



############## main page ############################
    @dash_app.callback(Output('main-page-content', 'children'),
                Input('main-page-tabs', 'value'))
    def render_content(tab):
        if tab == 'tab-1':
            return tab1()
        elif tab == 'tab-2':
            return tab2()


        # Callback updating backgrounds
    @dash_app.callback(
        Output("dark-theme-components", "children"),
        [Input("toggleTheme", "value")],
    )
    def turn_dark(turn_dark,):
        data = JSONS().readconfjson()
        onconf = data['onconf']
        offconf = data['offconf']
        jsontimeconf = data['timeconf']
        (h, m, s) = jsontimeconf.split(':')
        theme.update(dark=turn_dark)
        return DarkThemeProvider(
            theme=theme,
            children=[
                power_setting_div(jsontimeconf, h,m,s),
                function_setting_div(onconf, offconf),
            ],
        )


    # Callback updating backgrounds
    @dash_app.callback(
        [
            Output("main-page", "className"),
            Output("left-panel", "className"),
            Output("card-right-panel-info", "className"),
            Output("card-graph", "className"),
        ],
        [Input("toggleTheme", "value")],
    )
    def update_background(turn_dark):

        if turn_dark:
            return ["dark-main-page", "dark-card", "dark-card", "dark-card"]
        else:
            return ["light-main-page", "light-card", "light-card", "light-card"]
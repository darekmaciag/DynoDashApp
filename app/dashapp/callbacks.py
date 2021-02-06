from app.dashapp.layout import tab1
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app.dashapp.sensors import Semaphore, JSONS, Tests
from subprocess import call
import datetime
from dash.exceptions import PreventUpdate
from app.dashapp.motor import task1, task2
import threading
from dash_daq import DarkThemeProvider

semaphore = Semaphore()

theme = {
    "dark": False,
    "primary": "#447EFF",
    "secondary": "#D3D3D3",
    "detail": "#D3D3D3",
}

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

def register_callbacks(dash_app):
    """Register the callback functions for the Dash app, within the Flask app"""        


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

    @dash_app.callback(Output('main-page-content', 'children'),
                Input('main-page-tabs', 'value'))
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([
                tab1()
            ])
        elif tab == 'tab-2':
            return html.Div([
                html.H3('Tab content 2')
            ])
import dash
import time, json
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import NonExistentEventException, PreventUpdate
import datetime
import sensors
from subprocess import call
from sensors import Tests, JSONS
import dash_daq as daq

class Semaphore:
    def __init__(self, filename='test.txt'):
        self.filename = filename
        with open(self.filename, 'w') as f:
            f.write('done')

    def lock(self):
        with open(self.filename, 'w') as f:
            f.write('working')

    def unlock(self):
        with open(self.filename, 'w') as f:
            f.write('done')

    def is_locked(self):
        return open(self.filename, 'r').read() == 'working'


semaphore = Semaphore()


def run_motor():
    if semaphore.is_locked():
        raise Exception('Resource is locked')
    semaphore.lock()
    Tests().create_test()
    JSONS().writestatus("on", True)
    call(["python", 'motor.py'])
    JSONS().writestatus("on", False)
    Tests().finish_test()
    semaphore.unlock()
    return datetime.datetime.now()


app = dash.Dash()
server = app.server


def layout():
    data = JSONS().readconfjson()
    onconfif = data['onconf']
    offconfif = data['offconf']
    jsontimeconf = JSONS().readconfjson()['timeconf']
    (h, m, s) = jsontimeconf.split(':')
    return html.Div([
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
        daq.Knob(id='onconf-knob',value=onconfif,max=10,min=0.1),
        html.Div(id='onconf-knob-output'),
        daq.Knob(id='offconf-knob',value=offconfif,max=10,min=0.1),
        html.Div(id='offconf-knob-output'),
        html.Div([
            daq.NumericInput(
                id="hours-input",
                value=h,
                min=0,
                max=24
            ),
            daq.NumericInput(
                id="minutes-input",
                value=m,
                min=0,
                max=59
            ),
            daq.NumericInput(
                id="seconds-input",
                value=s,
                min=0,
                max=59
            )
        ]),
        html.Div(id='timeconf-knob-output'),
    ])


app.layout = layout


@app.callback(
    Output('my-indicator', 'value'),
    Input('interval', 'n_intervals'))
def display_status(n_intervals):
    return True if semaphore.is_locked() else False


@app.callback(
    Output('placeholder', 'children'),
    Input('stop', 'n_clicks'))
def stop_process(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    JSONS().writestatus("on", False)
    return 'Stoped'

@app.callback(
    Output('timeconf-knob-output', 'children'),
    [Input('hours-input', 'value'),
    Input('minutes-input', 'value'),
    Input('seconds-input', 'value')])
def update_output(inhours, inminutes, inseconds):
    inputtime = datetime.timedelta(hours=int(inhours), minutes=int(inminutes), seconds=int(inseconds))
    if inhours is None and inminutes is None and inseconds is None:
        raise PreventUpdate
    JSONS().writestatus("timeconf", str(inputtime))
    return 'The knob value is {}.'.format(inputtime)

@app.callback(
    Output('onconf-knob-output', 'children'),
    [Input('onconf-knob', 'value'),])
def update_output(value):
    if value is None:
        raise PreventUpdate
    JSONS().writestatus("onconf", value)
    return 'The knob value is {}.'.format(value)

@app.callback(
    Output('offconf-knob-output', 'children'),
    [Input('offconf-knob', 'value'),])
def update_output(value):
    if value is None:
        raise PreventUpdate
    JSONS().writestatus("offconf", value)
    return 'The knob value is {}.'.format(value)

@app.callback(
    Output('output', 'children'),
    Input('start', 'n_clicks'))
def run_process(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return 'Finished at {}'.format(run_motor())


if __name__ == '__main__':
    app.run_server(debug=True) 

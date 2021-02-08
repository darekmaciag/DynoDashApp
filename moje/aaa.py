import dash
import dash_html_components as html
import dash_core_components as dcc
from database import Database
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


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
    print(test_id)
    with Database() as db:
        rows = db.query(sql)
        columns = [str.lower(x[0]) for x in db.cursor.description]
        db.close 
        df = pd.DataFrame(rows, columns=columns)
    print("rows",rows)
    print("columns",columns)
    return df

def get_graph(trace, title):
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

def get_layout():
    types = get_sensor_types()
    return html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
        options=types,
        value=types[0]["label"]
    ),
    html.Div(id='dd-output-container'),
    dbc.Row(
        dbc.Col(
            id="time_series_chart_col"
        )
    )
])


app.layout = get_layout()


@app.callback(
    Output('dd-output-container', 'children'),
    [Input('demo-dropdown', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)


@app.callback(
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

if __name__ == '__main__':
    app.run_server(debug=True)
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
# Read data from a csv
from dash import dash
from dash.dependencies import Output, Input

z_data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')

fig = go.Figure(data=go.Surface(z=z_data, showscale=False))
fig.update_layout(
    title='Mt Bruno Elevation',
    width=400, height=400,
    margin=dict(t=40, r=0, l=20, b=20)
)

name = 'default'
# Default parameters which are used when `layout.scene.camera` is not provided
camera = dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=0),
    eye=dict(x=1.25, y=1.25, z=1.25),
    projection=dict(type='orthographic')
)

fig.update_layout(scene_camera=camera, title=name)

app = dash.Dash()
app.layout = html.Div([
    html.H1('title', id='title'),
    dcc.Graph(figure=fig, id='figure'),
])


@app.callback(
    Output(component_id='title', component_property='children'),
    Input(component_id='figure', component_property='relayoutData')
)
def update_output_div(input_value):
    if input_value is not None:
        print(input_value)
        print(input_value['scene.camera'])
    return 'another title'


app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter

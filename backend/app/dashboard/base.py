import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Output, Input

layout = dbc.Container(
    html.Div([

    ], id='graph-div', className='paint', style=dict(width='100%', height='100%')),
    fluid=True, style=dict(width='100%', height='95%', padding=0),
)


def callbacks(app):
    @app.callback(Output('cytoscape-two-nodes', 'elements'), Input('graph-div', 'children'))
    def c1(_):
        return [
            {'data': {'id': 'one', 'label': 'Node 3', 'type': 'vee'}, 'position': {'x': 75, 'y': 75}},
            {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'source': 'one', 'target': 'two', 'label': 'test2'}, 'classes': 'autorotate'},
            {'data': {'source': 'two', 'target': 'two', 'label': 'test', 'arrow': 'diamond'}, 'classes': 'autorotate'}
        ]

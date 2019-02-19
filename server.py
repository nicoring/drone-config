import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np

from loader import CsvLoader, SpreadsheetLoader
from combinations import combination_generator

def to_tuple(row, x_col='max_payload', y_col='min_fly_time'):
    return np.array([row[x_col], row[y_col]])

def is_row_dominating(row, rest):
    x = to_tuple(row)
    for _, other in rest.iterrows():
        x_other = to_tuple(other)
        if all(x_other >= x) and any(x_other > x):
            return False
    return True

def dominating_specs(df):
    return df[df.apply(lambda r: is_row_dominating(r, df), axis=1)]

def tuple_to_string(tuple):
    return '\n'.join(str(tuple).split(','))

def tuple_to_json(tuple):
    return json.dumps(tuple._asdict())


# loader = CsvLoader('data')
loader = SpreadsheetLoader()
data = loader.load()
all_specs = [specs for _, _, _, specs in combination_generator(*data)]
df = pd.DataFrame(all_specs)
dominating_df = dominating_specs(df)
current_drone_df = pd.read_csv('data/current_drone.csv')

table_page = dash_table.DataTable(
    id='table',
    style_data={'whiteSpace': 'normal'},
    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.round(2).to_dict("rows"),
    sorting=True,
    filtering=True,
    sorting_type="multi"
)

pareto_page = html.Div([
    dcc.Graph(
        id='pareto-interactions',
        figure={
            'data': [
                {
                    'x': dominating_df['max_payload'],
                    'y': dominating_df['min_fly_time'],
                    'text': [],
                    'customdata': list(map(tuple_to_json, dominating_df.itertuples())),
                    'name': 'pareto optimal configs',
                    'mode': 'markers',
                    'marker': {'size': 10}
                },
                {
                    'x': current_drone_df['max_payload'],
                    'y': current_drone_df['min_fly_time'],
                    'text': [],
                    'customdata': list(map(tuple_to_json, current_drone_df.itertuples())),
                    'name': 'beagle prototype',
                    'mode': 'markers',
                    'marker': {'size': 10}
                }

            ],
            'layout': {
                'clickmode': 'event+select',
                'title': 'Pareto Optimal Configurations',
                'xaxis': {
                    'title': 'max payload (g)'
                },
                'yaxis': {
                    'title': 'min fly time (min)'
                }
            }
        }
    ),
    html.Pre(id='click-data')
])

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True
app.layout = html.Div([ 
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('pareto-interactions', 'clickData')])
def display_click_data(clickData):
    if clickData and clickData['points']:
        data = json.loads(clickData['points'][0]['customdata'])
        del data['Index']
        if '_1' in data:
            del data['_1']
        rows = [html.Tr([html.Td(k), html.Td(v)]) for k, v in data.items()]
        return html.Table(rows)
    else:
        return 'no point selected'

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname is None:
        return table_page
    elif pathname == '/pareto':
        return pareto_page
    else:
        return '404'
        

if __name__ == '__main__':
    app.run_server(debug=True)

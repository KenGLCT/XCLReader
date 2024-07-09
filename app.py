import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import plotly.express as px

import pandas as pd



app = dash.Dash(__name__, suppress_callback_exceptions=True)

server = app.server


app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
	html.H1(
		"Excel Plotter",
		style = {
		'text-align':'left',
		'color':'#6A5ACD',
		'text-indent': '2%',
		'animation-name': 'titleanimation',
  		'animation-duration': '4s'
		}
		),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            'textAlign': 'center',
            'color': 'white',
            'margin':'10',
            'animation-name': 'buttonanimation',
  			'animation-duration': '6s'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Br(),
    html.Div(id='output-div'),
    html.Div(id='output-datatable'),
])



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Br(),
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns],
                     style = {
						'text-align':'center'

							}
                     ),
        html.Br(),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns],
                     style = {
						'text-align':'center'
							}),
        html.Br(),
        html.Button(id="submit-button", children="Create Graph",
       
        	style={
        	'position': 'relative',
  			'left': '25%',
            'width': '50%',
            'height': '60px',

            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            'bordercolor':'white',
            'textAlign': 'center',
            'color':'black',
            'background-color':'white'

        }
        ),
        html.Br(),
        html.Br(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
def make_graphs(n, data, x_data, y_data):
    if n is None:
        return dash.no_update
    else:
        #figg = px.bar(data, x=x_data, y=y_data)
        figg = px.line(data, x=x_data, y=y_data)
        #figg = px.scatter(data, x=x_data, y=y_data)

        return dcc.Graph(figure=figg)



if __name__ == '__main__':
    app.run_server(debug=True)

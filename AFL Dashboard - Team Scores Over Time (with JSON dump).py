from dash import Dash, dcc, html, Input, Output, callback_context
import numpy as np
import pandas as pd
import plotly.express as px

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("AFL Stats", style={'textAlign': 'center'}),                   # heading
        html.Div([                                                             # buttons
                  "Home Team: ", dcc.Input(id='home-team', value='Richmond', type='text'),
                  html.Button('Weekly', id='submit-home-team', n_clicks=0),
                  ], style={'textAlign': 'center'}),
        html.Div(id='container-button-press')                                   # output label               
    ]),
    html.Div([
        dcc.Graph(id='home-score-graphic')                                     # graph 
    ]), 
    
    # dcc.Store stores the intermediate value
    dcc.Store(id='intermediate-value')
])


@app.callback(
    Output('intermediate-value', 'data'), 
    Input('submit-home-team', 'n_clicks')
)
def clean_data(value):
     # Read datafiles and produce data frames
     df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
     
     # Get list of home teams
     teams = df_games['homeTeam'].unique()
     return teams.to_json()


@app.callback(
    Output('container-button-press', 'children'),
    Input('submit-home-team', 'n_clicks'),
    Input('home-team', 'value')
)
def displayClick(n_clicks, input_value):
    msg = 'Number of clicks: "{}", Input Value: "{}"'.format(n_clicks, input_value)
    return html.Div(msg)


@app.callback(
    Output('home-score-graphic', 'figure'),
    Input('intermediate-value', 'data'),    
    Input('submit-home-team', 'n_clicks'),
)
def updateGraph(data, n_clicks):
    dff = pd.read_json
    figure = homeTeamScore(input_value) 
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)

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
    ])
])    
        
###############################################################################
#####                             STAT STUFF                              #####
###############################################################################
def homeTeamScore(homeTeam):
    # Read datafiles and produce data frames
    df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
    
    # Get list of home teams
    teams = df_games['homeTeam'].unique()
    
    if homeTeam in teams:
        # Get all scores and dates for home team
        home_df = df_games.loc[df_games['homeTeam'] == homeTeam]
        score = home_df['homeTeamScore']
        dates = home_df['date'] 
            
        fig = px.scatter(x=dates, y=score)
        return fig
    

###############################################################################
#####                           DASH FUNCTIONS                            #####
###############################################################################

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
    Input('submit-home-team', 'n_clicks'),
    Input('home-team', 'value')
)
def updateGraph(n_clicks, input_value):
    # if input_value in teams: (check to see if text field has a valid team, then call function)
        figure = homeTeamScore(input_value) 
        return figure

if __name__ == '__main__':
    app.run_server(debug=True)

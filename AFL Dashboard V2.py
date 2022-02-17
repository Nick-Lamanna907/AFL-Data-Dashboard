"""
Created on Thu Feb 17 11:11:20 2022

@author: nllama
"""

from dash import Dash, html, dcc, Output, Input, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#### Start-Up Code ####

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP])

## Read datafiles and produce data frames
# Create df of game data
df_games = pd.read_csv('/Users/nllama/Documents/games.csv')

# Create df of unique teams and column headings
df_teamList = pd.DataFrame({
    'teams' : df_games['homeTeam'].unique(),
})

#### Components Code ####

app.layout = html.Div([
    dbc.Row( # Heading row
        dbc.Col(
            html.H1( # Heading
                'AFL Data Dashboard V2', 
                style={'textAlign':'center'}), 
        )
    ),
    
    dbc.Row( # Team choice row
        dbc.Col(
            html.Div([ # Drop down menu for team selection
                "Choose a team: ", dcc.Dropdown( 
                id='dropdown-team', 
                value='Richmond', 
                options=[{'label':i, 'value':i} for i in df_teamList['teams'].unique()])
            ]), 
        width={'size':3, 'offset':2})
    ),
    
    dbc.Row( # Home and away scatter plot row
        dbc.Col(
                html.Div( # Graph
                    id='graph-scatter-score', 
                    children=[]), 
        width={'size':10, 'offset':1})
    ),
    
    dbc.Row( # W, D, L pie chart row
        dbc.Col(
                html.Div(
                    id='graph-pie-WLD', 
                    children=[]), 
        width={'size':4, 'offset':1})
    ),
    
    # dcc.Store inside the user's current browser session
    dcc.Store(id='store-team-data', data=[], storage_type='memory') # 'local' or 'session'
])

#### Callback Code ####

# Store dataframe of all game data (df_games) for chosen team when dropdown-team is modified 
@callback(
    Output('store-team-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def storeData(value):
    dataset = df_games.loc[(df_games['homeTeam'] == value) | (df_games['awayTeam'] == value)] # Get all rows with chosen team in theme
    dataset["date"] = pd.to_datetime(dataset['date']) 
    dataset = dataset.sort_values(by='date') # Reorder based on date
    return dataset.to_dict()

# Create scatter from stored dataset (remember: stored dataset is for chosen team)
@callback(
    Output('graph-scatter-score', 'children'), # Scatter
    Input('store-team-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def createHAScoreScatter(data, value):
    df = pd.DataFrame(data) # Get the stored dataframe (for the home team)
    homeGO = go.Scatter(x=df.loc[(df['homeTeam'] == value)]['date'], y=df.loc[(df['homeTeam'] == value)]['homeTeamScore'], name='home', mode='markers') # Home graph object
    awayGO = go.Scatter(x=df.loc[(df['awayTeam'] == value)]['date'], y=df.loc[(df['awayTeam'] == value)]['awayTeamScore'], name='away', mode='markers') # Away graph object
    fig = make_subplots() # Useful for editing plot https://plotly.com/python/figure-structure/
    fig.add_trace(homeGO)
    fig.add_trace(awayGO)
    fig.layout.xaxis.title.text = 'date' 
    fig.layout.yaxis.title.text = 'total score'
    fig.layout.title.text = value + ' Home and Away Scores' # How to centre??? 
    return dcc.Graph(figure=fig)

# Create scatter from stored dataset (remember: stored dataset is for chosen team)
@callback(
    Output('graph-pie-WLD', 'children'), # Pie
    Input('store-team-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def createWDLPie(data, value):
    df = pd.DataFrame(data) # Get the stored dataframe (for the home team)
    
    # Get home data
    df_home = df.loc[(df['homeTeam']==value)]
    df_home_W = df_home.loc[(df_home['homeTeamScore']>df_home['awayTeamScore'])]
    home_games = len(df_home.index)
    home_wins = len(df_home_W.index)
    
    # Get away data
    df_away = df.loc[(df['awayTeam']==value)]
    df_away_W = df_away.loc[(df_away['awayTeamScore']>df_away['homeTeamScore'])]
    away_games = len(df_away.index)
    away_wins = len(df_away_W.index)
    
    # Get draw data
    df_home_away = df.loc[(df['homeTeam']==value) | (df['awayTeam']==value)]
    df_D = df_home_away.loc[(df_home_away['homeTeamScore']==df_home_away['awayTeamScore'])]
    draws = len(df_D.index)
    
    # Create pie chart lists
    pieVals = [
        (home_wins + away_wins),
        (draws),
        (home_games + away_games - home_wins - away_wins),
    ]
    pieNames = ['W', 'D', 'L']
    
    # Make piechart
    fig = px.pie(values=pieVals, 
                 names=pieNames,
                 color=pieNames,
                 color_discrete_map={'W':'green',
                                 'D':'blue',
                                 'L':'red',},)
    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)
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
df_stats = pd.read_csv('/Users/nllama/Documents/stats.csv')
df_colours = pd.read_csv('/Users/nllama/Documents/clubcolours.csv')

# Create df of unique teams 
df_teamList = pd.DataFrame({
    'teams' : df_games['homeTeam'].unique(),
})

# Create df of unique players for Richmond 
df_team = df_stats.loc[(df_stats['team']=='Richmond')]
players = df_team['displayName'].unique()
df_playerList = pd.DataFrame({
    'players' : players,
})

# Player class for creating player card
class Player:
    def __init__(self):
        self.name = None
        self.games = None
        self.GPG = None
        self.BPG = None
        self.PPG = None
        self.DPG = None

#### Components Code ####

app.layout = html.Div([
    html.Div([
        dbc.Row( # Heading row
            dbc.Col(
                html.H1( # Heading
                    'AFL Data Dashboard V2', 
                    style={'textAlign':'center'}), 
            )
        ),
    ]),
    
    html.Div([
        dbc.Row( # Team choice row
            dbc.Col(
                html.Div([ # Drop down menu for team selection
                    "Choose a team: ", dcc.Dropdown( 
                    id='dropdown-team', 
                    value='Richmond', 
                    options=[{'label':i, 'value':i} for i in df_teamList['teams'].unique()])
                ]), 
                style={'text-align':'center'},  width={'size':4, 'offset':4})
        ),
    ],style={'margin':'20px'}),
    
    html.Div([
        dbc.Row( # Home and away scatter plot row
            dbc.Col(
                    html.Div( # Graph
                        id='graph-scatter-score', 
                        children=[]), 
            width={'size':10, 'offset':1}),
            style={'border':'50px'}
        ),
    ],style={'margin':'20px'}),
    
    html.Div([
        dbc.Row([ # W, D, L pie chart row
            dbc.Col(
                    html.Div(
                        id='graph-pie-WLD', 
                        children=[]), 
            width={'size':4, 'offset':1}),
           
            dbc.Col([
                html.Div([ # Drop down menu for player selection
                    "Choose a player: ", dcc.Dropdown( 
                    id='dropdown-player',  
                    options=[{'label':i, 'value':i} for i in df_playerList['players'].unique()])
                ]), 
                html.Div( # Player stat card
                    html.P(
                        id='test-output',
                        children='Player stats will appear here\nChoose one to start ^^^'
                    )
                )],
            width={'size':3, 'offset':2})
        ]),
    ]),
    
    # dcc.Store inside the user's current browser session
    dcc.Store(id='store-team-data', data=[], storage_type='memory'), # 'local' or 'session'
    dcc.Store(id='store-team-colour', data=[], storage_type='memory'), # 'local' or 'session'
    dcc.Store(id='store-stat-data', data=[], storage_type='memory'), # 'local' or 'session'
], style={'fontSize': 20, 'background-color':'#DBAE86'})

#### Callback Code ####

# Store dataframe of all game data (df_games) for chosen team when dropdown-team is modified 
@callback(
    Output('store-team-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def storeGameData(value):
    dataset = df_games.loc[(df_games['homeTeam'] == value) | (df_games['awayTeam'] == value)] # Get all rows with chosen team in theme
    dataset["date"] = pd.to_datetime(dataset['date']) 
    dataset = dataset.sort_values(by='date') # Reorder based on date
    return dataset.to_dict()


# Store dataframe of team colours (df_colours)  
@callback(
    Output('store-team-colour', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def storeTeamColours(value):
    return df_colours.to_dict()


# Store dataframe of all stat data (df_stats) for chosen team when dropdown-team is modified 
@callback(
    Output('store-stat-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def storeStatData(value):
    dataset = df_stats.loc[(df_stats['team'] == value)] # Get all rows with chosen team in theme
    return dataset.to_dict()


# Update player list drop down (remember: stored dataset is for chosen team)
@callback(
    Output('dropdown-player', 'options'), # Playes list drop down
    Input('store-stat-data', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def updatePlayerList(data, value):
    df = pd.DataFrame(data) # Get the stored dataframe
    players = df.loc[(df['team']==value)]['displayName'].unique()
    return [{'label':i, 'value':i} for i in players]


# Update player stat card (remember: stored dataset is for chosen team)
@callback(
    Output('test-output', 'children'), # Test ouput label
    Input('dropdown-player', 'value'), # Playes list drop down
    Input('store-stat-data', 'data'), # Data storage
)
def updatePlayerCard(value, data):
    df = pd.DataFrame(data) # Get the stored dataframe
    df_player = df.loc[(df['displayName'] == value)]
    
    player = Player()
    player.name = value
    player.games = df_player['gameNumber'].max()
    player.GPG = round(df_player['Goals'].sum()/player.games,2)
    player.BPG = round(df_player['Behinds'].sum()/player.games,2)
    player.PPG = round((player.GPG*6) + player.BPG,2)
    player.DPG = round(df_player['Disposals'].sum()/player.games,2)
    
    if player.games > 0:
        msg = [html.Br(),
            'Player name:  ', player.name, html.Br(),
            'Games played: ', player.games, html.Br(),
            'Goals/game:   ', player.GPG, html.Br(),
            'Behinds/game: ', player.BPG, html.Br(),
            'Score/game:   ', player.PPG, html.Br(),
            'Disp./game:   ', player.DPG, html.Br()]
    else:
        msg = [html.Br(), 'Player stats will appear here', html.Br(), 'Choose one to start ^^^']
    
    return msg


# Create scatter from stored dataset (remember: stored dataset is for chosen team)
@callback(
    Output('graph-scatter-score', 'children'), # Scatter
    Input('store-team-data', 'data'), # Data storage
    Input('store-team-colour', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def createHAScoreScatter(dataTeam, dataColour, value):
    df = pd.DataFrame(dataTeam) # Get the stored dataframe (for the home team)
    df_colour = pd.DataFrame(dataColour)

    # Get team colours to display 
    colors = [
        df_colour.loc[(df_colour['team'] == value),'colour1'].iloc[0],  
        df_colour.loc[(df_colour['team'] == value),'colour2'].iloc[0],
        df_colour.loc[(df_colour['team'] == value),'colour3'].iloc[0],
    ]

    homeGO = go.Scatter( # Home graph object
        x=df.loc[(df['homeTeam'] == value)]['date'], 
        y=df.loc[(df['homeTeam'] == value)]['homeTeamScore'], 
        name='home', 
        mode='markers',
        textfont_size = 16,
        marker = dict(color=colors[0]))

    awayGO = go.Scatter(# Away graph object
        x=df.loc[(df['awayTeam'] == value)]['date'], 
        y=df.loc[(df['awayTeam'] == value)]['awayTeamScore'], 
        name='away', 
        mode='markers',
        textfont_size = 16,
        marker = dict(color=colors[1]))

    fig = make_subplots() # Useful for editing plot https://plotly.com/python/figure-structure/
    fig.add_trace(homeGO)
    fig.add_trace(awayGO)
    fig.layout.xaxis.title.text = 'date' 
    fig.layout.yaxis.title.text = 'total score'
    fig.layout.title.text = value + ' Home and Away Scores' # How to centre??? 
    return dcc.Graph(figure=fig)


# Create Pie from stored dataset (remember: stored dataset is for chosen team)
@callback(
    Output('graph-pie-WLD', 'children'), # Pie
    Input('store-team-data', 'data'), # Data storage
    Input('store-team-colour', 'data'), # Data storage
    Input('dropdown-team', 'value') # Team choice
)
def createWDLPie(dataTeam, dataColour, value):
    df = pd.DataFrame(dataTeam) # Get the stored dataframe (for the home team)
    df_colour = pd.DataFrame(dataColour)
    
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
    pieNames = ['W - ' + str(pieVals[0]), 'D - ' + str(pieVals[1]), 'L - ' + str(pieVals[2])]
    
    # Make piechart graph object
    fig = go.Figure()

    pie = go.Pie(
            labels = pieNames,
            values = pieVals, 
            sort = False,)
    fig.add_trace(pie)
    
    # Get team colours to display 
    colors = [
        df_colour.loc[(df_colour['team'] == value),'colour1'].iloc[0],  
        df_colour.loc[(df_colour['team'] == value),'colour2'].iloc[0],
        df_colour.loc[(df_colour['team'] == value),'colour3'].iloc[0],
    ]
    
    fig.update_traces(
            hoverinfo = 'label', 
            textinfo = 'percent', 
            textfont_size = 16,
            marker = dict(colors=colors, line=dict(color='#000000', width=2)))
    fig.layout.title.text = value + ' W/D/L Record'
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)',paper_bgcolor='rgba(0, 0, 0, 0)')
    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)
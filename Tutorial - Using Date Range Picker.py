from dash import Dash, html, dcc, Output, Input, callback, dash_table
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Read datafiles and produce data frames
df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
# Reorder based on date
df_games["date"] = pd.to_datetime(df_games["date"])
df_games = df_games.sort_values(by="date")
# Create list of unique teams
df_teamList = pd.DataFrame({
    'c' : df_games['homeTeam'].unique()
})

app.layout = html.Div([
    # Heading
    html.H1('Using the Slider', style={'textAlign':'center'}),
    
    html.Div([ 
        dcc.Dropdown( # Drop down menu
            id='dropdown-home-team', 
            value='Richmond', 
            options=[{'label':i, 'value':i} for i in df_teamList['c'].unique()]),
        
        dcc.DatePickerRange( # Date range picker
            id='date-picker-range',
            min_date_allowed=df_games.iloc[0]['date'],
            max_date_allowed=df_games.iloc[-1]['date'],
            initial_visible_month=df_games.iloc[0]['date'],
            start_date=df_games.iloc[0]['date'],
            end_date=df_games.iloc[-1]['date'])
    ], className='row', style={'width':'25%'}),

    html.Div([ # Graph
        html.Div(id='test-graph', children=[]), 
    ], className='row'),

    # dcc.Store inside the user's current browser session
    dcc.Store(id='store-data', data=[], storage_type='memory') # 'local' or 'session'
])


# Store dataframe of all game data (df_games)
@callback(
    Output('store-data', 'data'), # Data storage
    Input('dropdown-home-team', 'value') # Dropdown
)
def store_data(value):
    dataset = df_games.loc[df_games['homeTeam'] == value]                       # Store the dataset for the home team selected
    return dataset.to_dict()


# Create graph from store df_games
@callback(
    Output('test-graph', 'children'), # Graph
    Input('store-data', 'data'), # Data storage
    Input('date-picker-range', 'start_date'), # Start date
    Input('date-picker-range', 'end_date') # End date
)
def createGraph(data, start_date, end_date):
    home_df = pd.DataFrame(data)                                                # Get the stored dataframe (for the home team)
    home_df = home_df[                                                          # Filter the date range
        (home_df['date'] > start_date) & 
        (home_df['date'] < end_date)]
    score = home_df['homeTeamScore']
    dates = home_df['date']        
    fig1 = px.scatter(x=dates, y=score)
    return dcc.Graph(figure=fig1)


if __name__ == '__main__':
    app.run_server(debug=True)
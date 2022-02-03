from dash import Dash, html, dcc, Output, Input, callback, dash_table
import pandas as pd
import plotly.express as px

app = Dash(__name__)

# Read datafiles and produce data frames
df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
# Reorder based on date
df_games["date"] = pd.to_datetime(df_games["date"])
df_games = df_games.sort_values(by="date")
# Create list of unique teams and column headings
df_teamList = pd.DataFrame({
    'teams' : df_games['homeTeam'].unique(),
})
df_colNames = pd.DataFrame({
    'cols' : df_games.columns
})

app.layout = html.Div([
    # Heading
    html.H1('Using the Slider', style={'textAlign':'center'}),
    
    html.Div([ 
        "Choose a home side: ", dcc.Dropdown( # Drop down menu for home team
            id='dropdown-home-team', 
            value='Richmond', 
            options=[{'label':i, 'value':i} for i in df_teamList['teams'].unique()]),
        
        "Choose x axis: ", dcc.Dropdown( # Drop down menu for x column
            id='dropdown-x-axis', 
            value='date', 
            options=[{'label':i, 'value':i} for i in df_colNames['cols'].unique()]),
        
        "Choose y axis: ", dcc.Dropdown( # Drop down menu for y column
            id='dropdown-y-axis', 
            value='homeTeamScore', 
            options=[{'label':i, 'value':i} for i in df_colNames['cols'].unique()])
        ], style={'marginBottom': 25, 'marginTop': 25, 'width': '30%'}),
    
    html.Div([    
        dcc.DatePickerRange( # Date range picker
            id='date-picker-range',
            min_date_allowed=df_games.iloc[0]['date'],
            max_date_allowed=df_games.iloc[-1]['date'],
            initial_visible_month=df_games.iloc[0]['date'],
            start_date=df_games.iloc[0]['date'],
            end_date=df_games.iloc[-1]['date'])
    ], style={'marginBottom': 25, 'marginTop': 25, 'width': '40%'}),

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
    Input('date-picker-range', 'end_date'), # End date
    Input('dropdown-x-axis', 'value'), # x-axis choice
    Input('dropdown-y-axis', 'value') # y-axis choice
)
def createGraph(data, start_date, end_date, x_axis, y_axis):
    home_df = pd.DataFrame(data)                                                # Get the stored dataframe (for the home team)
    home_df = home_df[                                                          # Filter the date range
        (home_df['date'] > start_date) & 
        (home_df['date'] < end_date)]   
    fig1 = px.scatter(home_df, x=x_axis, y=y_axis)
    return dcc.Graph(figure=fig1)


if __name__ == '__main__':
    app.run_server(debug=True)
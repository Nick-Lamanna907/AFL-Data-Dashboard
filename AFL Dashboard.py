from dash import Dash, html, dcc, Output, Input, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read datafiles and produce data frames
df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
# Reorder based on date
df_games["date"] = pd.to_datetime(df_games["date"])
df_games = df_games.sort_values(by="date")
# Create df of unique teams and column headings
df_teamList = pd.DataFrame({
    'teams' : df_games['homeTeam'].unique(),
})
df_colNames = pd.DataFrame({
    'cols' : df_games.columns
})

app.layout = html.Div([
    dbc.Row(
        dbc.Col(
            html.H1('AFL Data Dashboard', style={'textAlign':'center'}), # Heading
        )
    ),
    
    dbc.Row([ # need this square bracket when multiple Col in one row
        dbc.Col(
            html.Div([ 
                "Choose a home side: ", dcc.Dropdown( # Drop down menu for home team
                id='dropdown-home-team', 
                value='Richmond', 
                options=[{'label':i, 'value':i} for i in df_teamList['teams'].unique()])
            ]), 
        width={'size':3, 'offset':2}), # this means 4 columns wide (each page is made of 12 columns)
        
        dbc.Col(
            html.Div([
                "Choose x axis: ", dcc.Dropdown( # Drop down menu for x column
                id='dropdown-x-axis', 
                value='date', 
                options=[{'label':i, 'value':i} for i in df_colNames['cols'].unique()])
            ]),
        width={'size':3}),
        
        dbc.Col(
            html.Div([
                "Choose y axis: ", dcc.Dropdown( # Drop down menu for y column
                id='dropdown-y-axis', 
                value='homeTeamScore', 
                options=[{'label':i, 'value':i} for i in df_colNames['cols'].unique()])
            ]),
        width={'size':3})
    ]),
    
    dbc.Row([
        dbc.Col(
            html.Div([   
                "Choose a date range: ", dcc.DatePickerRange( # Date range picker
                id='date-picker-range',
                min_date_allowed=df_games.iloc[0]['date'],
                max_date_allowed=df_games.iloc[-1]['date'],
                initial_visible_month=df_games.iloc[0]['date'],
                start_date=df_games.iloc[0]['date'],
                end_date=df_games.iloc[-1]['date'])
            ], style={'margin':'15px'}), # gives a border around the date range picker
        width={'size':5, 'offset':4})
    ]),

    dbc.Row(
        dbc.Col(
            html.Div( # Graph
                html.Div(id='test-graph', children=[]), 
            )
        )
    ),

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
    
    
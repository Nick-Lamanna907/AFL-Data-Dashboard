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
    
    html.Div([ # Drop down menu
        dcc.Dropdown(id='dropdown-home-team', value='Richmond', options=[
            {'label':i, 'value':i} for i in df_teamList['c'].unique()]),
    ], className='row', style={'width':'50%'}),
    
    html.Div([ # Range slider
        dcc.RangeSlider(
            min=0,
            max=10,
            marks={
                0:
                }
            step=10)]),

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
    Input('store-data', 'data') # Data storage
)
def createGraph(data):
    home_df = pd.DataFrame(data)                                                # Get the stored dataframe (for the home team)
    score = home_df['homeTeamScore']
    dates = home_df['date']        
    fig1 = px.scatter(x=dates, y=score)
    return dcc.Graph(figure=fig1)


# Fill drop down list with a list of unique teams
@app.callback(
    Output('output', 'children'),
    Input('dropdown', 'value')
)
def update_output_1(value):
    filtered_df = df_teamList[df_teamList['c'] == value]
    return filtered_df.iloc[0]['c']


if __name__ == '__main__':
    app.run_server(debug=True)
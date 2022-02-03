from dash import Dash, html, dcc, Output, Input, callback, dash_table
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Read datafiles and produce data frames
df_games = pd.read_csv('/Users/nllama/Documents/games.csv')
# Create list of teams
df_teamList = pd.DataFrame({
    'c' : df_games['homeTeam'].unique()
})

app.layout = html.Div([
    html.H1('Sharing Data between callbacks', style={'textAlign':'center'}),
    
    html.Div([
        dcc.Dropdown(id='dropdown-home-team', value='Richmond', options=[
            {'label':i, 'value':i} for i in df_teamList['c'].unique()
        ]),
        html.Div(id='output')
    ], className='row', style={'width':'50%'}),

    html.Div([
        html.Div(id='test-graph', children=[]),
    ], className='row'),

    # dcc.Store inside the user's current browser session
    dcc.Store(id='store-data', data=[], storage_type='memory') # 'local' or 'session'
])


# Store dataframe of all game data (df_games)
@callback(
    Output('store-data', 'data'),
    Input('dropdown-home-team', 'value')
)
def store_data(value):
    dataset = df_games.loc[df_games['homeTeam'] == value]
    return dataset.to_dict()


# Create graph from store df_games
@callback(
    Output('test-graph', 'children'),
    Input('store-data', 'data')
)
def createGraph(data):
    print(type(data))
    home_df = pd.DataFrame(data)
    print(home_df.head())
    print(type(home_df))
    
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
    print(filtered_df)
    return filtered_df.iloc[0]['c']


if __name__ == '__main__':
    app.run_server(debug=True)
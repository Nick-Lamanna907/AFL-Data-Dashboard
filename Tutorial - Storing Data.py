from dash import Dash, html, dcc, Output, Input, callback, dash_table
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Sharing Data between callbacks', style={'textAlign':'center'}),
    html.Div([
        dcc.Dropdown(id='data-set-chosen', multi=False, value='Richmond',
                     options=[{'label':'Richmond', 'value':'Richmond'},
                              {'label':'Sydney', 'value':'Sydney'},
                              {'label':'St Kilda', 'value':'St Kilda'}])
    ], className='row', style={'width':'50%'}),

    html.Div([
        html.Div(id='test-graph', children=[]),
    ], className='row'),

    # dcc.Store inside the user's current browser session
    dcc.Store(id='store-data', data=[], storage_type='memory') # 'local' or 'session'
])


@callback(
    Output('store-data', 'data'),
    Input('data-set-chosen', 'value')
)
def store_data(value):
    # Read datafiles and produce data frames
    df_games = pd.read_csv('/Users/nllama/Documents/games.csv')

    dataset = df_games.loc[df_games['homeTeam'] == value]

    return dataset.to_dict()


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


if __name__ == '__main__':
    app.run_server(debug=True)
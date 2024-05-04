import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

Spotify_df = pd.read_csv('/Users/jay/Documents/spotify-2023jt.csv')


dropped_columns = ['in_shazam_charts', 'in_apple_charts', 'in_spotify_charts']
Spotify_df = Spotify_df.drop(columns=dropped_columns)


Spotify_df.dropna(subset=['in_spotify_playlists', 'artist(s)_name', 'released_year'], inplace=True)

def create_scatter_chart(dataframe, x_axis="playlist_adds", y_axis="streams"):
    scatter_fig = px.scatter(dataframe, x=x_axis, y=y_axis, title="Scatter Plot of Playlist Adds vs Streams")
    return scatter_fig


def create_vertical_bar_chart_by_month(dataframe, x_axis='released_month', y_axis='streams'):
    bar_fig = px.bar(dataframe, x=x_axis, y=y_axis, title='Bar Graph of Streams by Released Month')
    return bar_fig

scatter_fig = create_scatter_chart(Spotify_df)
scatter_fig.show()

def create_bar_chart(dataframe, x_axis='released_month', y_axis='streams'):
    bar_fig = px.bar(dataframe, x=x_axis, y=y_axis, title='Bar Graph Streams by Released month')
    return bar_fig

fig = create_bar_chart(Spotify_df)
fig.show()


app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server= app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Second Page", href="/page-2")),
    ],
    brand="Spotify Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
)

def layout_page_1():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Spotify Dashboard", className="text-center mt-4"), width=12)
        ]),
        dbc.Row([ 
            dbc.Col(dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in Spotify_df['released_year'].unique()],
                value=Spotify_df['released_year'].unique()[0],
                style={'width': '100%', 'display': 'inline-block', 'margin-top': '10px'}
            ), width=6),
            dbc.Col(dcc.Input(
                id='search-input',
                type='text',
                placeholder='Search for songs or artists',
                style={'width': '100%', 'align': 'right', }
            ), width=6, class_name='my-auto')
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='month-bar-chart'), width=6),
            dbc.Col(dcc.Graph(id='playlist-scatter-plot'), width=6)
        ])
    ])
@app.callback(
    Output('month-bar-chart', 'figure'),
    Input('year-dropdown', 'value'), Input('search-input', 'value')
)
def update_month_bar_chart(selected_year, search_query):
    filtered_data = Spotify_df[Spotify_df['released_year'] == selected_year]
    if search_query:
        filtered_data = filtered_data[filtered_data['track_name'].str.contains(search_query, case=False) |
                                      filtered_data['artist(s)_name'].str.contains(search_query, case=False)]
    df_bar = filtered_data.groupby('released_month').sum()['streams'].reset_index()
    fig = px.bar(df_bar, x='released_month', y='streams', title='Streams by Released Month', category_orders={"released_month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    return fig

@app.callback(
    Output('playlist-scatter-plot', 'figure'),
    [Input('year-dropdown', 'value'), Input('search-input', 'value')]
)
def update_scatter_plot(selected_year, search_query):
    filtered_data = Spotify_df[Spotify_df['released_year'] == selected_year]
    if search_query:
        filtered_data = filtered_data[filtered_data['track_name'].str.contains(search_query, case=False) |
                                      filtered_data['artist(s)_name'].str.contains(search_query, case=False)]
    fig = px.scatter(filtered_data, x='playlist_adds', y='streams', color='released_month', title='Playlist Adds vs. Streams')
    return fig


def layout_page_2():
    return html.Div([
        html.H1("Search Songs or Artists", style={"textAlign": "center"}),
        dcc.Input(
            id='search-input-page2',
            type='text',
            placeholder='Enter a song or artist name...',
            style={'width': '100%', 'padding': '10px', 'margin-top': '10px'}
        ),
        html.Div(id='data-table-container', style={'margin-top': '20px'})  # Container for the DataTable
    ])


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-2':
        return layout_page_2()
    else:
        return layout_page_1()
@app.callback(
    Output('search-results', 'children'),
    [Input('search-input', 'value')]
)
def update_search_results(search_value):
    if not search_value:
        return "Please enter a search query to see results."
    filtered_data = Spotify_df[(Spotify_df['track_name'].str.contains(search_value, case=False)) |
                               (Spotify_df['artist(s)_name'].str.contains(search_value, case=False))]
    if filtered_data.empty:
        return "No results found."
    return html.Ul([html.Li(f"{row['track_name']} by {row['artist(s)_name']} - {row['streams']} streams") for index, row in filtered_data.iterrows()])

def display_page(pathname):
    if pathname == '/page-2':
        return layout_page_2()
    else:
        return layout_page_1()  


@app.callback(
    Output('data-table-container', 'children'),
    [Input('search-input-page2', 'value')]
)
def update_data_table(search_value):
    if not search_value:
        return "Please enter a search query to see results."
    filtered_data = Spotify_df[(Spotify_df['track_name'].str.contains(search_value, case=False)) |
                               (Spotify_df['artist(s)_name'].str.contains(search_value, case=False))]
    if filtered_data.empty:
        return "No results found."
    return dash_table.DataTable(
        data=filtered_data.to_dict('records'),
        columns=[{"name": i, "id": i} for i in filtered_data.columns],
        page_size=10,  # Display 10 records per page
        style_table={'height': '400px', 'overflowY': 'auto'},
        filter_action="native", 
        sort_action="native",  
        sort_mode="multi"  
    )

if __name__ == '__main__':
    app.run_server(debug=True)

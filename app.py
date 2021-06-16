import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = px.data.gapminder()

app.layout = html.Div([html.Div(dcc.Graph(id='map', clickData={'points': [{'hovertext': 'Japan'}]})),
            dcc.Slider(id="year_selector",
            min=df['year'].min(), max=df['year'].max(), value=df['year'].max(), step=None,
            marks={str(year): str(year) for year in df['year'].unique()}),
            html.Div([dcc.Dropdown(id="dropdown1", options=[{'label': i, 'value': i} for i in ['lifeExp', 'pop', 'gdpPercap']], value="pop"), 
            dcc.Graph(id='graph1'), 
            dcc.Dropdown(id="dropdown2", options=[{'label': i, 'value': i} for i in ['lifeExp', 'pop', 'gdpPercap']], value='lifeExp'), 
            dcc.Graph(id='graph2')])
            ])

@app.callback(Output(component_id='map', component_property='figure'), 
            Input('year_selector','value')
)
def render_map(year) :
    dff = df[df['year']==year]
    fig = px.choropleth(dff, locations="iso_alpha", color="pop", hover_name="country", projection='natural earth')   
    return fig

@app.callback(Output('graph1', 'figure'), [Input('map', 'clickData'), Input('dropdown1', 'value')])
def display_graph1(clickValue, type='pop'):
    dff = df[df['country']==clickValue['points'][0]['hovertext']]
    fig = px.scatter(x=dff['year'], y=dff[str(type)])
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback(Output('graph2', 'figure'), [Input('map', 'clickData'), Input('dropdown2', 'value')])
def display_graph2(clickValue, type='lifeExp'):
    dff = df[df['country']==clickValue['points'][0]['hovertext']]
    fig = px.scatter(x=dff['year'], y=dff[str(type)])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

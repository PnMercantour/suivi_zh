import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas
from pathlib import Path


df = pandas.read_csv(
    Path(Path(__file__).parent, 'assets', 'habitat.csv'))

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Identifiant zone humide"),
    dcc.Input(
        id="id_zh",
        type='number',
        value=105
    ),
    # html.P("zh:"),
    # dcc.Dropdown(
    #     id='code',
    #     value='code',
    #     options=[{'value': x, 'label': x}
    #              for x in ['smoker', 'day', 'time', 'sex']],
    #     clearable=False
    # ),
    # html.P("Values:"),
    # dcc.Dropdown(
    #     id='values',
    #     value='total_bill',
    #     options=[{'value': x, 'label': x}
    #              for x in ['total_bill', 'tip', 'size']],
    #     clearable=False
    # ),
    dcc.Graph(id="pie-chart", figure=px.pie(df[df["id_zh"] == 374],
              values='proportion', names='code')),
])


@app.callback(
    Output("pie-chart", "figure"),
    Input("id_zh", "value"))
def generate_chart(id_zh):
    print('callback', id_zh)
    fig = px.pie(df[df["id_zh"] == id_zh], values='proportion', names='code')
    return fig


app.run_server(debug=True)

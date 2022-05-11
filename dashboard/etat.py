import plotly.express as px
from dash import dcc, html, callback, Output
import dash_bootstrap_components as dbc
import pandas
import numpy as np
import config
import data
import carte

df = data.detail

color_pie_chart = {
    'bon': 'green',
    'moyen': 'orange',
    'mauvais': 'red',
}

graph = dcc.Graph(
    figure=px.pie(
        data_frame=df,
        values='surface',
        names='etat',
        color='etat',
        color_discrete_map=color_pie_chart,
    ))

component = dbc.Card([
    dbc.CardHeader('Etat de conservation des habitats (% de surface)'),
    dbc.CardBody([
        graph
    ]),
])

output = {
    'figure': Output(graph, "figure")
}
# @callback(output=dict(
#     figure=Output(graph, "figure"),
# ),
#     inputs=dict(context=carte.context),
# )
def update(state):
    id_site = state['site']
    id_vallee = state['vallee']
    if id_site is not None:
        the_df = df[df['id_site'] == id_site]
    elif id_vallee is not None:
        the_df = df[df['id_vallee'] == id_vallee]
    else:
        the_df = df
    return {
        'figure': px.pie(
            data_frame=the_df,
            values='surface',
            names='etat',
            color='etat',
            color_discrete_map=color_pie_chart,
        ),
    }

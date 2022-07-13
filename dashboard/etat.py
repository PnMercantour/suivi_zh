# import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Output
import dash_bootstrap_components as dbc
import config
from data import zh_data, list_sites
from common import info_header

color_pie_chart = {
    'bon': 'green',
    'moyen': 'orange',
    'mauvais': 'red',
}

graph = dcc.Graph(responsive=True, style={'height': '100%'})

component = dbc.Card([
    dbc.CardHeader(info_header(
        'Etat', '#etat-de-conservation')),
    dbc.CardBody([
        graph
    ]),
], class_name='h-100')

output = {
    'figure': Output(graph, "figure")
}


def update(state):
    id_site = state['site']
    id_vallee = state['vallee']
    surfaces = {}
    all_sites = False
    if id_site is not None:
        site_list = [id_site]
    elif id_vallee is not None:
        site_list = list_sites(id_vallee)
    else:
        all_sites = True
    for zh in zh_data.values():
        if all_sites or (zh['id_site'] in site_list):
            surfaces[zh['etat']] = zh['surface'] + surfaces.get(zh['etat'], 0)
    values = [
        surfaces.get('bon', 0),
        surfaces.get('moyen', 0),
        surfaces.get('mauvais', 0),
    ]

    fig = go.Figure(go.Pie(
        sort=False,
        values=values,
        labels=['bon', 'moyen', 'mauvais'],
        marker=dict(colors=['green', 'orange', 'red', ]),
        direction='clockwise',
        showlegend=False,
        textinfo='none',
        # hoverinfo="skip",
        # hovertemplate="<br>Surface: %{text}</br>",
        # text=[str(value) + ' m2' for value in values],
    ),
    )
    fig.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
    fig.update_layout(paper_bgcolor='rgb(50,56,62)')  # TODO : do it properly
    # fig.update_layout(legend_title_text='Etat')
    # fig.update_layout(height=200)
    return {
        'figure': fig,
    }

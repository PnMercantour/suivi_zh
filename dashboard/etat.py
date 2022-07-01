# import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Output
import dash_bootstrap_components as dbc
import config
from data import zh_data, list_sites
import carte


color_pie_chart = {
    'bon': 'green',
    'moyen': 'orange',
    'mauvais': 'red',
}

graph = dcc.Graph(
)

component = dbc.Card([
    dbc.CardHeader('Etat de conservation'),
    dbc.CardBody([
        graph
    ]),
])

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
        hovertemplate="<br>Surface: %{text}</br>",
        text=[str(value) + ' m2' for value in values],
    ))
    fig.update_layout(legend_title_text='Etat')
    return {
        'figure': fig,
    }

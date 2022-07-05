import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, Output
import dash_bootstrap_components as dbc
import pandas
from config import data_path
from data import site_data, list_sites, habitat_data, zh_data, ref_habitat, get_site_id

color_pie_chart = {
    'A': 'lightcyan',
    'B': 'cyan',
    'C': 'lightblue',
    'D': 'blue',
    'F': 'royalblue',
    'G': 'darkblue',
    'H': 'lightrange',
    'I': 'orange',
    'J': 'lightred',
    'K': 'red',
    'M': 'darkred',
    'N': 'lightgreen',
    'P': 'green',
    'Q': 'darkgreen',
    'R': 'grey',
    'S': 'black',
}

graph = dcc.Graph()

component = dbc.Card([
    dbc.CardHeader('Habitat'),
    dbc.CardBody([
        graph
    ]),
])

output = {
    'figure': Output(graph, "figure")
}


# def update(state):
#     id_vallee = state['vallee']
#     id_site = state['site']
#     id_zh = state['zh']
#     surfaces = {}
#     def update_surfaces(h, zh):
#         surfaces[h['habitat']] = zh['surface'] * \
#                     h['proportion'] /100 + surfaces.get(h['habitat'], 0)
#     if id_zh is not None:
#         zh = zh_data[id_zh]
#         for h in habitat_data:
#             if h['id_zh'] == id_zh:
#                 update_surfaces(h, zh)
#     else:
#         all_sites = False
#         if id_site is not None:
#             site_list = [id_site]
#         elif id_vallee is not None:
#             site_list = list_sites(id_vallee)
#         else:
#             all_sites = True
#         for h in habitat_data:
#             if all_sites or (h['id_site'] in site_list):
#                 zh = zh_data[h['id_zh']]
#                 update_surfaces(h, zh)
#     values = [round(value) for value in surfaces.values()]
#     fig = go.Figure(go.Pie(
#         sort=True,
#         values=values,
#         labels=list(surfaces.keys()),
#         # marker=dict(colors=['green', 'orange', 'red', ]),
#         # rotation=360,
#         direction='clockwise',
#         hovertemplate="<br>Surface: %{text}</br>",
#         text=[str(value) + ' m2' for value in values],
#     ))
#     fig = go.Figure(data=[
#         go.Bar(
#             name='Tous les états',
#             x=list(surfaces.keys()),
#             y=values,
#             )
#     ])
#     return {
#         'figure': fig,
#     }
def update(state):
    id_vallee = state['vallee']
    id_site = state['site']
    id_zh = state['zh']
    etats = {'bon': {}, 'moyen': {}, 'mauvais': {}}
    the_color = {'bon': 'green', 'moyen': 'orange', 'mauvais': 'red'}

    print('update habitat', state)

    def update_surfaces(h, zh):
        surfaces = etats[zh['etat']]
        surfaces[h['id_type']] = zh['surface'] * \
            h['proportion'] / 100 + surfaces.get(h['id_type'], 0)
    if id_zh is not None:
        zh = zh_data[id_zh]
        for h in habitat_data.values():
            if h['id_zh'] == id_zh:
                update_surfaces(h, zh)
    else:
        all_sites = False
        if id_site is not None:
            site_list = [id_site]
        elif id_vallee is not None:
            site_list = list_sites(id_vallee)
        else:
            all_sites = True
        for h in habitat_data.values():
            print(h)
            if all_sites or (get_site_id(h['id_zh']) in site_list):
                zh = zh_data[h['id_zh']]
                print(zh)
                update_surfaces(h, zh)
    etats = {etat: {id: etats[etat].get(id, 0) for id in sorted(
        ref_habitat.keys())}for etat in ['bon', 'moyen', 'mauvais']}
    layout = go.Layout({
        'xaxis': {
            'title': 'Habitats',
            # 'tickangle':45,
            # 'ticks': '',
            'showticklabels': False,
        },
        'yaxis': {'title': 'Surface (m2)'},
    })
    fig = go.Figure(data=[
        go.Bar(
            name=etat,
            # x=list(l.keys()),
            x=[ref_habitat[id]['label'] for id in sorted(
                ref_habitat.keys())],
            y=[round(value) for value in l.values()],
            marker_color=the_color[etat],
            # hoverinfo=['text'],
            # hovertemplate="Habitat %{x}: [%{text}] %{y}<br>",
            # hovertext=[ref_habitat.get(habitat, {'libelle': 'non défini'})[
            # 'libelle'] for habitat in list(l.keys())]
        ) for (etat, l) in etats.items()
    ],            layout=layout,
    )
    fig.update_layout(barmode='stack', legend_title_text='Etat')
    # fig.update_xaxes(ticktext=list(ref_habitat.keys()))
    # TODO use tickvals to align custom text
    return {
        'figure': fig,
    }

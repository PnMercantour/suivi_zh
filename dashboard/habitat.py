import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, Output
import dash_bootstrap_components as dbc
from config import data_path
from data import site_data, list_sites, habitat_data, zh_data, ref_habitat, get_site_id
from common import info_header

graph = dcc.Graph(responsive=True, style={'height': '100%'})

component = dbc.Card([
    dbc.CardHeader(info_header('Habitat', '#habitat')),
    dbc.CardBody([
        graph
    ]),
], class_name='h-100')

output = {
    'figure': Output(graph, "figure")
}

# on élimine les habitats hors liste (pas de label)
interest = sorted([habitat for habitat in ref_habitat.values()if habitat['label'] is not None],
                  key=lambda habitat: habitat['code'])
print(interest)


def update(state):
    id_vallee = state['vallee']
    id_site = state['site']
    id_zh = state['zh']
    etats = {'bon': {}, 'moyen': {}, 'mauvais': {}}
    the_color = {'bon': 'green', 'moyen': 'orange', 'mauvais': 'red'}

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
            if all_sites or (get_site_id(h['id_zh']) in site_list):
                zh = zh_data[h['id_zh']]
                update_surfaces(h, zh)
    etats = {etat: {id: etats[etat].get(id, 0) for id in [h['id'] for h in interest]}for etat in [
        'bon', 'moyen', 'mauvais']}
    layout = go.Layout({
        'xaxis': {
            'title': 'Habitats',
            # 'showticklabels': False,
            'color': 'rgb(170,170,170)',
        },
        'yaxis': {
            # https://plotly.com/python-api-reference/generated/plotly.graph_objects.layout.html#plotly.graph_objects.layout.YAxis
            'title': 'Surface (<em>m<sup>2</sup></em>)',
            'color': 'rgb(170,170,170)',
        },
        'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
        'paper_bgcolor': 'rgb(50,56,62)',
        'plot_bgcolor': 'rgb(50,56,62)',
    })

    def aux(value):
        print(value)
        return 'foo'

    fig = go.Figure(data=[
        go.Bar(
            name=etat,
            x=[h['code'] for h in interest],
            y=[round(value) for value in l.values()],
            marker_color=the_color[etat],
            showlegend=False,
            # hovertext=aux([round(value) for value in l.values()]),
            hovertext=[
                f"{h['label']} <br> {round(l[h['id']])} m<sup>2</sup>" for h in interest],
            hoverinfo='text',
            # hovertemplate="Habitat %{x}: [%{text}] %{y}<br>",
            # hovertext=[ref_habitat.get(habitat, {'libelle': 'non défini'})[
            # 'libelle'] for habitat in list(l.keys())]
        ) for (etat, l) in etats.items()
    ],            layout=layout,
    )
    fig.update_layout(barmode='stack')
    return {
        'figure': fig,
    }

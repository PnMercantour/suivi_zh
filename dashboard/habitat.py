import plotly.graph_objects as go
from dash import dcc, Output
import dash_bootstrap_components as dbc
from data import list_sites, habitat_data, zh_data, ref_habitat, get_site_id
from common import info_header, info_surface

graph = dcc.Graph(responsive=True, config={'displayModeBar': False}, style={'height': '100%'})

collapsible_card = dbc.Collapse(dbc.Card([
    dbc.CardHeader(info_header(
        "Habitats", '#habitat', title="""Types d'habitat d'intérêt communautaire
de la zone d'étude.
Cliquer pour consulter la documentation""")),
    dbc.CardBody([
        graph
    ]),
], class_name='h-100'), class_name='h-100')

component = collapsible_card
output = {
    'visible': Output(collapsible_card, 'is_open'),
    'figure': Output(graph, "figure")
}

# on élimine les habitats hors liste (pas de label)
interest = sorted([habitat for habitat in ref_habitat.values()if habitat['label'] is not None],
                  key=lambda habitat: habitat['code'])

STATUS_COLORS = {
    'bon': '#55d187',
    'moyen': '#f4be5b',
    'mauvais': '#f26b6c',
}

STATUS_LABELS = {
    'bon': 'Bon',
    'moyen': 'Moyen',
    'mauvais': 'Mauvais',
}


def update(state):
    id_vallee = state['vallee']
    id_site = state['site']
    id_zh = state['zh']
    etats = {'bon': {}, 'moyen': {}, 'mauvais': {}}

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
    fig = go.Figure()
    habitat_codes = [h['code'] for h in interest]

    for etat in ['bon', 'moyen', 'mauvais']:
        surfaces = etats[etat]
        fig.add_trace(go.Bar(
            name=STATUS_LABELS[etat],
            x=habitat_codes,
            y=[round(surfaces[h['id']]) for h in interest],
            marker_color=STATUS_COLORS[etat],
            marker_line=dict(color='rgba(17,25,34,0.75)', width=0.6),
            customdata=[
                [h['label'], info_surface(surfaces[h['id']])] for h in interest
            ],
            hovertemplate=(
                '<b>%{customdata[0]}</b>'
                f'<br>Etat : {STATUS_LABELS[etat]}'
                '<br>Surface : %{customdata[1]}'
                '<extra></extra>'
            ),
        ))

    fig.update_layout(
        barmode='stack',
        bargap=0.18,
        margin={'l': 8, 'r': 8, 't': 34, 'b': 54},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.02)',
        font=dict(color='#dfe8f6', size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.02,
            xanchor='left', x=0,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor='#111922',
            bordercolor='#2c3b52',
            font=dict(color='#dfe8f6'),
        ),
    )
    fig.update_xaxes(
        title_text='Habitats',
        title_font=dict(color='#9eb0c8'),
        tickfont=dict(color='#dfe8f6', size=10),
        tickangle=-32,
        showline=True,
        linecolor='rgba(223,232,246,0.25)',
    )
    fig.update_yaxes(
        title_text='Surface (<em>m<sup>2</sup></em>)',
        title_font=dict(color='#9eb0c8'),
        tickfont=dict(color='#9eb0c8'),
        gridcolor='rgba(223,232,246,0.14)',
        separatethousands=True,
        zeroline=False,
    )
    return {
        'visible': any([round(value) != 0 for (etat, l) in etats.items() for value in l.values()]),
        'figure': fig,
    }

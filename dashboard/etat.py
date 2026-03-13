# import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, Output
import dash_bootstrap_components as dbc
from data import zh_data, list_sites
from common import info_header, info_surface

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

graph = dcc.Graph(responsive=True, config={'displayModeBar': False}, style={'height': '100%'})

component = dbc.Card([
    dbc.CardHeader(info_header(
        'Etat', '#etat-de-conservation', title="""Etat de conservation des zones humides
de la zone d'étude en % de surface.
Cliquer pour consulter la documentation""")),
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
    ordered_states = ['bon', 'moyen', 'mauvais']
    values = [surfaces.get(state, 0) for state in ordered_states]
    labels = [STATUS_LABELS[state] for state in ordered_states]
    hover_surfaces = [info_surface(value) for value in values]
    total_surface = sum(values)
    total_surface_label = info_surface(total_surface) or '0 m<sup>2</sup>'

    fig = go.Figure(go.Pie(
        sort=False,
        hole=0.62,
        values=values,
        labels=labels,
        marker=dict(
            colors=[STATUS_COLORS[state] for state in ordered_states],
            line=dict(color='rgba(17,25,34,0.9)', width=2),
        ),
        direction='clockwise',
        showlegend=True,
        textinfo='none',
        customdata=hover_surfaces,
        hovertemplate='<b>%{label}</b><br>Surface : %{customdata}<br>%{percent}<extra></extra>',
    ))
    fig.update_layout(
        margin={'l': 6, 'r': 6, 't': 8, 'b': 8},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        annotations=[dict(
            x=0.5,
            y=0.5,
            showarrow=False,
            xanchor='center',
            yanchor='middle',
            text=f"<b>{total_surface_label}</b><br><span style='color:#9eb0c8;font-size:11px'>surface totale</span>",
        )],
    )
    return {
        'figure': fig,
    }

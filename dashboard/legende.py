import dash_bootstrap_components as dbc
from dash import html
from common import info_header


STATUS_COLORS = {
    'bon': '#55d187',
    'moyen': '#f4be5b',
    'mauvais': '#f26b6c',
}


def surface(color):
    return html.I(className="fa-solid fa-square",
                  style={"color": color})


def pastille(color):
    return html.I(className="fa-solid fa-circle",
                  style={"color": color})


def contour(color):
    return html.I(className="fa-regular fa-circle",
                  style={"color": color})


def legend_item(icon, label):
    return dbc.Row([dbc.Col(icon, md=2), dbc.Col(label, md=10)])


component = dbc.Card([
    dbc.CardHeader(info_header('Légende', '#')),
    dbc.CardBody(dbc.Row(dbc.Col([
        "Etat de conservation",
        legend_item(surface(STATUS_COLORS['bon']), 'Bon état'),
        legend_item(surface(STATUS_COLORS['moyen']), 'Etat moyen'),
        legend_item(surface(STATUS_COLORS['mauvais']), 'Etat dégradé'),
        html.Hr(),
        legend_item(contour('purple'), 'Site rhomeo'),
        legend_item(contour('blue'), 'Espace de bon fonctionnement'),
        legend_item(contour('black'), 'Défens'),
        legend_item(contour('magenta'), 'Altération'),

    ]),),  class_name='h-100 overflow-auto'),
], class_name='h-100')

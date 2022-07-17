import dash_bootstrap_components as dbc
from dash import html
from common import info_header


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
        legend_item(surface('green'), 'Bon état'),
        legend_item(surface('orange'), 'Etat moyen'),
        legend_item(surface('red'), 'Etat dégradé'),
        html.Hr(),
        legend_item(contour('purple'), 'Site rhomeo'),
        legend_item(contour('blue'), 'Espace de bon fonctionnement'),
        legend_item(contour('black'), 'Défens'),
        legend_item(contour('magenta'), 'Altération'),

    ]),),  class_name='h-100 overflow-auto'),
], class_name='h-100')

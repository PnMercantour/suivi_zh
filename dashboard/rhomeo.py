import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte
from common import info_header
from data import site_data, rhomeo_site_data


body = html.Div()

collapsible_card = dbc.Collapse(dbc.Card([
    dbc.CardHeader(info_header('Suivi Rhomeo', '#Rhomeo')),
    dbc.CardBody(body),
]))

component = collapsible_card

zh_type_directory = {
    "7.1": "Zone humide d'altitude",
    "7.2": "Tourbière acide",
    "7.3": "Tourbière alcaline",
}


def zh_site_label(type):
    label = zh_type_directory.get(type, "Non renseigné")
    return f'{label} ({type})'


def display_row(key, value):
    return dbc.Row([dbc.Col(key, md=5), dbc.Col(value, md=7)])


output = {
    'visible': Output(collapsible_card, 'is_open'),
    'body': Output(body, 'children'),
}


def update(state):
    id_site = state['site']
    if id_site is None or site_data[id_site]['rhomeo'] is None:
        return {
            'visible': False,
            'body': None,
        }
    code = site_data[id_site]['rhomeo']
    obj = rhomeo_site_data[code]
    return {
        'visible': True,
        'body': [
            display_row('code site', obj['code']),
            display_row('Type de zone humide', zh_site_label(obj['type'])),
            display_row('Référent', obj['referent']),
            display_row('Structure', obj['org']),
        ],
    }

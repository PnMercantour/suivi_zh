import dash_bootstrap_components as dbc
from dash import Input, Output, callback, callback_context, html, no_update, dcc
import dash_bootstrap_components as dbc

from common import info_header
from data import get_vallee_id, vallee_data, site_data
import notice
import carte


def n_sites(l):
    if l is None:
        return ''
    if len(l) == 1:
        return '(1 site)'
    return f'({len(l)} sites)'


vallee_dropdown = dcc.Dropdown(options=[{'label': f"{vallee['nom_vallee']} {n_sites(vallee['ids_site'])}", 'value': vallee['id']}
                               for vallee in vallee_data.values()], placeholder="Choisir une vallée")

site_dropdown = dcc.Dropdown(options=[{'label': site['nom_site'], 'value': site['id']}
                             for site in site_data.values()], placeholder="Choisir un site")

component = dbc.Card([
    dbc.CardHeader(info_header("Zone d'étude", '#zone-détude')),
    dbc.CardBody([
        dbc.Row(['Vallée', vallee_dropdown]),
        html.Hr(),
        dbc.Row(['Site', site_dropdown]),
    ]),
])


input = {
    'vallee': Input(vallee_dropdown, 'value'),
    'site': Input(site_dropdown, 'value'),
}


def process(vallee, site):
    triggers = [trigger['prop_id'] for trigger in callback_context.triggered]
    if any([site_dropdown.id in trigger for trigger in triggers]):
        if site:
            return{
                'vallee': get_vallee_id(site),
                'site': site,
            }
        else:
            return{
                'vallee': vallee,
                'site': None,
            }
    if any([vallee_dropdown.id in trigger for trigger in triggers]):
        return{
            'vallee': vallee,
            'site': None,
        }
    return None


output = {
    'vallee': Output(vallee_dropdown, 'value'),
    'site': Output(site_dropdown, 'value'),
    'site_options': Output(site_dropdown, 'options'),
}


def update(state):
    if state['vallee'] is None:
        return {
            'vallee': None,
            'site': None,
            'site_options': [{'label': site['nom_site'], 'value': site['id']} for site in site_data.values()]
        }
    vallee_id = state['vallee']
    vallee = vallee_data[vallee_id]
    sites = [site_data[id] for id in vallee['ids_site']]
    return {
        'vallee': vallee_id,
        'site': state['site'],
        'site_options': [{'label': site['nom_site'], 'value': site['id']} for site in sites]
    }

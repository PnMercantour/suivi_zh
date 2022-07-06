import dash_bootstrap_components as dbc
from dash import Input, Output, callback, callback_context, html, no_update, dcc
from data import get_vallee_id, vallee_data, site_data
import notice
import carte


vallee_dropdown = dcc.Dropdown(options=[{'label': vallee['nom_vallee'], 'value': vallee['id']}
                               for vallee in vallee_data.values()], placeholder="Choisir une vallée")

site_dropdown = dcc.Dropdown(options=[{'label': site['nom_site'], 'value': site['id']}
                             for site in site_data.values()], placeholder="Choisir un site")

component = dbc.Card([
    dbc.CardHeader("Zone d'étude"),
    dbc.CardBody([
        vallee_dropdown,
        html.Hr(),
        site_dropdown,
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
    return {
        'vallee': state['vallee'],
        'site': state['site'],
        'site_options': [{'label': site['nom_site'], 'value': site['id']} for site in site_data.values() if site['id_vallee'] == state['vallee']]
    }

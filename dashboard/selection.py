import dash_bootstrap_components as dbc
from dash import Input, Output, callback, callback_context, html, no_update, dcc
from config import vallees, sites
from data import get_site_vallee
import notice
import carte


vallee_dropdown = dcc.Dropdown(options=[{'label': vallee['nom_vallee'], 'value': vallee['id_vallee']}
                               for vallee in vallees], placeholder="Choisir une vallée")

site_dropdown = dcc.Dropdown(options=[{'label': site['nom_site'], 'value': site['id_site']}
                             for site in sites], placeholder="Choisir un site")

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
                'site': site,
                'vallee': get_site_vallee(site)
            }
        else:
            return{
                'site': None,
                'vallee': vallee,
            }
    if any([vallee_dropdown.id in trigger for trigger in triggers]):
        return{
            'site': None,
            'vallee': vallee,
        }
    return None


output = {
    'vallee': Output(vallee_dropdown, 'value'),
    'site': Output(site_dropdown, 'value'),
    'site_options': Output(site_dropdown, 'options'),
}


def update(vallee, site, zh):
    if vallee is None:
        return {
            'vallee': None,
            'site': None,
            'site_options': [{'label': site['nom_site'], 'value': site['id_site']} for site in sites]
        }
    return {
        'vallee': vallee,
        'site': site,
        'site_options': [{'label': site['nom_site'], 'value': site['id_site']} for site in sites if site['id_vallee'] == vallee]
    }

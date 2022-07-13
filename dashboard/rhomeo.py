import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte
from common import info_header
from data import site_data, rhomeo_site_data, rhomeo_result_data


rhomeo_summary = html.Div()

rows = html.Tbody()

collapsible_card = dbc.Collapse(dbc.Card([
    dbc.CardHeader(info_header('Suivi Rhomeo', '#rhomeo')),
    dbc.CardBody([
        rhomeo_summary,
        html.Br(),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Indicateur"),
                html.Th("Point de mesure"),
                html.Th('Valeur'),
            ])),
            rows,
        ]),
    ])
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


def display_info(key, value):
    return dbc.Row([dbc.Col(key, md=5), dbc.Col(value, md=7)])


def indicateur(results, i):
    rows = [result['value'] for result in results if result['name'] == i]
    if rows:
        return round(sum(rows)/len(rows))


def indicateurs(results):
    return([html.Tr([
        html.Td(result['name']),
        html.Td(result['location']),
        html.Td(result['value']),
    ]) for result in results
    ])


output = {
    'visible': Output(collapsible_card, 'is_open'),
    'info': Output(rhomeo_summary, 'children'),
    'rows': Output(rows, 'children'),
}


def update(state):
    id_site = state['site']
    if id_site is None or site_data[id_site]['rhomeo'] is None:
        return {
            'visible': False,
            'info': no_update,
            'rows': no_update,
        }
    code = site_data[id_site]['rhomeo']
    obj = rhomeo_site_data[code]
    results = [result for result in rhomeo_result_data.values()
               if code in result['location']]
    return {
        'visible': True,
        'info': [
            display_info('code site', obj['code']),
            display_info('Type de zone humide', zh_site_label(obj['type'])),
            display_info('Référent', obj['referent']),
            display_info('Structure', obj['org']),
            display_info('Indicateur I01', indicateur(results, 'I01')),
            display_info('Indicateur I02', indicateur(results, 'I02')),
            display_info('Indicateur I06', indicateur(results, 'I06')),
            display_info('Indicateur I08', indicateur(results, 'I08')),
        ],
        'rows': indicateurs(results),
    }

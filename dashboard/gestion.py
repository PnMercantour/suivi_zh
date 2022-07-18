import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte
from common import info_header


component = dbc.Card([
    dbc.CardHeader(info_header('Gestion', '#mesures-de-gestion', title="""Mesures de gestion
relatives à la zone d'étude.
Cliquer pour consulter la documentation""")),
    dbc.CardBody([
        notice.component,
    ], class_name='h-100 overflow-auto'),
], class_name='h-100')

output = {
    'notice': notice.output,
}


def update(state):
    return {
        'notice': notice.update(state),
    }

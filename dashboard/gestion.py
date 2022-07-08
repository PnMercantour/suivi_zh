import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte
from common import info_header


component = dbc.Card([
    dbc.CardHeader(info_header('Mesures de gestion', '#mesures-de-gestion')),
    dbc.CardBody([
        notice.component,
    ]),
])

output = {
    'notice': notice.output,
}


def update(state):
    return {
        'notice': notice.update(state),
    }

import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte


component = dbc.Card([
    dbc.CardHeader('Mesures de gestion'),
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

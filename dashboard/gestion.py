import dash_bootstrap_components as dbc
from dash import Output, callback, callback_context, html, no_update
import config
import notice
import carte


component = dbc.Card([
    dbc.CardHeader('Notices de gestion'),
    dbc.CardBody([
        notice.component,
    ]),
])


@callback(output=dict(
    notice=notice.output,
),
    inputs=dict(context=carte.context))
def update_gestion(context):
    return {
        'notice': notice.update_component(context),
    }

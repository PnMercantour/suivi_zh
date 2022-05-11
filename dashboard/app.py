from dash import callback, callback_context, html, dcc, Input, State, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from config import app
import selection
import carte
import carte_site
import gestion
# import habitat
import etat

client_state = dcc.Store(id='zh_client_state', storage_type='local')

app.layout = dbc.Container([
    client_state,
    html.Div(style={'height': '3vh'}),
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url(
                'logo-structure.png'), width='100%'),
            html.H1("Les zones humides"),
            selection.component,
            carte.component,
            gestion.component,
        ], md=3),
        dbc.Col([
            carte_site.component,
            # dbc.Row([
            #     # dbc.Col(gestion.component, md=6),
            #     dbc.Col(habitat.component, md=6),
            #     dbc.Col(etat.component, md=6),
            # ]),
        ], md=6,
        ),
        dbc.Col([
            etat.component,
            # habitat.component,
        ], md=3)
    ],
        align='top', justify='evenly',
    ),
], fluid=True)


@callback(
    output={
        'client_state': Output(client_state, 'data'),
        'carte': carte.output,
        'selection': selection.output,
        'carte_site': carte_site.output
    },
    inputs={
        'client_state': State(client_state, 'data'),
        'carte_input': carte.input,
        'selection_input': selection.input,
        'carte_site_input': carte_site.input
    }
)
def update(client_state, carte_input, selection_input, carte_site_input):
    if client_state is None: # No cookie, needs initialization
        client_state= {
            'vallee':None,
            'site':None,
            'zh':None,
        }
    changes = selection.process(**selection_input)
    if changes is None:
        changes = carte.process(client_state, **carte_input)
    if changes is None:
        changes = carte_site.process(client_state, **carte_site_input)
    new_state= client_state if changes is None else {**client_state, **changes}
    return {
        'client_state': new_state,
        'carte': carte.update(new_state),
        'carte_site': carte_site.update(new_state, client_state, changes is None),
        'selection': selection.update(new_state)
    }


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')

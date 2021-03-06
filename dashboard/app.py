from dash import callback, callback_context, html, dcc, Input, State, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from config import app
import selection
import carte
import carte_site
import gestion
import habitat
import etat
import rhomeo
import legende
from common import info_header

client_state = dcc.Store(id='zh_client_state', storage_type='local')

app.layout = dbc.Container([
    client_state,
    html.Div(style={'height': '1vh'}),
    dbc.Row([
        dbc.Col([
            html.Div([html.Img(src=app.get_asset_url(
                'logo-structure.png'),  style={'height': '60%'}), html.H3('Les Zones humides')],
                style={'height': '25vh'}),
            html.Div(legende.component, style={'height': '35vh'}),
            html.Div(selection.component, style={'height': '28vh'}),
            html.Div(style={'height': '1vh'}),
            dbc.Row([
                dbc.Col(html.Img(src=app.get_asset_url(
                    'logo_rfae-recadre.jpg'), height='100%'), md=6, style={'height': '100%'}),
                dbc.Col(html.Img(src=app.get_asset_url(
                    'picto_engage_pour_leau_valide.png'), height='100%'), md=6, style={'height': '100%'}),
            ], style={'height': '8vh'}),
            html.Div(style={'height': '1vh'}),

        ], md=3),
        dbc.Col([
            html.Div(carte_site.component, style={'height': '60vh'}),
            dbc.Row([
                dbc.Col(etat.component, md=4, style={'height': '100%'}),
                dbc.Col(habitat.component, md=8, style={'height': '100%'}),
            ], style={'height': '38vh'}, className='g-0'),
        ], md=6),
        dbc.Col([
            html.Div(gestion.component, style={'height': '25vh'}),
            html.Div(carte.component, style={'height': '35vh'}),
            html.Div(rhomeo.component, style={'height': '38vh'}),
        ], md=3)
    ],
        align='start', justify='evenly', className='g-0'
    ),
], fluid=True)


@ callback(
    output={
        'client_state': Output(client_state, 'data'),
        'carte': carte.output,
        'selection': selection.output,
        'carte_site': carte_site.output,
        'gestion': gestion.output,
        'etat': etat.output,
        'habitat': habitat.output,
        'rhomeo': rhomeo.output,
    },
    inputs={
        'client_state': State(client_state, 'data'),
        'carte_input': carte.input,
        'selection_input': selection.input,
        'carte_site_input': carte_site.input
    }
)
def update(client_state, carte_input, selection_input, carte_site_input):
    if client_state is None:  # No cookie, needs initialization
        client_state = {
            'vallee': None,
            'site': None,
            'zh': None,
        }
    changes = selection.process(**selection_input)
    if changes is None:
        changes = carte.process(client_state, **carte_input)
    if changes is None:
        changes = carte_site.process(client_state, **carte_site_input)
    # no trigger, every component to be updated with last known client state (cookie)
    just_reloaded = changes is None
    new_state = client_state if just_reloaded else {
        **client_state, **changes}
    return {
        'client_state': new_state,
        'carte': carte.update(new_state),
        'carte_site': carte_site.update(new_state, client_state, just_reloaded),
        'selection': selection.update(new_state),
        'gestion': gestion.update(new_state),
        'etat': etat.update(new_state),
        'habitat': habitat.update(new_state),
        'rhomeo': rhomeo.update(new_state),
    }


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')

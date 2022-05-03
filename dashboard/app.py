from dash import callback, callback_context, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from config import app
import selection
import carte
import carte_site
import gestion
# import habitat
import etat

app.layout = dbc.Container([
    html.Div(style={'height': '3vh'}),
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url(
                'logo-structure.png'), width='100%'),
            html.H2("Les zones humides"),
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
        'carte': carte.output,
        'selection': selection.output,
        'carte_site': carte_site.output
    },
    inputs={
        'carte_input': carte.input,
        'selection_input': selection.input,
        'carte_site_input': carte_site.input
    }
)
def update(carte_input, selection_input, carte_site_input):
    context = carte.process(**carte_input)
    if context is None:
        context = selection.process(**selection_input)
    if context is None:
        context = carte_site.process(**carte_site_input)
    if context is None:
        context = {'zh': None, 'site': None, 'vallee': None}
    context = {'zh': None, 'site': None, 'vallee': None, **context}
    print(context)
    return {
        'carte': carte.update(**context),
        'carte_site': carte_site.update(**context, input=carte_site_input),
        'selection': selection.update(**context)
    }


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, callback_context, html, no_update, dcc
import plotly.graph_objects as go
import config
import notice
import carte
from common import info_header
from data import site_data, rhomeo_site_data, rhomeo_result_data, analyse_rhomeo_data


rhomeo_summary = html.Div()

rhomeo_chart = dcc.Graph(config={'displayModeBar': False}, style={'height': '340px'})
rhomeo_indicator_layus = dbc.Alert(
    [], color='light', is_open=False, dismissable=True, class_name='mt-2 mb-2 py-2'
)

rows = html.Tbody()

collapsible_card = dbc.Collapse(dbc.Card([
    dbc.CardHeader(info_header('Rhomeo', '#rhomeo',
                   title="""Protocole de suivi Rhomeo
Cliquer pour consulter la documentation""")),
    dbc.CardBody([
        rhomeo_summary,
        html.Div(style={"height": "1em"}),  # petit espace
        rhomeo_chart,
        rhomeo_indicator_layus,
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Indicateur"),
                html.Th("Point de mesure"),
                html.Th('Valeur'),
            ])),
            rows,
        ], class_name='d-none'),  # remove class tag to display details
    ], class_name='overflow-auto')
], class_name='h-100'), class_name='h-100')

component = collapsible_card

zh_type_directory = {
    "7.1": "Zone humide d'altitude",
    "7.2": "Tourbière acide",
    "7.3": "Tourbière alcaline",
}

# https://rhomeo-bao.fr/?q=indicateurs
i_cat = {
    "I01": {
        "id": "I01",
        "label": "Humidité du sol",
        "tooltip": "L’indicateur définit un niveau d’humidité du sol de la zone humide, en attribuant aux horizons supérieurs du sol une note basée sur le type de trait d’hydromorphie observé. Les différents types de sols hydromorphes sont définis par les critères de l’arrêté de délimitation des zones humides du 1er octobre 2009.",
        "interp": """Plus la note d’hydromorphie est importante, 
plus la saturation en eau du sol est importante.
Une diminution de cette note traduit donc 
un assèchement de la zone humide.
Les valeurs s’échelonnent entre 0, 
pour un sol non hydromorphe et 6, 
pour des horizons totalement saturés en permanence
dans les 50 premiers centimètres.""",
        "url": "https://rhomeo-bao.fr/?q=indicateurs_01",
    }, "I02": {
        "id": "I02",
        "label": "Indice floristique d'engorgement",
        "tooltip": "La présence d’une nappe d’eau dans le sol constitue une contrainte pour les végétaux, contrainte à laquelle les espèces sont plus ou moins tolérantes ou adaptées. Il est donc possible d’évaluer de manière simplifiée l’optimum de chaque espèce vis-à-vis du niveau moyen de la nappe : c’est sa valeur indicatrice. Les végétaux peuvent donc être utilisés pour évaluer le niveau de la nappe à travers un indicateur, que nous appellerons indice de niveau d’engorgement.",
        "interp": """La valeur de l’indice est corrélée positivement avec
le niveau moyen annuel ou estival de la nappe :
plus sa valeur est élevée, plus le niveau moyen de
la nappe est proche de la surface. La gamme de
valeur va de 1 à 10 en théorie.""",
        "url": "https://rhomeo-bao.fr/?q=indicateurs_02",

    }, "I06": {
        "id": "I06",
        "label": "Indice floristique de fertilité du sol",
        "tooltip": "La quantité des nutriments (principalement azote et phosphore) disponibles dans le sol est un facteur important auquel les espèces sont plus ou moins tolérantes ou adaptées. Il est donc possible d’évaluer de manière simplifiée l’optimum de chaque espèce en fonction de la disponibilité des nutriments : c’est sa valeur indicatrice. La richesse “moyenne” en nutriments d’une zone humide, que nous appellerons indice de fertilité du sol, peut être calculée à l’échelle de la placette ou de la zone humide.",
        "interp": """La valeur diagnostique de fertilité est corrélée
positivement avec la disponibilité en nutriments
(azote et phosphore). La gamme de variation va
de 1 (sites très pauvres en nutriments) à 5 (sites
très riches).
        """,
        "url": "https://rhomeo-bao.fr/?q=indicateurs_06",

    }, "I08": {
        "id": "I08",
        "label": "Indice de qualité floristique",
        "tooltip": "Chaque espèce végétale développe, par une allocation particulière de ses ressources (racines, parties aériennes, graines), des stratégies lui permettant de faire face à certaines caractéristiques du milieu : perturbations diverses, facteurs limitant la croissance, aptitude à la compétition avec les autres espèces. On peut évaluer la plus ou moins grande aptitude d’une espèce à supporter des perturbations (hydrologique, trophique, …) d’une zone humide par un coefficient, nommé coefficient de conservatisme. L’indice de qualité floristique est un indice dérivé du coefficient de conservatisme, rendant compte à la fois du niveau global d’altération du régime naturel des perturbations auquel un site est soumis et de la richesse de ce site en espèces typiques des zones humides.",
        "interp": """L’indice est corrélé positivement avec le niveau
de perturbation global du site et avec le degré de
colonisation par les espèces exotiques. La gamme
de variation va de 0 (sites pour lesquels on n’aurait
contacté que des espèces exotiques) à environ 35
(tourbières non perturbées), la plupart étant situées
entre 10 et 25.
        """,
        "url": "https://rhomeo-bao.fr/?q=indicateurs_08",

    },
}


def zh_site_label(type):
    label = zh_type_directory.get(type, "Non renseigné")
    return f'{label} ({type})'


def display_info(key, value, key_width=5):
    return dbc.Row([dbc.Col(key, width=key_width), dbc.Col(value, width=12 - key_width)])


def indicator_color(i, value):
    return 'green'


def display_indicateur(i, results):
    value = indicateur(results, i)
    color = indicator_color(i, value)
    ref = i_cat[i]
    if value:
        return display_info(
            html.A(f"{ref['id']} - {ref['label']}", title=ref.get('tooltip'),
                   href=ref['url'], target='_blank',),
            html.H5(value,  title=ref.get('interp')),
            key_width=10,
        )


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


# Color palette for years — new years automatically get the next color
YEAR_COLORS = [
    '#4cc9f0',
    '#f8961e',
    '#90be6d',
    '#f94144',
    '#b5179e',
    '#43aa8b',
    '#f9c74f',
]

# Maps result indicator codes to CSV indicator codes
INDICATOR_CSV_MAP = {'I01': 'A01', 'I02': 'A02', 'I06': 'A06', 'I08': 'A08'}
INDICATORS_LIST = ['I01', 'I02', 'I06', 'I08']


def make_rhomeo_chart(results, zh_type):
    """Single graph: x = indicators, y = values (0-35).

    - Bande colorée semi-transparente : plage min-max de référence nationale
    - Point plein (gris) : moyenne de référence nationale
    - Tirets horizontaux colorés : moyenne du site pour chaque année
    Ajouter des années dans rhomeo_result.json suffit à les afficher.
    """
    years = sorted({r['year'] for r in results})
    labels = [i_cat[i]['id'] for i in INDICATORS_LIST]
    palette = {
        'text': '#dfe8f6',
        'muted': '#9eb0c8',
        'grid': 'rgba(223,232,246,0.14)',
        'panel': 'rgba(255,255,255,0.02)',
        'band': 'rgba(111,190,255,0.16)',
        'band_line': 'rgba(111,190,255,0.30)',
        'mean': '#a6d8ff',
    }

    fig = go.Figure()

    # --- Bande de référence (min → max) comme une barre semi-transparente ---
    ref_mins, ref_maxs, ref_means = [], [], []
    for ind in INDICATORS_LIST:
        ref = analyse_rhomeo_data.get((INDICATOR_CSV_MAP[ind], zh_type))
        if ref:
            ref_mins.append(ref['min'])
            ref_maxs.append(ref['max'])
            ref_means.append(ref['mean'])
        else:
            ref_mins.append(None)
            ref_maxs.append(None)
            ref_means.append(None)

    fig.add_trace(go.Bar(
        x=labels,
        y=ref_maxs,
        base=ref_mins,
        customdata=INDICATORS_LIST,
        name='Plage référence',
        marker_color=palette['band'],
        marker_line_color=palette['band_line'],
        marker_line_width=1,
        width=0.58,
        hovertemplate='<b>%{x}</b><br>Plage réf. : %{base:.1f} – %{y:.1f}<extra></extra>',
    ))

    # --- Point de la moyenne de référence ---
    fig.add_trace(go.Scatter(
        x=labels,
        y=ref_means,
        customdata=INDICATORS_LIST,
        mode='markers',
        name='Moy. référence',
        marker=dict(symbol='circle', size=10, color=palette['mean'], line=dict(width=1, color='#0f1724')),
        hovertemplate='<b>%{x}</b><br>Moy. réf. : %{y:.2f}<extra></extra>',
    ))

    # --- Tirets horizontaux par année ---
    for j, year in enumerate(years):
        color = YEAR_COLORS[j % len(YEAR_COLORS)]
        y_vals = []
        for ind in INDICATORS_LIST:
            vals = [r['value'] for r in results if r['name'] == ind and r['year'] == year]
            y_vals.append(round(sum(vals) / len(vals), 2) if vals else None)

        fig.add_trace(go.Scatter(
            x=labels,
            y=y_vals,
            customdata=INDICATORS_LIST,
            mode='markers',
            name=str(year),
            marker=dict(
                symbol='line-ew-open',
                size=30,
                line=dict(width=3, color=color),
                color=color,
            ),
            hovertemplate='<b>%{x}</b><br>' + str(year) + ' : %{y:.2f}<extra></extra>',
        ))

    # Zone de clic près de l'axe X pour ouvrir le layus de l'indicateur.
    fig.add_trace(go.Scatter(
        x=labels,
        y=[0.45] * len(labels),
        customdata=INDICATORS_LIST,
        mode='markers',
        marker=dict(size=28, color='rgba(0,0,0,0.01)'),
        showlegend=False,
        hovertemplate='Cliquer pour ouvrir le descriptif<extra></extra>',
    ))

    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor=palette['panel'],
        font=dict(color=palette['text'], size=12),
        hoverlabel=dict(bgcolor='#111922', bordercolor='#2c3b52', font=dict(color=palette['text'])),
        legend_title_text='Légende',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
        margin=dict(t=52, b=48, l=46, r=16),
    )
    fig.update_xaxes(
        title_text='Indicateur',
        title_font=dict(color=palette['muted']),
        tickfont=dict(color=palette['text']),
        showline=True,
        linecolor='rgba(223,232,246,0.28)',
    )
    fig.update_yaxes(
        range=[0, 35],
        dtick=5,
        title_text='Valeur',
        title_font=dict(color=palette['muted']),
        tickfont=dict(color=palette['muted']),
        gridcolor=palette['grid'],
        zeroline=False,
    )
    return fig


def get_clicked_indicator(click_data):
    if not click_data or not click_data.get('points'):
        return None
    point = click_data['points'][0]
    indicator = point.get('customdata') or point.get('x')
    if isinstance(indicator, str) and indicator in i_cat:
        return indicator
    return None


@callback(
    Output(rhomeo_indicator_layus, 'is_open'),
    Output(rhomeo_indicator_layus, 'children'),
    Input(rhomeo_chart, 'clickData'),
    prevent_initial_call=True,
)
def open_indicator_layus(click_data):
    indicator = get_clicked_indicator(click_data)
    if indicator is None:
        return no_update, no_update

    ref = i_cat[indicator]
    return True, [
        html.H6(f"{ref['id']} - {ref['label']}", className='mb-2'),
        html.P(ref.get('tooltip'), className='mb-2'),
        html.Div(ref.get('interp'), style={'whiteSpace': 'pre-line'}, className='mb-2'),
        html.A('Documentation RHOMEO', href=ref['url'], target='_blank'),
    ]


output = {
    'visible': Output(collapsible_card, 'is_open'),
    'info': Output(rhomeo_summary, 'children'),
    'rows': Output(rows, 'children'),
    'chart': Output(rhomeo_chart, 'figure'),
}


def update(state):
    id_site = state['site']
    if id_site is None or site_data[id_site]['rhomeo'] is None:
        return {
            'visible': False,
            'info': no_update,
            'rows': no_update,
            'chart': no_update,
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
            # display_indicateur('I01', results),
            # display_indicateur('I02', results),
            # display_indicateur('I06', results),
            # display_indicateur('I08', results),
        ],
        'rows': indicateurs(results),
        'chart': make_rhomeo_chart(results, obj['type']),
    }

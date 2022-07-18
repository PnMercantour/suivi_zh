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
    dbc.CardHeader(info_header('Rhomeo', '#rhomeo',
                   title="""Protocole de suivi Rhomeo
Cliquer pour consulter la documentation""")),
    dbc.CardBody([
        rhomeo_summary,
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
            display_indicateur('I01', results),
            display_indicateur('I02', results),
            display_indicateur('I06', results),
            display_indicateur('I08', results),
        ],
        'rows': indicateurs(results),
    }

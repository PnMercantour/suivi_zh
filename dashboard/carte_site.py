
from config import IGN_KEY, app, ns
import dash_leaflet as dl
from dash_extensions.javascript import assign, arrow_function, Namespace
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, callback, clientside_callback, callback_context, no_update, html
import dash_bootstrap_components as dbc
import data
import tile
from common import info_header

title = html.Div('Etat des zones humides')

vallees = dl.GeoJSON(
    url=app.get_asset_url('vallee.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        style=ns('valleeStateStyle'),
        # style={'color': 'white', 'fillOpacity': 0,
        #        'pane': 'detail_vallee_pane'},
        onEachFeature=ns('pourChaqueVallee'),
    ),
)

sites = dl.GeoJSON(
    url=app.get_asset_url('site.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        filter=ns('siteFilter'),
        pointToLayer=ns('siteStatePointToLayer'),
        onEachFeature=ns('siteTooltip'),
        pane='detail_site_pane',
    ),
)

zones_humides = dl.GeoJSON(
    url=app.get_asset_url('zh.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        filter=ns('zhFilter'),
        onEachFeature=ns('zhTooltip'),
        style=ns('zhStyle'),
        color='blue',
        fillOpacity=0.4,
        pane="markerPane",
    ),
)

alteration = dl.GeoJSON(
    url=app.get_asset_url('alteration.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        filter=ns('alterationFilter'),
        onEachFeature=ns('alterationTooltip'),
        pane='shadowPane',
        style={
            'color': 'pink',
            'fillOpacity': 0.4,
        }
    )
)

defens = dl.GeoJSON(
    url=app.get_asset_url('defens.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        filter=ns('defensFilter'),
        onEachFeature=ns('defensTooltip'),
        pane='shadowPane',
        style={
            'color': 'black',
            'fillOpacity': 0.2,
        }
    )
)

ebf = dl.GeoJSON(
    url=app.get_asset_url('ebf.json'),
    hideout={
        'vallee': None,
        'site': None,
        'zh': None,
    },
    options=dict(
        filter=ns('ebfFilter'),
        onEachFeature=ns('ebfTooltip'),
        pane='detail_ebf_pane',
        style={
            'color': 'blue',
            'fillOpacity': 0.1,
        }
    )
)

rhomeo = dl.GeoJSON(
    url=app.get_asset_url('rhomeo.json'),
    hideout={
        'vallee': None,
        'site': None,
        'code': None,
    },
    options=dict(
        pointToLayer=ns('rhomeoPointToLayer'),
        filter=ns('rhomeoFilter'),
        onEachFeature=ns('rhomeoTooltip'),
        # pane='detail_ebf_pane',
        # style={
        #     'color': 'blue',
        #     'fillOpacity': 0.1,
        # }
    )
)

map = dl.Map(
    dl.LayersControl([
        dl.BaseLayer(tile.ign('carte'), name='IGN', checked=False),
        dl.BaseLayer(tile.ign('ortho'), name='Vue aérienne', checked=True),
        dl.Pane(
            dl.Pane(vallees, name='detail_vallee_pane_s',
                    pane='detail_vallee_pane_s', style={'zIndex': 451}),
            name='detail_vallee_pane',
            pane='detail_vallee_pane', style={'zIndex': 450}),
        dl.Pane(sites, name='detail_site_pane',
                pane='detail_site_pane', style={'zIndex': 460}),
        dl.Overlay(dl.Pane(ebf, name='detail_ebf_pane',
                           pane='detail_ebf_pane', style={'zIndex': 455}),
                   name='Espaces de bon fonctionnement', checked=False),
        dl.Overlay(zones_humides, name='Zones humides', checked=True),
        dl.Overlay(alteration, name='Altérations', checked=False),
        dl.Overlay(defens, name='Défens', checked=True),
        dl.Overlay(dl.Pane(rhomeo, name='rhomeo_pane',
                           pane='rhomeo_pane', style={'zIndex': 600}),
                   name='Relevés Rhomeo', checked=False),

    ]),
    style={'width': '100%', 'height': '60vh'},
    bounds=data.bounds(),
)


# component internal input triggers
input = {
    'map_click': Input(map, 'click_lat_lng'),
    'vallee': Input(vallees, 'click_feature'),
    'site': Input(sites, 'click_feature'),
    'zh': Input(zones_humides, 'click_feature'),
    'rhomeo': Input(rhomeo, 'click_feature'),
}


def process(previous_state, map_click, vallee, site, zh, rhomeo):
    if vallee:
        prev_site = previous_state['site']
        prev_vallee = previous_state['vallee']
        clicked_vallee = vallee['properties']['id']
        return{
            'vallee': clicked_vallee if (clicked_vallee != prev_vallee or prev_site is not None) else None,
            'site': prev_site if (clicked_vallee == prev_vallee and previous_state['zh'] is not None) else None,
            'zh': None,
        }
    if site:
        return {
            'vallee': site['properties']['id_vallee'],
            'site': site['properties']['id'],
            'zh': None,
        }
    if zh:
        prev_zh = previous_state['zh']
        clicked_zh = zh['properties']['id']
        new_zh = clicked_zh if clicked_zh != prev_zh else None
        return {
            'zh': new_zh,
        }
    if rhomeo:
        print(rhomeo)
        the_site = data.site_data[rhomeo['properties']['id_site']]
        return{
            'vallee': the_site['id_vallee'],
            'site': the_site['id'],
            'zh': None,
        }
    if map_click:
        if previous_state['zh']:
            return{
                'zh': None,
            }
        if previous_state['site']:
            return{
                'site': None,
                'zh': None,
            }
        if previous_state['vallee']:
            return{
                'vallee': None,
                'site': None,
                'zh': None,
            }
    return None


def make_title(zh=None, site=None, vallee=None):
    if vallee is None:
        return "Zones humides du Parc national du Mercantour"
    if site is None:
        return f"Zones humides de la vallée {data.vallee_data[vallee]['nom_vallee']}"

    return f"Zones humides du site {data.site_data[site]['nom_site']} ({data.vallee_data[vallee]['nom_vallee']})"


# component internal output properties
output = {
    'hideout': Output(zones_humides, 'hideout'),
    'map_click': Output(map, 'click_lat_lng'),
    'vallee_click': Output(vallees, 'click_feature'),
    'site_click': Output(sites, 'click_feature'),
    'zh_click': Output(zones_humides, 'click_feature'),
    'rhomeo_click': Output(rhomeo, 'click_feature'),
    'bounds': Output(map, 'bounds'),
    'site_hideout': Output(sites, 'hideout'),
    'vallee_hideout': Output(vallees, 'hideout'),
    'alteration_hideout': Output(alteration, 'hideout'),
    'defens_hideout': Output(defens, 'hideout'),
    'ebf_hideout': Output(ebf, 'hideout'),
    'rhomeo_hideout': Output(rhomeo, 'hideout'),
    'title': Output(title, 'children'),
}


def update(new_state, old_state, force_update):
    vallee = new_state['vallee']
    site = new_state['site']
    zh = new_state['zh']
    same_context = not force_update and vallee is not None and site == old_state[
        'site'] and vallee == old_state['vallee']
    return {
        'hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'alteration_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'defens_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'site_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'vallee_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'ebf_hideout': {'vallee': vallee},  # don't use site
        'rhomeo_hideout': {'site': site, 'vallee': vallee, 'code': data.site_data[site]['rhomeo'] if site is not None else None, },
        'title': no_update if same_context else make_title(site=site, vallee=vallee, zh=zh),
        'bounds': no_update if same_context else data.bounds(site=site, vallee=vallee),
        'map_click': None,
        'vallee_click': None,
        'site_click': None,
        'zh_click': None,
        'rhomeo_click': None,
    }


component = dbc.Card([
    dbc.CardHeader(info_header(title, "#carte-des-zones-humides")),
    dbc.CardBody(map),
])

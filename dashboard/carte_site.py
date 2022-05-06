
from config import IGN_KEY, app, ns
import dash_leaflet as dl
from dash_extensions.javascript import assign, arrow_function, Namespace
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, callback, clientside_callback, callback_context, no_update, html
import dash_bootstrap_components as dbc
import data
import tile

title = html.Div('Etat des zones humides')

vallees = dl.GeoJSON(
    url=app.get_asset_url('vallee_full.json'),
    hideout={'zh': None, 'site': None, 'vallee': None},
    options=dict(
        style=ns('valleeStateStyle'),
        # style={'color': 'white', 'fillOpacity': 0,
        #        'pane': 'detail_vallee_pane'},
        onEachFeature=ns('pourChaqueVallee'),
    ),
)

sites = dl.GeoJSON(
    url=app.get_asset_url('sites.json'),
    hideout={'zh': None, 'site': None, 'vallee': None},
    options=dict(
        filter=ns('siteFilter'),
        pointToLayer=ns('siteStatePointToLayer'),
        onEachFeature=ns('pourChaqueSite'),
        pane='detail_site_pane',
    ),
)

zones_humides = dl.GeoJSON(
    hideout={'zh': None, 'site': None, 'vallee': None},
    options=dict(
        style=ns('zhColor'),
        color='blue',
        fillOpacity=0.4,
        pane="markerPane",
    ),
)

defens = dl.GeoJSON(
    url=app.get_asset_url('defens.json'),
    hideout={'zh': None, 'site': None, 'vallee': None},
    options=dict(
        filter=ns('defensFilter'),
        style={
            'color': 'black',
            'fillOpacity': 0
        }
    )
)
map = dl.Map(dl.LayersControl([
    dl.BaseLayer(tile.ign('carte'), name='IGN', checked=False),
    dl.BaseLayer(tile.ign('ortho'), name='Vue aérienne', checked=True),
    dl.Pane(
        dl.Pane(vallees, name='detail_vallee_pane_s',
                pane='detail_vallee_pane_s', style={'zIndex': 451}),
        name='detail_vallee_pane',
        pane='detail_vallee_pane', style={'zIndex': 450}),
    dl.Pane(sites, name='detail_site_pane',
            pane='detail_site_pane', style={'zIndex': 460}),
    dl.Overlay(zones_humides, name='Zones humides', checked=True),
    dl.Overlay(defens, name='Défens', checked=True),

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
    'hideout': Input(zones_humides, 'hideout'),
}


def process(map_click, vallee, site, zh, hideout):
    print(map_click, vallee, site, zh)
    if vallee:
        prev_site = hideout['site'] if hideout else None
        prev_vallee = hideout['vallee'] if hideout else None
        clicked_vallee = vallee['properties']['id_vallee']
        return{
            'site': None,
            'vallee': clicked_vallee if (clicked_vallee != prev_vallee or prev_site is not None) else None,
        }
    if site:
        return {
            'site': site['properties']['id_site'],
            'vallee': hideout['vallee'],
        }
    if zh:
        prev_zh = hideout['zh'] if hideout else None
        clicked_zh = zh['properties']['id']
        new_zh = clicked_zh if clicked_zh != prev_zh else None
        return {**hideout, 'zh': new_zh}
    if map_click:
        if hideout['zh']:
            return{**hideout, 'zh': None}
        if hideout['site']:
            return{**hideout, 'site': None, 'zh': None}
        if hideout['vallee']:
            return{'vallee': None, 'site': None, 'zh': None}
    return None


def make_title(zh=None, site=None, vallee=None):
    if vallee is None:
        return "Etat des zones humides des vallées du Parc national du Mercantour"
    if site is None:
        return f"Etat des sites de la vallée {data.vallee_data[vallee]['nom_vallee']}"

    return f"Etat du site {data.site_data[site]['nom_site']} ({data.vallee_data[vallee]['nom_vallee']})"


# component internal output properties
output = {
    'hideout': Output(zones_humides, 'hideout'),
    'map_click': Output(map, 'click_lat_lng'),
    'vallee_click': Output(vallees, 'click_feature'),
    'site_click': Output(sites, 'click_feature'),
    'zh_click': Output(zones_humides, 'click_feature'),
    'bounds': Output(map, 'bounds'),
    'url': Output(zones_humides, 'url'),
    'site_hideout': Output(sites, 'hideout'),
    'vallee_hideout': Output(vallees, 'hideout'),
    'defens_hideout': Output(defens, 'hideout'),
    'title': Output(title, 'children'),
}


def update(zh, site, vallee, input):
    same_context = input['hideout']['site'] == site and input['hideout']['vallee'] == vallee
    return {
        'hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'defens_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'site_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'vallee_hideout': {'site': site, 'vallee': vallee, 'zh': zh},
        'title': no_update if same_context else make_title(site=site, vallee=vallee, zh=zh),
        'bounds': no_update if same_context else data.bounds(site=site, vallee=vallee),
        'url': app.get_asset_url('sites/' + str(site) + '.json') if site is not None else None,
        'map_click': None,
        'vallee_click': None,
        'site_click': None,
        'zh_click': None,
    }


component = dbc.Card([
    dbc.CardHeader(title),
    dbc.CardBody(map),
])

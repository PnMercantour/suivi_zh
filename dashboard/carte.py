
from config import IGN_KEY, app, ns
import dash_leaflet as dl
from dash_extensions.javascript import assign, arrow_function, Namespace
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, callback, clientside_callback, callback_context
import dash_bootstrap_components as dbc
import data
import tile


vallees = dl.GeoJSON(
    url=app.get_asset_url('vallees.json'),
    id='vallees',
    hideout={'zh': None, 'site': None, 'vallee': None},
    options=dict(
        style=ns('valleeSituationStyle'),
        onEachFeature=ns('pourChaqueVallee'),
        pane='vallee_pane',
    ),
)

sites = dl.GeoJSON(
    url=app.get_asset_url('sites.json'),
    id='sites',
    hideout={'site': None, 'vallee': None},
    options=dict(
        pointToLayer=ns('siteSituationToLayer'),
        onEachFeature=ns('pourChaqueSite'),
        pane="site_pane",
    ),
)

# https://leafletjs.com/reference.html#map-pane
map = dl.Map(dl.LayersControl([
    dl.BaseLayer(tile.ign('carte'), name='IGN', checked=False),
    dl.BaseLayer(tile.stamen('toner'), name='Noir et blanc', checked=True),
    dl.Pane(vallees, name='vallee_pane',
            pane='vallee_pane', style={'zIndex': '(450)'}),
    dl.Pane(sites, name='site_pane', pane='site_pane', style={'zIndex': 460}),
]),
    id='map',
    bounds=data.bounds(),
    style={'width': '100%', 'height': '30vh'},
)


input = {
    'map_click': Input(map, 'click_lat_lng'),
    'vallee': Input(vallees, 'click_feature'),
    'site': Input(sites, 'click_feature'),
    'hideout': Input(sites, 'hideout'),
}


def process(map_click, vallee, site, hideout):
    triggers = [trigger['prop_id'] for trigger in callback_context.triggered]
    if any([sites.id in trigger for trigger in triggers]):
        if site:
            prev_site = hideout['site'] if hideout else None
            clicked_site = site['properties']['id_site']
            return{
                'site': clicked_site if clicked_site != prev_site else None,
                'vallee': site['properties']['id_vallee'],
            }
    if any([vallees.id in trigger for trigger in triggers]):
        if vallee:
            prev_site = hideout['site'] if hideout else None
            prev_vallee = hideout['vallee'] if hideout else None
            clicked_vallee = vallee['properties']['id_vallee']
            return{
                'site': None,
                'vallee': clicked_vallee if (clicked_vallee != prev_vallee or prev_site is not None) else None,
            }
    if any([map.id in trigger for trigger in triggers]):
        if map:
            return{
                'site': None,
                'vallee': None,
            }
    return None


output = {
    'hideout': Output(sites, 'hideout'),
    'vallee_hideout': Output(vallees, 'hideout'),
    'bounds': Output(map, 'bounds'),
    'map_click': Output(map, 'click_lat_lng'),
    'vallee_click': Output(vallees, 'click_feature'),
    'site_click': Output(sites, 'click_feature'),
}


def update(zh, site, vallee):
    return {
        'hideout': {'site': site, 'vallee': vallee},
        'vallee_hideout': {'site': site, 'vallee': vallee},
        'bounds': data.bounds(vallee=vallee),
        'map_click': None,
        'vallee_click': None,
        'site_click': None,
    }


context = Input(sites, 'hideout')

component = dbc.Card([
    dbc.CardHeader('Carte de situation'),
    dbc.CardBody(map),
])

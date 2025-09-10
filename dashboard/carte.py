
from config import IGN_KEY, app, ns
import dash_leaflet as dl
from dash_extensions.javascript import assign, arrow_function, Namespace
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, callback, clientside_callback, callback_context
import dash_bootstrap_components as dbc

from common import info_header
import data
import tile

vallees = dl.GeoJSON(
    url=app.get_asset_url('vallee.json'),
    id='vallees',
    hideout={'vallee': None, 'site': None},
    options=dict(
        style=ns('valleeSituationStyle'),
        onEachFeature=ns('pourChaqueVallee'),
        pane='vallee_pane',
    ),
)

sites = dl.GeoJSON(
    url=app.get_asset_url('site.json'),
    id='sites',
    hideout={'vallee': None, 'site': None},
    options=dict(
        filter=ns('siteSituationFilter'),
        pointToLayer=ns('siteSituationToLayer'),
        onEachFeature=ns('siteTooltip'),
        pane="site_pane",
    ),
)

# https://leafletjs.com/reference.html#map-pane
map = dl.Map([
    tile.stamen('toner'),
    dl.Pane(vallees, name='vallee_pane',
            pane='vallee_pane', style={'zIndex': 450}),
    dl.Pane(
        dl.Pane(
            sites,
            name='site_pane',
            pane='site_pane',
            style={'zIndex': 460},
        ),
        name='selected_site_pane',
        pane='selected_site_pane',
        style={'zIndex': 470},
    ),
],
    id='map',
    bounds=data.bounds(),
    zoomControl=False,
    style={'width': '100%', 'height': '100%'},
)


input = {
    'map_click': Input(map, 'clickData'),
    'vallee': Input(vallees, 'clickData'),
    'site': Input(sites, 'clickData'),
}


def process(previous_state, map_click, vallee, site):
    if site:
        clicked_site = site['properties']['id']
        return {
            'vallee': site['properties']['id_vallee'],
            'site': clicked_site if clicked_site != previous_state['site'] else None,
        }
    if vallee:
        clicked_vallee = vallee['properties']['id']
        return{
            'vallee': clicked_vallee if (clicked_vallee != previous_state['vallee'] or previous_state['site'] is not None) else None,
            'site': None,
        }
    if map_click:
        return {
            'vallee': None,
            'site': None,
        }
    return None


output = {
    'hideout': Output(sites, 'hideout'),
    'vallee_hideout': Output(vallees, 'hideout'),
    # 'bounds': Output(map, 'bounds'),
    'map_click': Output(map, 'clickData'),
    'vallee_click': Output(vallees, 'clickData'),
    'site_click': Output(sites, 'clickData'),
    'viewport': Output(map, 'viewport'),
}


def update(state):
    bounds = data.bounds()
    return {
        'hideout': {'site': state['site'], 'vallee': state['vallee']},
        'vallee_hideout': {'site': state['site'], 'vallee': state['vallee']},
        # 'bounds': data.bounds(),  # reset bounds to initial value
        'map_click': None,
        'vallee_click': None,
        'site_click': None,
        'viewport': dict(bounds=bounds, transition="flyToBounds")
    }


context = Input(sites, 'hideout')

component = dbc.Card([
    dbc.CardHeader(info_header('Localisation', '#carte-de-situation')),
    dbc.CardBody(map),
], style={'width': '100%', 'height': '100%'})

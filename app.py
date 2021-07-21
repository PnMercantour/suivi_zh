import os
import dash
import dash_html_components as html
import dash_leaflet as dl
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
from pathlib import Path
from dotenv import load_dotenv
import json
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
load_dotenv('.env/.env')

app = dash.Dash(__name__)

#assign(""" () => {let test = {}} """)
#création d'un dictionaire pour les couleurs des polygones
js_style = assign("""
function(feature, context) {
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {return {color:"#000000"}}
    else {
        let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500"};
        return {color: t[feature.properties.etat_zh]}}
}""")

fonction_couleur_carte = assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    cachedData.zhTable[feature.properties.id] = {surface : feature.properties.surface, etat: feature.properties.etat_zh}
    if(feature.properties.etat_zh){
        layer.bindTooltip(feature.properties.etat_zh)
    }
}
""")

# Chargement de sites.json utilisation pour les données du tableaux des sites
with open(Path(Path(__file__).parent, 'assets', 'sites.json'), 'r') as fichier:
    sites_json = json.loads(fichier.read())
    fichier.close()

point_to_layer = assign("""function(feature, latlng, context){
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {
        circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
    }
    else
        circleOptions= {color: "blue"};
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

# GeoJSON pour les sites
siteLayer = dl.GeoJSON(id="siteLayer", url=app.get_asset_url('sites.json'), options=dict(pointToLayer=point_to_layer, hideout=dict(selected_site=-1), onEachFeature=assign("""
    (feature, layer) => {
        if(!feature.properties){
            return
        }
        cachedData.siteTable[feature.properties.id] = feature
        if(feature.properties.nom_site){
            layer.bindTooltip(feature.properties.nom_site)
        }
}
""")))

zhLayer = dl.GeoJSON(id='zhLayer', options=dict(pointToLayer=point_to_layer, hideout=dict(selected_site=-1), onEachFeature=fonction_couleur_carte, style=js_style), zoomToBounds=True)

zhTable = dash_table.DataTable(
            id='zhTable',
            columns=[],
            data=[],
            sort_action='native',
            filter_action='native',
            style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ], page_size=10,  merge_duplicate_headers=True,
)

siteTable = dash_table.DataTable(
        id='siteTable',
        columns=[{"name": "nom_site", "id": "nom_site"}],
        data=[{'nom_site':index['properties']}['nom_site'] for index in sites_json['features']],
        sort_action='native',
        filter_action='native',
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
)

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
baseLayer = dl.TileLayer(url="https://wxs.ign.fr/" + os.getenv('IGN_KEY') + "/wmts?" +
                         "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                         "&STYLE=normal" +
                         "&TILEMATRIXSET=PM" +
                         "&FORMAT=image/jpeg" +
                         "&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS" +
                         "&TILEMATRIX={z}" +
                         "&TILEROW={y}" +
                         "&TILECOL={x}",
                         minZoom=0,
                         maxZoom=18,
                         tileSize=256,
                         attribution="IGN-F/Geoportail")

# Le layout
app.layout = html.Div([
    html.Div([
        siteTable
    ],style={'float':'left', 'paddingRight': '5vh'}),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, siteLayer],
        center=[44.3, 7], zoom=9),style={'display':'flex', 'paddingBottom':'5vh'}),
    html.Div([
        dl.Map(id="site_unique", children=[baseLayer, zhLayer]),
        zhTable
    ], style={'display':'flex', 'maxHeight': '50vh'}), html.Div(id='test')
])

def trouve_le_centroid(id):
    for elem in sites_json['features']:
        if elem['properties']['id'] == id:
            return elem['geometry']['coordinates'][::-1]

def trouve_le_fichier_du_site(id):
    return app.get_asset_url('sites/'+str(id)+'.json')

@app.callback([Output('zhLayer', 'url'), Output('site_unique', 'center')], [Input('siteLayer', 'click_feature'), Input('siteTable', 'selected_cells')])
def maj_carte_site_unique(feature, cell):
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger == '.':
        raise PreventUpdate
    if trigger == 'siteLayer.click_feature':
        id = feature['properties']['id']
        return trouve_le_fichier_du_site(id), trouve_le_centroid(id)
    if trigger == 'siteTable.selected_cells':
        id = cell[0]['row_id']
        return trouve_le_fichier_du_site(id), trouve_le_centroid(id)

# @app.callback([Output('zhTable', 'data'), Output('zhTable', 'columns'), Output('siteTable', 'selected_cells')], [Input("siteTable", "selected_cells"), Input("siteLayer", "click_feature"), Input('siteTable', 'derived_viewport_row_ids')])
# def maj_siteTable(cell, feature, sites_lignes):
#     trigger = dash.callback_context.triggered[0]['prop_id']
#     columns = [{'name': 'surface', 'id': 'surface'}, {'name':'etat', 'id': 'etat_zh'}]
#     if trigger == '.':
#         raise PreventUpdate
#     if trigger == 'siteLayer.click_feature': 
#         with open('assets/sites/'+str(feature['properties']['id'])+'.json', 'r') as fichier_json:
#             site = json.loads(fichier_json.read())
#             fichier_json.close()   
#         ligne = sites_lignes.index(feature['properties']['id'])
#         return [dict(zone['properties']) for zone in site['features']], [{'name': [feature['properties']['nom_site'], column['name']], 'id': column['id']} for column in columns], [{'row': ligne, 'column':0}]
#     if trigger == 'siteTable.selected_cells':
#         with open('assets/sites/'+str(cell[0]['row_id'])+'.json', 'r') as fichier_json:
#             site = json.loads(fichier_json.read())
#             fichier_json.close()
#         for elem in sites_json['features']:
#             if elem['properties']['id'] == cell[0]['row_id']:
#                 nom_site = elem['properties']['nom_site']
#         return [dict(zone['properties'])for zone in site['features']], [{'name': [nom_site, column['name']], 'id': column['id']} for column in columns], cell

@app.callback([Output('zhTable', 'active_cell')], [Input('zhLayer','click_feature'), Input('zhTable', 'derived_viewport_row_ids')], prevent_initial_call=True) 
def zhTable(zone, tableau_zones_lignes):
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger == '.':
        raise PreventUpdate
    row = tableau_zones_lignes.index(zone['properties']['id'])
    return [{'row': row, 'column': 0}]

app.clientside_callback(
    """function(feature, cell, hideout) {
    if (feature == undefined && dash_clientside.callback_context.triggered[0].prop_id === '.') 
        return dash_clientside.no_update
    else if (dash_clientside.callback_context.triggered[0].prop_id === "siteTable.active_cell" )
        return {...hideout, selected_site: cell.row_id}
    else
        return {...hideout, selected_site: feature.properties.id}
    }""",
    Output("siteLayer", "hideout"),
    Input("siteLayer", "click_feature"),
    Input("siteTable", "active_cell"),
    State("siteLayer", "hideout")
    )

app.clientside_callback(
    """function(feature, hideout) {
    if (feature == undefined) 
        return hideout
    else
        return {...hideout, selected_site: feature.properties.id}
    }""",
    Output("zhLayer", "hideout"),
    Input("zhLayer", "click_feature"),
    State("siteLayer", "hideout")
    )

app.clientside_callback(
    """function(hideout) {
    return cachedData.siteTable.map((feature, id) => ({nom_site: feature.properties.nom_site, id}));
    }""",
    Output("siteTable", "data"),
    Input("siteLayer", "hideout"))

app.clientside_callback(
    """function(site, hideout) {
        i = site.selected_site
        console.log(i)
        const nom = cachedData.siteTable[i].properties.nom_site
    let table = cachedData.zhTable.map((feature, id) => ({surface: feature.surface, etat: feature.etat, id}))
    return [table, [{"name": [nom, "surface"], "id": "surface"}, {"name": [nom, "état"], "id": "etat"}]];
    }""",
    Output("zhTable", "data"),
    Output("zhTable", "columns"),
    Input("siteLayer", "hideout"),
    Input("zhLayer", "hideout"))

if __name__ == '__main__':
    app.run_server(debug=True)
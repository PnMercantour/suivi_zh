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
    //if(document.getElementById('tableau_des_zones').getElementByClassName('cell--selected')) {console.log("ok")}
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {return {color:"#000000"}}
    else {
        let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500"};
        return {color: t[feature.properties.etat_zh]}}
}""")

fonction_couleur_carte = assign("""
(feature, layer) => {
    //table id + geometry
    if(!feature.properties){
        return
    }
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
carte_sites = dl.GeoJSON(id="carte_sites", data=sites_json, options=dict(pointToLayer=point_to_layer, hideout=dict(selected_site=-1), onEachFeature=assign("""
    (feature, layer) => {
        if(!feature.properties){
            return
        }
        if(feature.properties.nom_site){
            layer.bindTooltip(feature.properties.nom_site)
        }
}
""")))

tableau_des_zones = dash_table.DataTable(
            id='tableau_des_zones',
            columns=[{"name": "nom site", "id": "nom_site"}],
            data=[],
            sort_action='native',
            filter_action='native',
            style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ], page_size=10,  merge_duplicate_headers=True,
)

tableau_des_sites = dash_table.DataTable(
        id='tableau_des_sites',
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
        tableau_des_sites
    ],style={'float':'left', 'paddingRight': '5vh'}),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, carte_sites],
        center=[44.3, 7], zoom=9),style={'display':'flex', 'paddingBottom':'5vh'}),
    html.Div([
        dl.Map(id="site_unique", children=[baseLayer, dl.GeoJSON(id='zone_humide_unique', options=dict(pointToLayer=point_to_layer, hideout=dict(selected_site=-1), onEachFeature=fonction_couleur_carte, style=js_style), zoomToBounds=True)]),
        tableau_des_zones
    ], style={'display':'flex', 'maxHeight': '50vh'}), html.Div(id='test')
])

# @app.callback(Output('test', 'children'), Input('carte_sites', 'click_feature'))
# def test(input):
#     with open('assets/sites/'+str(input['properties']['id'])+'.json', 'r') as f:
#         content = f.read()
#         with open('assets/cachedData.js', 'r') as js_file:
#             list_of_lines = js_file.readlines()
#             list_of_lines[1] =  'siteTable : '+content+',\n'
#             with open('assets/cachedData.js', 'w') as js_file:
#                 js_file.writelines(list_of_lines)
#             js_file.close()
#         f.close()
#     return 'ok'
#================================================
# app.clientside_callback(
#     """
#     function(data, cell, carte){
#         const elem = L.DomUtil.get('parc')
#         console.log(elem)
#         const context = elem.getContext('2d')
#         console.log(context)
#         data.features.forEach(feature => {if(cell.row_id && feature.properties.id === cell.row_id){ dashExtensions.default.function2(feature, feature.geometry.coordinates, context)}})
#     }
#     """,
#     Output('carte_sites', 'options'), Input('carte_sites', 'data'), Input('tableau_des_sites', 'active_cell'), Input('parc', 'children')
# )
#==============================================================================
def trouve_le_centroid(id):
    for elem in sites_json['features']:
        if elem['properties']['id'] == id:
            return elem['geometry']['coordinates'][::-1]

def trouve_le_fichier_du_site(id):
    return app.get_asset_url('sites/'+str(id)+'.json')

@app.callback([Output('tableau_des_zones', 'data'), Output('tableau_des_zones', 'columns'), Output('tableau_des_sites', 'selected_cells')], [Input("tableau_des_sites", "selected_cells"), Input("carte_sites", "click_feature"), Input('tableau_des_sites', 'derived_viewport_row_ids')])
def maj_tableau_des_sites(cell, feature, sites_lignes):
    trigger = dash.callback_context.triggered[0]['prop_id']
    columns = [{'name': 'surface', 'id': 'surface'}, {'name':'etat', 'id': 'etat_zh'}]
    if trigger == '.':
        raise PreventUpdate
    if trigger == 'carte_sites.click_feature': 
        with open('assets/sites/'+str(feature['properties']['id'])+'.json', 'r') as fichier_json:
            site = json.loads(fichier_json.read())
            fichier_json.close()   
        ligne = sites_lignes.index(feature['properties']['id'])
        return [dict(zone['properties']) for zone in site['features']], [{'name': [feature['properties']['nom_site'], column['name']], 'id': column['id']} for column in columns], [{'row': ligne, 'column':0}]
    if trigger == 'tableau_des_sites.selected_cells':
        with open('assets/sites/'+str(cell[0]['row_id'])+'.json', 'r') as fichier_json:
            site = json.loads(fichier_json.read())
            fichier_json.close()
        for elem in sites_json['features']:
            if elem['properties']['id'] == cell[0]['row_id']:
                nom_site = elem['properties']['nom_site']
        return [dict(zone['properties'])for zone in site['features']], [{'name': [nom_site, column['name']], 'id': column['id']} for column in columns], cell

@app.callback([Output('tableau_des_zones', 'active_cell')], [Input('zone_humide_unique','click_feature'), Input('tableau_des_zones', 'derived_viewport_row_ids')], prevent_initial_call=True) 
def selection_cellule_tableau_des_zones(zone, tableau_zones_lignes):
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger == '.':
        raise PreventUpdate
    row = tableau_zones_lignes.index(zone['properties']['id'])
    return [{'row': row, 'column': 0}]
#&& trigger === "tableau_des_sites.active_cell"
app.clientside_callback(
    """function(feature, cell, hideout) {
    if (feature == undefined && dash_clientside.callback_context.triggered[0].prop_id === '.') 
        return dash_clientside.no_update
    else if (dash_clientside.callback_context.triggered[0].prop_id === "tableau_des_sites.active_cell" )
        return {...hideout, selected_site: cell.row_id}
    else
        return {...hideout, selected_site: feature.properties.id}
    }""",
    Output("carte_sites", "hideout"),
    Input("carte_sites", "click_feature"),
    Input("tableau_des_sites", "active_cell"),
    State("carte_sites", "hideout")
    )

app.clientside_callback(
    """function(feature, hideout) {
    if (feature == undefined) 
        return hideout
    else
        return {...hideout, selected_site: feature.properties.id}
    }""",
    Output("zone_humide_unique", "hideout"),
    Input("zone_humide_unique", "click_feature"),
    State("carte_sites", "hideout")
    )

if __name__ == '__main__':
    app.run_server(debug=True)
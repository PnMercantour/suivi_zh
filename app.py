import dash
import dash_html_components as html
import dash_leaflet as dl
import dash_table
from dash.dependencies import Input, Output, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import arrow_function, assign
import json
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

#création d'un dictionaire pour les couleurs des polygones
js_style = assign("""
function(feature) {
    let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500", sel: "FFFFFF"};
    console.log(feature);
    return {color: t[feature.properties.etat_zh]}
}""")

fonction_couleur_carte = assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    if(feature.properties.etat_zh){
        layer.bindTooltip(feature.properties.etat_zh)
    }
}
""")

# Chargement de sites.json utilisation pour les données du tableaux des sites
with open('assets/sites.json', 'r') as fichier:
    sites_json = json.loads(fichier.read())
    fichier.close()

# GeoJSON pour les sites
carte_sites = dl.GeoJSON(id="carte_sites", url=app.get_asset_url('sites.json'), options=dict(onEachFeature=assign("""
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
baseLayer = dl.TileLayer()

# dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
#                    layers="TOPO-OSM-WMS", format="image/png")
# Le layout
app.layout = html.Div([
    html.Div([
        tableau_des_sites
    ],style={'float':'left', 'paddingRight': '5vh'}),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, carte_sites],
        center=[44.3, 7], zoom=9,),style={'display':'flex', 'paddingBottom':'5vh'}),
    html.Div([
        dl.Map(id="site_unique", children=[baseLayer, dl.GeoJSON(id='zone_humide_unique', options=dict(onEachFeature=fonction_couleur_carte, style=js_style)), dl.Polygon(id="selection", positions=[], color="#000000")],zoom=15),
        tableau_des_zones
    ], style={'display':'flex', 'maxHeight': '50vh'}), html.Div(id='test')
])

def trouve_le_centroid(id):
    for elem in sites_json['features']:
        if elem['properties']['id'] == id:
            return elem['geometry']['coordinates'][::-1]

def trouve_le_fichier_du_site(id):
    return app.get_asset_url('sites/'+str(id)+'.json')

@app.callback([Output('zone_humide_unique', 'url'), Output('site_unique', 'center')], [Input('carte_sites', 'click_feature'), Input('tableau_des_sites', 'selected_cells')])
def maj_carte_site_unique(feature, cell):
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger == '.':
        raise PreventUpdate
    if trigger == 'carte_sites.click_feature':
        id = feature['properties']['id']
        return trouve_le_fichier_du_site(id), trouve_le_centroid(id)
    if trigger == 'tableau_des_sites.selected_cells':
        id = cell[0]['row_id']
        return trouve_le_fichier_du_site(id), trouve_le_centroid(id)

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

@app.callback([Output('tableau_des_zones', 'active_cell')], [Input('zone_humide_unique','click_feature'), Input('tableau_des_zones', 'derived_viewport_row_ids')]) 
def selection_cellule_tableau_des_zones(zone, tableau_zones_lignes):
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger == '.':
        raise PreventUpdate
    row = tableau_zones_lignes.index(zone['properties']['id'])
    return [{'row': row, 'column': 0}]

# @app.callback(Output("zone_humide_unique", "children"), [Input("zone_humide_unique", "click_feature"), Input("tableau_des_zones", "active_cell")])
# def zh_selectionnee_change_couleur(input,cell):
#     trigger = dash.callback_context.triggered[0]['prop_id']
#     if trigger == '.':
#         raise PreventUpdate
#     elif trigger == 'zone_humide_unique.click_feature':
#         points = [point[::-1] for point in input['geometry']['coordinates'][0][0]]
#         return dl.Polygon(positions=points, color="#0000FF")
#     else :
#         print(cell)

app.clientside_callback(
    """
    function(feature) {
        let coor = feature.geometry.coordinates[0][0]
        let returnTab = []
        coor.forEach(element => returnTab.push(element.reverse()))
        return returnTab
    }
    """,
Output("selection", "positions"), Input("zone_humide_unique", "click_feature"))

if __name__ == '__main__':
    app.run_server(debug=True)

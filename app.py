import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
from dash_extensions.javascript import arrow_function
import json
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Lecture des csv
points = pd.read_csv("data/sites.csv", ';')
zh = pd.read_csv("data/zh.csv", ';')
#création d'un dictionaire pour les couleurs des polygones
color = {'bon': 'green', 'moyen': 'yellow', 'mauvais': 'red'}

# GeoJSON pour les points
sites = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="sites")
# GeoJSON pour les zones humides
zones_humides = dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zh.loc[i]['geojson']), "properties":{"site": zh.loc[i]['nom_site']}}for i in range(len(zh))]}, hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')), id="zones_humides")

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
baseLayer = dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png")
# Le layout
app.layout = html.Div([
    html.Div([dl.Map(children = [baseLayer, sites, zones_humides],
        center=[44.3, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto"}, id="map"),
    dl.Map(style={'width': '30%', 'height': '50vh', 'margin': "auto"},zoom=15,id="mini_map")], style={'display':'flex'}),
    html.Div([dash_table.DataTable(
    id='table',
    columns=[{"name": "nom site", "id": "nom_site"}],
    data=points.to_dict('records'),
    sort_action='native',
    filter_action='native',
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
)], id="test"), html.Div(id="test2")
])
#, Output("table", "active_cell"), Output("table", "filter_query")
# @app.callback([Output("mini_map", "children"), Output("mini_map", "center"), Output("sites", "click_feature"), Output("table", "active_cell")], [Input("table", "selected_cells"), Input("table", "data"), Input("sites", "click_feature")])
# def zh_mini_map(selectionTab, dataTab, feature):
#   if feature is not None:
#     for item in zh['geojson'] :
#       if json.loads(item) == feature['geometry']: 
#         row = zh[zh['geojson']==item]['id']
#   if feature is not None:
#       toutes_zones = zh[zh['nom_site']==feature['properties']['nom_site']]['geojson']
#       centre = json.loads(points[points['nom_site']==feature['properties']['nom_site']]['centroid'].all())['coordinates'][::-1]
#       return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre, None , {'row': int(1), 'column': 0} #, "{nom_site} contains"+feature['properties']['site']
#   if selectionTab is not None:
#     toutes_zones = zh[zh['nom_site']==dataTab[selectionTab[0]['row']]['nom_site']]['geojson']
#     centre = json.loads(points[points['nom_site']==dataTab[selectionTab[0]['row']]['nom_site']]['centroid'].all())['coordinates'][::-1]
#     return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre, None , None #, None
#   else:
#     return [baseLayer, sites], [44.3, 7], None , None #, None

@app.callback([Output("mini_map", "children"), Output("mini_map", "center"), Output("test", "style")], [Input("table", "selected_cells"), Input("table", "data"), Input("sites", "click_feature")])
def test(cell, data, feature):
    if dash.callback_context.triggered[0]['prop_id'] == 'sites.click_feature':
        toutes_zones = zh[zh['nom_site']==feature['properties']['nom_site']]['geojson']
        centre = json.loads(points[points['nom_site']==feature['properties']['nom_site']]['centroid'].all())['coordinates'][::-1]
        return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre , {"display":"None"} #, {'row': int(1), 'column': 0} #, "{nom_site} contains"+feature['properties']['site']
    else:
        toutes_zones = zh[zh['nom_site']==data[cell[0]['row']]['nom_site']]['geojson']
        centre = json.loads(points[points['nom_site']==data[cell[0]['row']]['nom_site']]['centroid'].all())['coordinates'][::-1]
        return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre, None #, None #, None


if __name__ == '__main__':
    app.run_server(debug=True)


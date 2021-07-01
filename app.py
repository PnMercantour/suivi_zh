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
sites = dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry" : json.loads(point)} for point in points['centroid']]})
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
    dash_table.DataTable(
    id='table',
    columns=[{"name": "nom site", "id": "nom_site"},{"name": "surface", "id": "surface"} ,{"name": "état", "id": "etat"}],
    data=zh.to_dict('records'),
    sort_action='native',
    filter_action='native',
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
), html.Div(id='test')
])
#, Output("table", "active_cell"), Output("table", "filter_query")
@app.callback([Output("mini_map", "children"), Output("mini_map", "center"), Output("zones_humides", "click_feature"), Output("table", "active_cell")], [Input("table", "selected_cells"), Input("table", "data"), Input("zones_humides", "click_feature")])
def zh_mini_map(selectionTab, dataTab, feature):
  if feature is not None:
    for item in zh['geojson'] :
      if json.loads(item) == feature['geometry']: 
        row = zh[zh['geojson']==item]['id']+1
  if feature is not None:
      toutes_zones = zh[zh['nom_site']==feature['properties']['site']]['geojson']
      centre = json.loads(points[points['nom_site']==feature['properties']['site']]['centroid'].all())['coordinates'][::-1]
      return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre, None , {'row': int(row), 'column': 0} #, "{nom_site} contains"+feature['properties']['site']
  if selectionTab is not None:
    toutes_zones = zh[zh['nom_site']==dataTab[selectionTab[0]['row_id']-1]['nom_site']]['geojson']
    centre = json.loads(points[points['nom_site']==dataTab[selectionTab[0]['row_id']-1]['nom_site']]['centroid'].all())['coordinates'][::-1]
    return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre, None , None #, None
  else:
    return [baseLayer, sites], [44.3, 7], None , None #, None

# @app.callback(Output("table", "filter_query"), Input("test", "children"))
# def test(filter):
#   return "{nom_site} contains Plate"

if __name__ == '__main__':
    app.run_server(debug=True)


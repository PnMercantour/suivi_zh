import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output, State, MATCH, ALL
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
zones_humides2 = dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zh.loc[i]['geojson']), "properties":{"site": zh.loc[i]['nom_site']}}for i in range(len(zh))]}, hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')), id="test")
# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
baseLayer = dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png")
# Le layout
app.layout = html.Div([
    html.Div([dl.Map(children = [baseLayer, sites, zones_humides2],
        center=[44.3, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto"}, id="map"),
    html.Div([dcc.Checklist(id="selection_zone_humide",options=[{"label": nom, "value": nom}for nom in zh['nom_site'].unique()])], style={'maxHeight':'50vh', 'width':'400px', 'overflowY': 'auto', 'paddingLeft': '1vh'}, id="liste")], style={'display': 'flex'}),
    html.Div(id="site_selectionne"),
    dl.Map(style={'width': '30%', 'height': '50vh', 'margin': "auto"},zoom=15,id="mini_map"),
])

@app.callback(Output('selection_zone_humide', 'value'), Input('selection_zone_humide', 'value'))
def maj_checlist(v):
  if v:
    if len(v) > 1:
      return v[1:]
    else:
      return v
  else:
    return []

@app.callback([Output("mini_map", "children"), Output("mini_map", "center")], [Input("map", "click_feature")])
def site_click(feature):
    if feature is not None:
      toutes_zones = zh[zh['nom_site']==feature['properties']['site']]['geojson']
      centre = json.loads(points[points['nom_site']==feature['properties']['site']]['centroid'].all())['coordinates'][::-1]
      return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre
    else:
      return [baseLayer, sites, zones_humides2], [44.3, 7]

# @app.callback([Output("mini_map", "children"), Output("mini_map", "center")], Input("selection_zone_humide", 'value'))
# def zh_mini_map(nom_site):
#   if nom_site:
#     nom_site = nom_site[0]
#     toutes_zones = zh[zh['nom_site']==nom_site]['geojson']
#     centre = json.loads(points[points['nom_site']==nom_site]['centroid'].all())['coordinates'][::-1]
#     return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre
#   else:
#     return [baseLayer, sites, zones_humides], [44.3, 7]

if __name__ == '__main__':
    app.run_server(debug=True)


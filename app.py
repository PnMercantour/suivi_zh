import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
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
zones_humides = dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(site)}for site in zh['geojson']]})

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
df = [dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png"), sites, zones_humides]
# Le layout
app.layout = html.Div([
    html.Div([dl.Map(children = df,
        center=[44.3, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto"}, id="map"),
    html.Div([dcc.RadioItems(id="selection_zone_humide",options=[{"label": nom, "value": nom}for nom in zh['nom_site'].unique()])], style={'maxHeight':'50vh', 'width':'400px', 'overflowY': 'auto', 'paddingLeft': '1vh'}, id="liste")], style={'display': 'flex'}),
])

@app.callback([Output("map", "children"), Output("map", "center")], Input("selection_zone_humide", 'value'))
def test(nom_site):
  if nom_site:
    toutes_zones = zh[zh['nom_site']==nom_site]['geojson']
    centre = json.loads(points[points['nom_site']==nom_site]['centroid'].all())['coordinates'][::-1]
    return [dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png"), dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre
  else:
    return df, [44.3, 7]

if __name__ == '__main__':
    app.run_server(debug=True)


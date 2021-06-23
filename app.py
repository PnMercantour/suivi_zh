import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
import pandas as pd
import json
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Lecture des csv
points = pd.read_csv("data/sites.csv", ';')
zh = pd.read_csv("data/zh.csv", ';')
#création d'un dictionaire pour les couleurs des polygones
color = {'bon': 'green', 'moyen': 'yellow', 'mauvais': 'red'}
# Ces lignes ne sont utiles que pour inverser les entrées des tableaux des csv. Sinon le parc se retrouve en Ethiopie
coor = [{'lat' : json.loads(points['centroid'][i])['coordinates'][1], 'lon' : json.loads(points['centroid'][i])['coordinates'][0]} for i in range(len(points))]

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
df = [dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png")]
# Ajout des points
for obj in coor:
    df.append(dl.GeoJSON(data=dlx.dicts_to_geojson([obj])))
# Ajout des polygones
for item in zh['geojson']:
    df.append(dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(item)}]}))

# Le layout
app.layout = html.Div([
    dl.Map(children = df,
        center=[44.3, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
])

if __name__ == '__main__':
    app.run_server(debug=True)


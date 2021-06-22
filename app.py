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
points = pd.read_csv("data/sites2.csv", ';')
zh = pd.read_csv("data/zh.csv", ';')
# Ces lignes ne sont utiles que pour inverser les entrées des tableaux des csv. Sinon le par se retrouve en Ethiopie
coor = [{'lat' : json.loads(points['centroid'][i])['coordinates'][1], 'lon' : json.loads(points['centroid'][i])['coordinates'][0]} for i in range(len(points))]
poly = [json.loads(zh['geojson'][i])['coordinates'][0][0] for i in range(len(zh))]
for item in poly:
    for array in item:
        array.reverse()

# Création de la dataframe, un tableau passé en paramètre de dl.Map
# Le fond de carte
df = [dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                    layers="TOPO-OSM-WMS", format="image/png")]
# Ajout des points
for i in range(len(coor)):
    df.append(dl.GeoJSON(data=dlx.dicts_to_geojson([coor[i]])))
# Ajout des polygones
for i in range(len(poly)):
    df.append(dl.Polygon(positions=poly[i]))

# Le layout
app.layout = html.Div([
    dl.Map(children=df, 
        center=[45, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
])

if __name__ == '__main__':
    app.run_server(debug=True)


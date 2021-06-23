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


# Création de la couche raster
# Le fond de carte
baseLayer = dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                            layers="TOPO-OSM-WMS", format="image/png")
# # Ajout des points
# for i in range(len(coor)):
#     df.append(dl.GeoJSON(data=dlx.dicts_to_geojson([coor[i]])))
# # Ajout des polygones
# for i in range(len(poly)):
#     df.append(dl.Polygon(positions=poly[i], color=color[zh['etat'][i]]))
f = open('data/features.json',)
siteData = json.load(f)
f.close()
siteLayer = dl.GeoJSON(data=siteData, id="sites")

# Le layout
app.layout = html.Div([
    dl.Map(children=[baseLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="site_selectionne")])


@app.callback(Output("site_selectionne", "children"), [Input("sites", "click_feature")])
def site_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['site']}"


if __name__ == '__main__':
    app.run_server(debug=True)

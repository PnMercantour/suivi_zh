import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
import pandas as pd
import dash_html_components as html
import json
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Le fond de carte
baseLayer = dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
                             layers="TOPO-OSM-WMS", format="image/png")

siteLayer = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="sites")
 # Le layout
app.layout = html.Div([
    html.Img(src=app.get_asset_url('morgon.png')),
    dl.Map(children=[baseLayer, siteLayer],
            center=[44.3, 7], zoom=9,
            style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
            html.Div(id="site_selectionne")])

@app.callback(Output("site_selectionne", "children"), [Input("sites", "click_feature")])
def site_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['nom_site']}"

if __name__ == '__main__':
    app.run_server(debug=True)
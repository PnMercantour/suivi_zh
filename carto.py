import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign, arrow_function
from dotenv import load_dotenv
import json

load_dotenv('.env')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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

siteLayer = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="sites", options=dict(onEachFeature=assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    console.log(feature);
    console.log(layer);
    if(feature.properties.nom_site){
        layer.bindTooltip(feature.properties.nom_site)
    }
}
""")))
# Le layout
app.layout = html.Div([
    dl.Map(children=[baseLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="site_selectionne"),
])


if __name__ == '__main__':
    app.run_server(debug=True)

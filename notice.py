import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
from dash_table import DataTable

from dash_extensions.javascript import assign, arrow_function
from dotenv import load_dotenv
import pandas
from pathlib import Path

import json

load_dotenv('.env/.env')

df = pandas.read_csv(
    Path(Path(__file__).parent, 'assets', 'notice.csv'))

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

siteLayer = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="siteLayer", options=dict(onEachFeature=assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    cachedData.siteTable[feature.properties.id] = feature.geometry;
    console.log(cachedData.siteTable);
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
    html.Div([
        DataTable(
            id='noticeTable',
            columns=[
                dict(name='Notices', id='link',
                     type='text', presentation='markdown'),
            ],
            data=None
        )])])


@ app.callback(
    Output("noticeTable", "data"),
    Input("siteLayer", "click_feature"))
def updateNoticeTable(feature):
    if feature:
        id = feature['properties']['id']
        data = df[df["id_site"] == id].to_dict('records')
        for item in data:
            item['link'] = f"""[{item['nom']}]({app.get_asset_url('pdf/' + item['nom']).replace(' ', '%20')})"""
        return data
    else:
        return None


if __name__ == '__main__':
    app.run_server(debug=True)

import os
import dash
import dash_html_components as html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State
from dash_extensions.javascript import assign
from dotenv import load_dotenv

load_dotenv('.env/.env')
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

point_to_layer = assign("""function(feature, latlng, context){
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {
        circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
    }
    else
        circleOptions= {color: "blue"};
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

siteLayer = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="sites", options=dict(pointToLayer=point_to_layer, hideout=dict(selected_site=-1), onEachFeature=assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    if(feature.properties.nom_site){
        layer.bindTooltip(feature.properties.nom_site)
    }
}
""")))
# Le layout
app.layout = html.Div([
    dl.Map(id='map', children=[baseLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="site_selectionne"),
])

app.clientside_callback(
    """(click_feature, click_lat_lng, hideout) => [{...hideout, selected_site: (click_feature)? click_feature.properties.id : -1}, null]""",
    Output("sites", "hideout"),
    Output("sites", "click_feature"),
    Input("sites", "click_feature"),
    Input("map", "click_lat_lng"),
    State("sites", "hideout"))
if __name__ == '__main__':
    app.run_server(debug=True)

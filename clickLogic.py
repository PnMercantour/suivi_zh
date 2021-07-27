import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output, State
from dash_extensions.javascript import assign, arrow_function
from dotenv import load_dotenv
import json

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

sitePointToLayer = assign("""function(feature, latlng, context){
    if (context.props.click_feature) {
        if (feature.properties.id == context.props.click_feature.properties.id) {
            circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
        } else if (feature.properties.vallee == -14) {
            circleOptions= {color: "orange"};
        } else {
            circleOptions= {color: "blue"};
        }
    } else {
        circleOptions= {color: "blue"};
    }
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

siteLayer = dl.GeoJSON(url=app.get_asset_url('sites.json'), id="siteLayer", hideout=dict(id=None), options=dict(pointToLayer=sitePointToLayer, onEachFeature=assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    cachedData.siteTable[feature.properties.id] = feature;
    if(feature.properties.nom_site){
        layer.bindTooltip(feature.properties.nom_site)
    }
}
""")))
# Le layout
app.layout = html.Div([
    dl.Map(id="map", children=[baseLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(dcc.Input(
        id="siteInput",
        type='number',
        value=None)),
    html.Div(id="siteInfo"),
])


@ app.callback(Output("siteInfo", "children"), [Input("siteLayer", "click_feature")])
def updateSiteInfo(feature):
    """Callback séparée possible pour site info car pas de boucle."""
    if feature:
        return f"Site sélectionné: {feature['properties']['id']}"
    else:
        return "Pas de sélection site"


@ app.callback(Output("siteLayer", "hideout"), Input("siteLayer", "click_feature"), State("siteLayer", "hideout"))
def redrawSite(feature, hideout):
    """
    La carte n'est redessinée que lorsque hideout change (elle est insensible au click_feature).
    """
    print('hideout', hideout)
    if feature:
        new_id = feature['properties']['id']
    else:
        new_id = None
    if new_id != hideout['id']:
        return dict(id=new_id)
    return dash.no_update


#    Tous les objets interdépendants doivent être en output dans cette callback pour éviter de créer des boucles.
app.clientside_callback(
    """function(feature, id, click_lat_lng) {
        //console.log(dash_clientside.callback_context);
        const triggers = dash_clientside.callback_context.triggered;
        if (triggers.some((o) => o.prop_id == "siteLayer.click_feature"))
            return [feature, feature.properties.id];
        if (triggers.some((o) => o.prop_id == "map.click_lat_lng"))
            return [undefined, undefined];
        // on prend la valeur du widget input.
        return [cachedData.siteTable[id], id];
    }""",
    Output("siteLayer", "click_feature"),
    Output("siteInput", "value"),
    Input("siteLayer", "click_feature"),
    Input("siteInput", "value"),
    Input("map", "click_lat_lng"))


if __name__ == '__main__':
    app.run_server(debug=True)

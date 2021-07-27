import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Button import Button
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

valleeLayer = dl.GeoJSON(
    url=app.get_asset_url('vallees.json'),
    id="valleeLayer",
    options=dict(onEachFeature=assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    cachedData.valleeTable[feature.properties.id] = feature;
    if(feature.properties.nom){
        layer.bindTooltip(feature.properties.nom)
    }
}
""")))

sitePointToLayer = assign("""function(feature, latlng, context){
    if (context.props.hideout) {
        if (feature.properties.id == context.props.hideout.id) {
            circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
        } else if (feature.properties.id_vallee == context.props.hideout.id_vallee) {
            circleOptions= {color: "red", fillColor: "blue"};
        } else {
            circleOptions= {color: "blue"};
        }
    } else {
        circleOptions= {color: "blue"};
    }
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

siteLayer = dl.GeoJSON(
    url=app.get_asset_url('sites.json'),
    id="siteLayer",
    hideout=dict(id=None, id_vallee=None),
    options=dict(
        pointToLayer=sitePointToLayer,
        onEachFeature=assign("""
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
    dl.Map(id='map', children=[baseLayer, valleeLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(dcc.Input(
        id="valleeInput",
        type='number',
        value=None)),
    html.Div(id="valleeInfo"),
    html.Div(dcc.Input(
        id="siteInput",
        type='number',
        value=None)),
    html.Div(id="siteInfo")
])


@ app.callback(Output("siteInfo", "children"), Input("siteLayer", "click_feature"))
def updateSiteInfo(feature):
    if feature:
        return f"Site sélectionné: {feature['properties']['id']}"
    else:
        return "Pas de sélection site"


@ app.callback(Output("valleeInfo", "children"), Input("valleeLayer", "click_feature"))
def updateValleeInfo(feature):
    if feature:
        return f"Vallée sélectionnée: {feature['properties']['id']}"
    else:
        return "Pas de sélection vallée"


app.clientside_callback(
    """function(
  site_feature,
  site_input,
  vallee_feature,
  vallee_input,
  click_lat_lng,
  hideout
) {
  console.log(vallee_feature);
  const triggers = dash_clientside.callback_context.triggered;
  if (triggers.some((o) => o.prop_id == "siteLayer.click_feature")){
    // update "site" and "vallee"
    return [
      {id: site_feature.properties.id, id_vallee: site_feature.properties.id_vallee},
      site_feature,
      site_feature.properties.id,
      cachedData.valleeTable[site_feature.properties.id_vallee],
      site_feature.properties.id_vallee
    ];
  }
  if (triggers.some((o) => o.prop_id == "valleeLayer.click_feature")) {
    // update "vallee" and reset "site"
    return [{id: undefined, id_vallee: vallee_feature.properties.id}, undefined, undefined, cachedData.valleeTable[vallee_feature.properties.id], vallee_feature.properties.id];
  }
  if (triggers.some((o) => o.prop_id == "map.click_lat_lng")){
    return [{id: undefined, id_vallee: undefined}, undefined, undefined, undefined, undefined];
  }
  if (triggers.some((o) => o.prop_id == "siteInput.value")){
    let new_site_feature = site_input? cachedData.siteTable[site_input] : undefined;
    let new_id_vallee = new_site_feature? new_site_feature.properties.id_vallee: undefined;
    let vallee_feature = new_id_vallee? cachedData.valleeTable[new_id_vallee]: undefined;
    return [{id: site_input, id_vallee: new_id_vallee}, new_site_feature, site_input, vallee_feature, new_id_vallee];
    }
  if (triggers.some((o) => o.prop_id == "valleeInput.value")){
    let vallee_feature = vallee_input? cachedData.valleeTable[vallee_input]: undefined;
    return [{id: undefined, id_vallee: vallee_input}, undefined, undefined, vallee_feature, vallee_input];
  }
  return[{id: undefined, id_vallee: undefined}, undefined, undefined, undefined, undefined];
}
""",
    Output("siteLayer", "hideout"),
    Output("siteLayer", "click_feature"),
    Output("siteInput", "value"),
    Output("valleeLayer", 'click_feature'),
    Output("valleeInput", "value"),
    Input("siteLayer", "click_feature"),
    Input("siteInput", "value"),
    Input("valleeLayer", "click_feature"),
    Input("valleeInput", "value"),
    Input("map", "click_lat_lng"),
    State("siteLayer", "hideout"))


if __name__ == '__main__':
    app.run_server(debug=True)

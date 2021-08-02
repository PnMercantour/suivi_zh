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
from pathlib import Path
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


def featurePropertiesFromJson(kind):
    with open(Path(Path(__file__).parent, 'assets', f'{kind}.json'), 'r') as file:
        json_data = json.load(file)
        return [feature['properties'] for feature in json_data['features']]


# keep all site options in memory
site__feature_properties = featurePropertiesFromJson('sites')

vallee_dropdown = dcc.Dropdown(
    id="valleeDropdown", placeholder='Vallée sélectionnée?', options=[{'label': property['nom'], 'value': property['id']} for property in featurePropertiesFromJson('vallees')])

site_dropdown = dcc.Dropdown(
    id='siteDropdown', placeholder='Site sélectionné?', options=[{'label': property['nom_site'], 'value': property['id']} for property in site__feature_properties])

overall_info = html.Div(id='overallInfo', hidden=False, children="""
Cette section s'affiche lorsque aucune région n'est sélectionnée.
Elle affiche des indicateurs pour l'ensemble du Parc national du Mercantour.
""")
vallee_info = html.Div(id='valleeInfo', hidden=True, children="""
Cette section s'affiche lorsque une vallée est sélectionné, mais pas de site.
Elle affiche des indicateurs pour l'ensemble de la vallée.
""")
site_info = html.Div(id='siteInfo', hidden=True, children="""
Cette section s'affiche lorsqu'un site est sélectionné.
Elle affiche le détail des zones humides et des indicateurs pour ce site.""")
# Le layout
app.layout = html.Div([
    html.Div(children=[vallee_dropdown, site_dropdown]),
    dl.Map(id='map', children=[baseLayer, valleeLayer, siteLayer],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(children=[overall_info, vallee_info, site_info])
])


@app.callback(Output("overallInfo", "hidden"), Output("valleeInfo", "hidden"), Output("siteInfo", "hidden"), Input("siteLayer", "hideout"))
def toggleInfo(hideout):
    if hideout['id']:
        return [True, True, False]
    if hideout['id_vallee']:
        return [True, False, True]
    return [False, True, True]


@ app.callback(Output("siteDropdown", "options"), Input("valleeDropdown", "value"))
def updateSiteDropdown(id_vallee):
    return [{'label': property['nom_site'], 'value': property['id']} for property in site__feature_properties if id_vallee == None or property['id_vallee'] == id_vallee]


app.clientside_callback(
    """function(
  site_feature, vallee_feature, click_lat_lng,
  site_dropdown,
  vallee_dropdown,
  hideout
) {
  //console.log(dash_clientside.callback_context);
  const triggers = dash_clientside.callback_context.triggered;

  let id = null, id_vallee = null;

  if (triggers.some((o) => o.prop_id == "siteLayer.click_feature")){
    // update "site" and "vallee"
    if (site_feature != null) {
      id = (site_feature.properties.id != hideout.id)? site_feature.properties.id: null;
      id_vallee = site_feature.properties.id_vallee;
    } else {
      // should not happen
      console.log( 'Warning, site click_feature triggered with null feature', hideout);
      id = null;
      id_vallee = hideout.id_vallee;
    }
  } else
  if (triggers.some((o) => o.prop_id == "valleeLayer.click_feature")) {
    // update "vallee" and reset "site"
    id = null;
    if (vallee_feature != null) {
        id_vallee = (vallee_feature.properties.id != hideout.id_vallee)? vallee_feature.properties.id: null;
    } else {
      // should not happen
      console.log( 'Warning, vallee click_feature triggered with null feature', hideout);
      id_vallee = null;
    }
  } else
  if (triggers.some((o) => o.prop_id == "map.click_lat_lng")){
    id = null;
    id_vallee = null;
  } else
  if (triggers.some((o) => o.prop_id == "siteDropdown.value")){
    if (site_dropdown != null){
      id = site_dropdown;
      id_vallee = (cachedData.siteTable[id]) ? cachedData.siteTable[id].properties.id_vallee : hideout.id_vallee;
    } else {
      id = null;
      id_vallee = hideout.id_vallee;
    }
  } else
  if (triggers.some((o) => o.prop_id == "valleeDropdown.value")){
    id = null;
    id_vallee = vallee_dropdown;
  }

  let result = [
    {...hideout, id, id_vallee}, null, //siteLayer
    null, //valleeLayer
    id, //siteDropdown
    id_vallee, //valleeDropdown
    ];
  //console.log('result = ', result);
  return result;
}
""",
    Output("siteLayer", "hideout"), Output("siteLayer", "click_feature"),
    Output("valleeLayer", 'click_feature'),
    Output("siteDropdown", "value"),
    Output("valleeDropdown", "value"),

    Input("siteLayer", "click_feature"),
    Input("valleeLayer", "click_feature"),
    Input("map", "click_lat_lng"),
    Input("siteDropdown", "value"),
    Input("valleeDropdown", "value"),
    State("siteLayer", "hideout"))

if __name__ == '__main__':
    app.run_server(debug=True)

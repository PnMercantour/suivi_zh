import os
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_leaflet as dl
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
from pathlib import Path
import pandas
from dotenv import load_dotenv
import json
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
load_dotenv('.env/.env')

app = dash.Dash(__name__)

df = pandas.read_csv(
    Path(Path(__file__).parent, 'assets', 'habitat.csv'))

def featurePropertiesFromJson(kind):
    with open(Path(Path(__file__).parent, 'assets', f'{kind}.json'), 'r') as file:
        json_data = json.load(file)
        return [feature['properties'] for feature in json_data['features']]

# keep all site options in memory
site__feature_properties = featurePropertiesFromJson('sites')

#assign(""" () => {let test = {}} """)
#création d'un dictionaire pour les couleurs des polygones
js_style = assign("""
function(feature, context) {
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_zone) {return {color:"#000000"}}
    else {
        let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500"};
        return {color: t[feature.properties.etat_zh]}}
}""")

fonction_couleur_carte = assign("""
(feature, layer) => {
    if(!feature.properties){
        return
    }
    cachedData.zhTable[feature.properties.id] = {surface : feature.properties.surface, etat: feature.properties.etat_zh}
    if(feature.properties.etat_zh){
        layer.bindTooltip(feature.properties.etat_zh)
    }
}
""")

sitePointToLayer = assign("""function(feature, latlng, context){
    if (context.props.hideout) {
        if (feature.properties.id == context.props.hideout.selected_site) {
            circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
        } else if (feature.properties.id_vallee == context.props.hideout.selected_vallee) {
            circleOptions= {color: "red", fillColor: "blue"};
        } else {
            circleOptions= {color: "blue"};
        }
    } else {
        circleOptions= {color: "blue"};
    }
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

point_to_layer = assign("""function(feature, latlng, context){
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {
        circleOptions= {color: "red", fillColor: "red", fillOpacity: 0.8};
    }
    else
        circleOptions= {color: "blue"};
    return L.circleMarker(latlng, circleOptions)  // send a simple circle marker.
}""")

# GeoJSON pour les sites
siteLayer = dl.GeoJSON(id="siteLayer", url=app.get_asset_url('sites.json'), hideout={'selected_site': None, 'selected_vallee': None}, options=dict(pointToLayer=sitePointToLayer, onEachFeature=assign("""
    (feature, layer) => {
        if(!feature.properties){
            return
        }
        cachedData.siteTable[feature.properties.id] = feature
        if(feature.properties.nom_site){
            layer.bindTooltip(feature.properties.nom_site)
        }
}
""")))

zhLayer = dl.GeoJSON(id='zhLayer', hideout={'selected_zone': None, 'selected_site': None, 'nom_site': None},
    options=dict(pointToLayer=point_to_layer,  
    onEachFeature=fonction_couleur_carte, style=js_style), 
    zoomToBounds=True)

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

zhTable = dash_table.DataTable(
            id='zhTable',
            columns=[],
            data=[],
            sort_action='native',
            filter_action='native',
            style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ], page_size=10,  merge_duplicate_headers=True,
)

# siteTable = dash_table.DataTable(
#         id='siteTable',
#         columns=[{"name": "nom_site", "id": "nom_site"}],
#         data=[{'nom_site':index}['nom_site'] for index in site__feature_properties],
#         sort_action='native',
#         filter_action='native',
#         style_data_conditional=[
#             {'if': {'row_index': 'odd'},
#             'backgroundColor': 'rgb(248, 248, 248)'
#             }
#         ]
# )

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
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

# Le layout
app.layout = html.Div([
    html.Div(id="dropdownDiv", children=[
        dcc.Dropdown(id="valleeDropdown", options = [{'label': property['nom'], 'value': property['id']} for property in featurePropertiesFromJson('vallees')]), 
        dcc.Dropdown(id="siteDropdown")
    ]),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, valleeLayer, siteLayer],
        center=[44.3, 7], zoom=9),style={'display':'flex', 'paddingBottom':'5vh'}),
    html.Div(id="div_zh",children=[
        dl.Map(id="site_unique", children=[baseLayer, zhLayer], center=[44.3, 7]),
        zhTable,
        dcc.Graph(id="pie-chart", figure=px.pie(df[df["id_zh"] == 374],
              values='proportion', names='code'), style={"backgroundColor": "yellow"})
    ], style={'display':'flex', 'flexWrap': 'wrap', 'maxHeight': '50vh'})
])

app.clientside_callback(
    """function(dropdown_value, valleeDropdown_value, site_feature, vallee_feature, click_lat_lng, hideout) {
        const triggers = dash_clientside.callback_context.triggered
        let return_hideout = {selected_site: null, selected_vallee: null}
        let return_active_cell = {'row': -1, 'column': 0}
        let return_zhLayer_url = "assets/sites/"
        let return_valleeDropdown_value
        if(triggers.some((o) => o.prop_id === "siteLayer.click_feature")){
            return_hideout = {selected_site: site_feature.properties.id, selected_vallee: site_feature.properties.id_vallee, nom_site: site_feature.properties.nom_site}
            return_zhLayer_url += site_feature.properties.id+".json"
            return_vallee_feature = cachedData.valleeTable[site_feature.properties.id_vallee]
        }
        if(triggers.some((o) => o.prop_id === "valleeLayer.click_feature")) {
            return_hideout = {selected_site: null, selected_vallee: vallee_feature.properties.id}
        }
        if(site_feature === undefined && vallee_feature===undefined) {
            return_hideout = {selected_site: null, selected_vallee: null}
            dropdown_value = 0 
        }
        if(triggers.some((o) => o.prop_id === "siteDropdown.value")) {
            cachedData.siteTable.forEach((elem)=>{if(elem.properties.id===dropdown_value){return_valleeDropdown_value = elem.properties.id_vallee}})
            return_hideout = {selected_site: dropdown_value, selected_vallee: return_valleeDropdown_value}
        }
        if(triggers.some((o) => o.prop_id === "valleeDropdown.value")) {
            return_hideout = {...return_hideout, selected_vallee: valleeDropdown_value}
        }
        return_valleeDropdown_value = return_valleeDropdown_value ? return_valleeDropdown_value : return_hideout.selected_vallee
        const return_siteDropdown_value = return_hideout.selected_site ? return_hideout.selected_site : dropdown_value
        console.log(return_hideout)
        return [return_hideout, {}, {}, return_zhLayer_url, return_valleeDropdown_value, return_siteDropdown_value]
    }""",
    Output("siteLayer", "hideout"),
    Output("siteLayer", "click_feature"),
    Output("valleeLayer", "click_feature"),
    Output("zhLayer", "url"),
    Output("valleeDropdown", "value"),
    Output("siteDropdown", "value"),
    Input("siteDropdown", "value"),
    Input("valleeDropdown", "value"),
    Input("siteLayer", "click_feature"),
    Input("valleeLayer", "click_feature"),
    Input("parc", "click_lat_lng"), 
    State("siteLayer", "hideout"),
)
#, Output("valleeDropdown", "value")
@ app.callback(Output("siteDropdown", "options"), Input("valleeDropdown", "value"))
def dropdownsOptions(valleeValue):
    if valleeValue != 0 and valleeValue != None:
        siteOptions = [{'label': index['nom_site'], 'value': index['id']} for index in filter(lambda item : item['id_vallee']==valleeValue, site__feature_properties)]
    else:
        siteOptions = [{'label': property['nom_site'], 'value': property['id']} for property in site__feature_properties]
    return siteOptions
    
# app.clientside_callback(
#     """
#     function(zhfeature, hideout, data){
#         data = []
#         cachedData.zhTable.map((feature, id) => data.push({surface: feature.surface, etat: feature.etat, id}))
#         const triggers = dash_clientside.callback_context.triggered
#         let return_hideout = hideout
#         if(triggers.some((o) => o.prop_id === "zhLayer.click_feature")){
#             return_hideout = {...return_hideout, selected_zone: zhfeature.properties.id}
#         }
#         const zhTable_columns = [{"name": [hideout.nom_site, "surface"], "id": "surface"}, {"name": [hideout.nom_site, "état"], "id": "etat"}]
#         cachedData.zhTable = []
#         return [data, zhTable_columns, return_hideout]
#     }
#     """,
#     Output("zhTable", "data"),
#     Output("zhTable", "columns"),
#     Output("zhLayer", "hideout"),
#     Input("zhLayer", "click_feature"),
#     Input("siteLayer", "hideout"),
#     Input("zhTable", "data"),
# )

# @app.callback(
#     Output("pie-chart", "figure"),
#     Input("zhLayer", "hideout"))
# def generate_chart(hideout):
#     id_zh = hideout['selected_zone']
#     fig = px.pie(df[df["id_zh"] == id_zh], values='proportion', names='code')
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True)
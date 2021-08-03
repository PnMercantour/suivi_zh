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
    console.log(feature)
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
    options=dict( 
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
    html.Div("Lorem ipsum", id="detail_parc", style={'display':'none'}), html.Div(id="detail_vallee", style={'display':'none'}),
    html.Div(id="detail_site",children=[
        dl.Map(id="site_unique", children=[baseLayer, zhLayer], center=[44.3, 7]),
        zhTable,
        dcc.Graph(id="pie-chart", figure=px.pie(df[df["id_zh"] == 374],
              values='proportion', names='code'), style={"backgroundColor": "yellow"})
    ], style={'visibility':'hidden'}),
])

app.clientside_callback(
    """function(dropdown_value, valleeDropdown_value, site_feature, vallee_feature, click_lat_lng) {
        const triggers = dash_clientside.callback_context.triggered
        let return_hideout = {selected_site: null, selected_vallee: null}
        // this manages siteLayer hideout
        // first two statements updates "site" and "vallee". Both siteLayer and siteDropdown can fit conditions
        if(triggers.some((o) => o.prop_id === "siteLayer.click_feature" )){
            return_hideout = {selected_site: site_feature.properties.id, selected_vallee: site_feature.properties.id_vallee, nom_site: site_feature.properties.nom_site}
        } else
        if(triggers.some((o) => o.prop_id === "siteDropdown.value")) {
            return_hideout = {selected_site: dropdown_value, selected_vallee: dropdown_value ? cachedData.siteTable.filter((elem) => elem.properties.id === dropdown_value)[0].properties.id_vallee : valleeDropdown_value}
        }
        // following statement updates "vallee" reset "site" => both valleeLayer and valleeDropdown could update selected_vallee
        else 
        if(triggers.some((o) => o.prop_id === "valleeLayer.click_feature" ||  o.prop_id === "valleeDropdown.value")) {
            return_hideout = {selected_site: null, selected_vallee: vallee_feature ?  vallee_feature.properties.id : valleeDropdown_value }
        }
        // not clicking on any features reset both "vallee" and "site"  
        else if (triggers.some((o) => o.prop_id === "parc.click_lat_lng")) {
            return_hideout = {selected_site: null, selected_vallee: null}
        }

        // set dropdowns values 
        const return_valleeDropdown_value = return_hideout.selected_vallee 
        const return_siteDropdown_value = return_hideout.selected_site 
        
        return [return_hideout, 
        undefined, //reset siteLayer.click_feature
        undefined, //reset valleeLayer.click_feature
        return_valleeDropdown_value, return_siteDropdown_value]
    }""",
    Output("siteLayer", "hideout"),
    Output("siteLayer", "click_feature"),
    Output("valleeLayer", "click_feature"),
    Output("valleeDropdown", "value"),
    Output("siteDropdown", "value"),
    Input("siteDropdown", "value"),
    Input("valleeDropdown", "value"),
    Input("siteLayer", "click_feature"),
    Input("valleeLayer", "click_feature"),
    Input("parc", "click_lat_lng"), 
)

@ app.callback(Output("siteDropdown", "options"), Input("valleeDropdown", "value"))
def dropdownsOptions(valleeValue):
    if valleeValue != 0 and valleeValue != None:
        siteOptions = [{'label': index['nom_site'], 'value': index['id']} for index in filter(lambda item : item['id_vallee']==valleeValue, site__feature_properties)]
    else:
        siteOptions = [{'label': property['nom_site'], 'value': property['id']} for property in site__feature_properties]
    return siteOptions
    
@app.callback([Output("detail_parc", "style"), Output("detail_vallee", "style"), Output("detail_site", "style")], Input("siteLayer", "hideout"), State("detail_parc", "style"), State("detail_vallee", "style"), State("detail_site", "style"))
def detail(hideout, detail_parcStyle, detail_valleeStyle, detail_siteStyle):
    detail_parcStyle.update({'display':'none'})
    detail_valleeStyle.update({'display':'none'})
    detail_siteStyle.update({'visibility':'hidden'})
    if all(propertie==None for propertie in hideout.values()) :
        detail_parcStyle.update({'display':'inline'})
    elif hideout['selected_vallee'] is not None and hideout['selected_site'] is None:
        detail_valleeStyle.update({'display':'inline'})
    else  :
        detail_siteStyle.update({'visibility':'visible'})
    return detail_parcStyle, detail_valleeStyle, detail_siteStyle

app.clientside_callback(
        """function(zhfeature, hideout){
            const triggers = dash_clientside.callback_context.triggered
            let return_hideout 
            if(triggers.some((o) => o.prop_id === "zhLayer.click_feature")){
                return_hideout = {...hideout, selected_zone: zhfeature.properties.id}
            } else {
                return_hideout = {...hideout, selected_zone: null}
            }
            const zhTable_columns = [{"name": [hideout.nom_site, "surface"], "id": "surface"}, {"name": [hideout.nom_site, "état"], "id": "etat"}]
            return [zhTable_columns, return_hideout]
        }""",
        Output("zhTable", "columns"),
        Output("zhLayer", "hideout"),
        Input("zhLayer", "click_feature"),
        Input("siteLayer", "hideout"),
)

@app.callback([Output("zhLayer", "url"), Output("zhTable", "data")], Input("siteLayer", "hideout"))
def zhLayer_url(hideout):
    if hideout['selected_site']:
        data = map(lambda x : {'surface': x['surface'], 'etat': x['etat_zh']}, featurePropertiesFromJson("sites/"+str(hideout['selected_site'])))
        url = "/assets/sites/"+str(hideout['selected_site'])+".json"
        return url, list(data)
    else:
        raise PreventUpdate
        
@app.callback(
    Output("pie-chart", "figure"),
    Input("zhLayer", "hideout"))
def generate_chart(hideout):
    if hideout:
        id_zh = hideout['selected_zone']
        fig = px.pie(df[df["id_zh"] == id_zh], values='proportion', names='code')
        return fig

if __name__ == '__main__':
    app.run_server(debug=True)
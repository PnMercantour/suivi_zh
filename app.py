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
from dash_table import DataTable
from pathlib import Path
import pandas
from dotenv import load_dotenv
import json
import functools
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
load_dotenv('.env/.env')

#=====CREATION DE L'APP=====#
app = dash.Dash(__name__)

#=====PARTIE DONNEES JSON ET CSV POUR L'APP=====#
def featurePropertiesFromJson(kind):
    with open(Path(Path(__file__).parent, 'assets', f'{kind}.json'), 'r') as file:
        json_data = json.load(file)
        return [feature['properties'] for feature in json_data['features']]

# keep all site options in memory
site_feature_properties = featurePropertiesFromJson('sites')
# Pie Chart csv
df = pandas.read_csv(
    Path(Path(__file__).parent, 'assets', 'habitat.csv'))
# Notice csv
df_notice = pandas.read_csv(
    Path(Path(__file__).parent, 'assets', 'notice.csv'))

#=====CREATION DES FONCTION POUR LES LAYERS=====#
# création d'un dictionaire pour les couleurs des polygones
js_style = assign("""
function(feature, context) {
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_zone) {return {color:"#000000"}}
    else {
        let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500"};
        return {color: t[feature.properties.etat_zh]}}
}""")
# Give a color to each feature on siteLayer
site_point_to_layer = assign("""function(feature, latlng, context){
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
# Give a color to each feature on zhLayer
couleur_zh = assign("""
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

#=====CREATION DES LAYERS POUR L'APP=====#
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
# GeoJSON pour les vallées
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
# GeoJSON pour les sites
site_layer = dl.GeoJSON(id="siteLayer", url=app.get_asset_url('sites.json'), hideout={'selected_site': None, 'selected_vallee': None}, options=dict(pointToLayer=site_point_to_layer, onEachFeature=assign("""
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
# GeoJSON pour les zones humides
zh_layer = dl.GeoJSON(id='zhLayer', hideout={'selected_zone': None, 'selected_site': None, 'nom_site': None},
    options=dict( 
    onEachFeature=couleur_zh, style=js_style), 
    zoomToBounds=True)

#=====CREATION DES DATATABLES POUR L'APP=====#
# siteTable = dash_table.DataTable(
#         id='siteTable',
#         columns=[{"name": "nom_site", "id": "nom_site"}],
#         data=[{'nom_site':index}['nom_site'] for index in site_feature_properties],
#         sort_action='native',
#         filter_action='native',
#         style_data_conditional=[
#             {'if': {'row_index': 'odd'},
#             'backgroundColor': 'rgb(248, 248, 248)'
#             }
#         ]
# )

zhTable = dash_table.DataTable(
            id='zhTable',
            columns=[],
            data=[],
            style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ], page_size=10,  merge_duplicate_headers=True,
)

#=====CREATION DES DIVS POUR LA PARTIE BASSE=====#
detail_parc = html.Div("Lorem ipsum", id="detailParc", hidden=True, key="detailParc")
detail_vallee = html.Div(id="detailVallee", hidden=True, key="detailVallee")
detail_site = html.Div(id="detailSite",children=[
        html.Div(id='detailSiteAnalyseFeatures', children=[dl.Map(id="site_unique", children=[baseLayer, zh_layer], center=[44.3, 7]),
        zhTable,
        dcc.Graph(id="pie-chart", figure=px.pie(df[df["id_zh"] == 374],
              values='proportion', names='code'))], key='detailSiteAnalyseFeatures'),
        DataTable(
            id='noticeTable',
            columns=[
                dict(name='Notices', id='link',
                     type='text', presentation='markdown'),
            ],
            data=None
        )
        
    ],key="detailSite")
#=====CREATION DU LAYOUT=====#
app.layout = html.Div([
    html.Div(id="dropdownDiv", children=[
        dcc.Dropdown(id="valleeDropdown", options = [{'label': property['nom'], 'value': property['id']} for property in featurePropertiesFromJson('vallees')], placeholder = "Sélection d'une vallée"), 
        dcc.Dropdown(id="siteDropdown", placeholder = "Sélection d'un site")
    ], key="dropdownDiv"),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, valleeLayer, site_layer],
        center=[44.3, 7], zoom=9), key="partieHaute"),
    html.Div(id="partieBasse", children=[detail_parc , detail_vallee,html.Div(id="controleStyleDetailSite",children=[detail_site])], key='partieBasse')
    
], key='div')
#=====LES CALLBACKS=====#

#=====LES CALLBACKS PARTIE HAUTE=====#
@app.callback(Output("siteDropdown", "options"), Input("valleeDropdown", "value"))
def dropdownsOptions(valleeValue):
    if valleeValue != None:
        siteOptions = [{'label': index['nom_site'], 'value': index['id']} for index in filter(lambda item : item['id_vallee']==valleeValue, site_feature_properties)]
    else:
        siteOptions = [{'label': property['nom_site'], 'value': property['id']} for property in site_feature_properties]
    return siteOptions

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
            return_hideout = {selected_site: dropdown_value, selected_vallee: dropdown_value ?cachedData.siteTable[dropdown_value].properties.id_vallee : valleeDropdown_value}
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

#=====CALLBACK DE GESTION DES PARTIES DETAILS=====#
@app.callback([Output("detailParc", "hidden"), Output("detailVallee", "hidden"), Output("controleStyleDetailSite", "hidden")], Input("siteLayer", "hideout"))
def detail_features(hideout):
    if all(property==None for property in hideout.values()) :
        return [False, True, True]
    elif hideout['selected_vallee'] is not None and hideout['selected_site'] is None:
        return [True, False, True]
    else :
        return [True, True, False]

#=====LES CALLBACKS DE detailSite=====#
@app.callback([Output("zhLayer", "url"), Output("zhTable", "data")], Input("siteLayer", "hideout"))
def zhLayer_url(hideout):
    if hideout['selected_site']:
        data = map(lambda x : {'surface': x['surface'], 'etat': x['etat_zh'], 'id': x['id'], 'key':x['id']}, featurePropertiesFromJson("sites/"+str(hideout['selected_site'])))
        url = "/assets/sites/"+str(hideout['selected_site'])+".json"
        return url, list(data)
    else:
        raise PreventUpdate

@app.callback(
    Output("pie-chart", "figure"),
    Input("zhLayer", "hideout"),
    Input("zhTable", "data"))
def generate_chart(hideout, data):
    if hideout['selected_site'] is not None and hideout['selected_zone'] is None:
        surface_site=functools.reduce(lambda a,b: a+b, [i['surface'] for i in data])
        csv_habitat = list(zip(df['code'], df['proportion'], df['id_zh']))
        surface_zh = {x['id']:x['surface']for x in data}
        df_par_site = [{'proportion':((zone[1]*surface_zh[zone[2]])/surface_site), 'code':zone[0]} for zone in csv_habitat if any(line['id']==zone[2] for line in data)]
        return px.pie(df_par_site if df_par_site else [{'proportion':100, 'code':'Pas de données'}], values='proportion', names='code')
    elif hideout['selected_zone']:
        id_zh = hideout['selected_zone']
        fig = px.pie(df[df["id_zh"] == id_zh], values='proportion', names='code')
        return fig
    else:
        raise PreventUpdate

@app.callback(
    Output("noticeTable", "data"),
    Input("siteLayer", "hideout"))
def updateNoticeTable(hideout):
    if hideout['selected_site']:
        id = hideout['selected_site']
        data = df_notice[df_notice["id_site"] == id].to_dict('records')
        for item in data:
            item['link'] = f"""[{item['nom']}]({app.get_asset_url('pdf/' + item['nom']).replace(' ', '%20')})"""
        return data
    else:
        return None

app.clientside_callback(
        """function(zhfeature, hideout, data_zhTable, cells, click_lat_lng){
            const triggers = dash_clientside.callback_context.triggered
            let return_hideout = {...hideout, selected_zone: null}
            let return_selected_cells = []
            if(triggers.some((o) => o.prop_id === "zhLayer.click_feature")){
                return_hideout = {...hideout, selected_zone: zhfeature.properties.id}
                return_selected_cells = [{row: data_zhTable.indexOf(zhfeature.properties.id) , column: 0}, {row: data_zhTable.indexOf(zhfeature.properties.id) , column: 1}]
            } else 
            if(triggers.some((o) => o.prop_id === "zhTable.selected_cells")){
                return_hideout = {...hideout, selected_zone: cells[0].row_id}
                return_selected_cells = [{row: data_zhTable.indexOf(cells[0].row_id) , column: 0}, {row: data_zhTable.indexOf(cells[0].row_id) , column: 1}]
            }
            else 
            if(triggers.some((o) => o.prop_id === "zhLayer.click_lat_lng")){
                return_selected_cells = []
                return_hideout = {...hideout, selected_zone: null} 
            }
            const zhTable_columns = [{"name": [hideout.nom_site, "surface"], "id": "surface"}, {"name": [hideout.nom_site, "état"], "id": "etat"}]
            return [zhTable_columns, return_hideout, return_selected_cells, undefined]
        }""",
        Output("zhTable", "columns"),
        Output("zhLayer", "hideout"),
        Output("zhTable", "selected_cells"),
        Output("zhTable", "active_cell"),
        Input("zhLayer", "click_feature"),
        Input("siteLayer", "hideout"),
        Input('zhTable', 'derived_viewport_row_ids'),
        Input("zhTable", "selected_cells"),
        Input("site_unique", "click_lat_lng"),

)

if __name__ == '__main__':
    app.run_server(debug=True)

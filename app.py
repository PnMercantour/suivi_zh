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

#assign(""" () => {let test = {}} """)
#création d'un dictionaire pour les couleurs des polygones
js_style = assign("""
function(feature, context) {
    if (context.props.hideout && feature.properties.id == context.props.hideout.selected_site) {return {color:"#000000"}}
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

# Chargement de sites.json utilisation pour les données du tableaux des sites
with open(Path(Path(__file__).parent, 'assets', 'sites.json'), 'r') as fichier:
    sites_json = json.loads(fichier.read())
    fichier.close()

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

siteTable = dash_table.DataTable(
        id='siteTable',
        columns=[{"name": "nom_site", "id": "nom_site"}],
        data=[{'nom_site':index['properties']}['nom_site'] for index in sites_json['features']],
        sort_action='native',
        filter_action='native',
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
)

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
    html.Div([
        dcc.Dropdown(id="vallee_dropdown"),
        siteTable
    ],style={'float':'left', 'paddingRight': '5vh'}),
    html.Div(
        dl.Map(id="parc", children = [baseLayer, valleeLayer, siteLayer],
        center=[44.3, 7], zoom=9),style={'display':'flex', 'paddingBottom':'5vh'}),
    html.Div(id="div_zh",children=[
        dl.Map(id="site_unique", children=[baseLayer, zhLayer]),
        zhTable,
        dcc.Graph(id="pie-chart", figure=px.pie(df[df["id_zh"] == 374],
              values='proportion', names='code'), style={"backgroundColor": "yellow"})
    ], style={'display':'flex', 'flexWrap': 'wrap', 'maxHeight': '50vh'})
])

app.clientside_callback(
    """function(site_feature, cell, dropdown_value, hideout, data) {
        let dropdown_options = []
        cachedData.valleeTable.forEach((elem) => dropdown_options.push({label: elem.properties.nom, value: elem.properties.id}))
        const triggers = dash_clientside.callback_context.triggered
        let return_hideout = {selected_site: null, selected_vallee: null}
        let return_click_feature = site_feature
        let return_active_cell = {'row': -1, 'column': 0}
        let return_selected_cells = []
        const objet_data = cachedData.siteTable.map((feature, id) => ({nom_site: feature.properties.nom_site, id_vallee: feature.properties.id_vallee, id}))
        let return_siteTable_data = dropdown_value ? objet_data.filter((elem) => (elem.id_vallee === dropdown_value)) : objet_data
        let return_zhLayer_url = "assets/sites/"
        let return_zhLayer_hideout = {selected_site: null, nom_site: null}
        if(triggers.some((o) => o.prop_id === "siteLayer.click_feature")){
            return_hideout = {selected_site: site_feature.properties.id, selected_vallee: site_feature.properties.id_vallee}
            data.forEach(elem => {if(elem === site_feature.properties.id) return_active_cell = {'row': data.indexOf(elem), 'column': 0}})
            return_zhLayer_url += site_feature.properties.id+".json"
            return_zhLayer_hideout = {selected_site: site_feature.properties.id, nom_site: site_feature.properties.nom_site}
        }
        if(triggers.some((o) => o.prop_id === "siteTable.active_cell")){
            cachedData.siteTable.forEach((site) => {
                if(site.properties.id === cell.row_id){
                    return_hideout = {selected_site: cell.row_id, selected_vallee: site.properties.id_vallee }
                    return_active_cell = cell
                }
            })
            return_zhLayer_url += cell.row_id+".json"
            return_zhLayer_hideout = {selected_site: cell.row_id, nom_site: cachedData.siteTable.filter((site) => site.properties.id === cell.row_id)[0].properties.nom_site}
        }
    
        return [return_hideout, site_feature, return_active_cell, return_selected_cells, return_siteTable_data, return_zhLayer_url, return_zhLayer_hideout, dropdown_options]
    }""",
    Output("siteLayer", "hideout"),
    Output("siteLayer", "click_feature"),
    Output("siteTable", "active_cell"),
    Output("siteTable", "selected_cells"),
    Output("siteTable", "data"),
    Output("zhLayer", "url"),
    Output("zhLayer", "hideout"),
    Output("vallee_dropdown", "options"),
    Input("siteLayer", "click_feature"),
    Input("siteTable", "active_cell"),
    Input("vallee_dropdown", "value"),
    State("siteLayer", "hideout"),
    State("siteTable", "derived_viewport_row_ids")
)

app.clientside_callback(
    """
    function(hideout){
        console.log(cachedData.zhTable)
        const zhTable_data = cachedData.zhTable.map((feature, id) => ({surface: feature.surface, etat: feature.etat, id}))
        const zhTable_columns = [{"name": [hideout.nom_site, "surface"], "id": "surface"}, {"name": [hideout.nom_site, "état"], "id": "etat"}]
        cachedData.zhTable = []
        console.log(cachedData.zhTable)
        return [zhTable_data, zhTable_columns]
    }
    """,
    Output("zhTable", "data"),
    Output("zhTable", "columns"),
    Input("zhLayer", "hideout"),
)

# app.clientside_callback(
#     """function(feature, hideout) {
#     if (feature == undefined) 
#         return dash_clientside.no_update
#     else
#         return {...hideout, selected_site: feature.properties.id}
#     }""",
#     Output("zhLayer", "hideout"),
#     Input("zhLayer", "click_feature"),
#     State("siteLayer", "hideout")
#    )

# app.clientside_callback(
#     """function(site, hideout) {
#         i = site.selected_site
#         const nom = cachedData.siteTable[i].properties.nom_site
#         let table = cachedData.zhTable.map((feature, id) => ({surface: feature.surface, etat: feature.etat, id}))
#         cachedData.zhTable = []
#         return [table, [{"name": [nom, "surface"], "id": "surface"}, {"name": [nom, "état"], "id": "etat"}]];
#     }""",
#     Output("zhTable", "data"),
#     Output("zhTable", "columns"),
#     Input("siteLayer", "hideout"),
#     Input("zhLayer", "hideout"))

# @app.callback(
#     Output("pie-chart", "figure"),
#     Input("zhLayer", "hideout"))
# def generate_chart(hideout):
#     id_zh = hideout['selected_zone']
#     fig = px.pie(df[df["id_zh"] == id_zh], values='proportion', names='code')
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True)
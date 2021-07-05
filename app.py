import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd
from dash_extensions.javascript import arrow_function, assign
import json
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Lecture des csv
points = pd.read_csv("data/sites.csv", ';')
zh = pd.read_csv("data/zh.csv", ';')
#création d'un dictionaire pour les couleurs des polygones
color = {'bon': 'green', 'moyen': 'yellow', 'mauvais': 'red'}
dd_options = [dict(value=p, label=p) for p in points["nom_site"]]
dd_defaults = [o["value"] for o in dd_options]
geojson_filtre = assign("function(feature, context){{return context.props.hideout.includes(feature.properties.nom_site);}}")
# GeoJSON pour les points
listes_sites = dl.GeoJSON(id="listes_sites", url=app.get_asset_url('sites.json'), options=dict(filter=geojson_filtre), hideout=dd_defaults)
# GeoJSON pour les zones humides
zones_humides = dl.GeoJSON(id="zones_humides", data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zh.loc[i]['geojson']), "properties":{"site": zh.loc[i]['nom_site']}}for i in range(len(zh))]}) #, hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))

# Création de la dataframe, un tableau passé en paramètre de dl.Map dans le layout
# Le fond de carte
baseLayer = dl.TileLayer()

# dl.WMSTileLayer(url="http://ows.mundialis.de/services/service?",
#                    layers="TOPO-OSM-WMS", format="image/png")
# Le layout
app.layout = html.Div([
    html.Div([dl.Map(id="parc", children = [baseLayer, listes_sites, zones_humides],
        center=[44.3, 7], zoom=9,
        style={'width': '100%', 'height': '50vh', 'margin': "auto"}),
    dl.Map(id="site_unique", style={'width': '30%', 'height': '50vh', 'margin': "auto"},zoom=15)], style={'display':'flex'}),
    html.Div([dash_table.DataTable(
    id='tableau_des_sites',
    columns=[{"name": "nom site", "id": "nom_site"}],
    data=points.to_dict('records'),
    sort_action='native',
    filter_action='native',
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
)], id="test"), html.Div(id="test2")
])

@app.callback([Output('site_unique', 'children'), Output('site_unique', 'center')], [Input('listes_sites', 'click_feature'), Input('tableau_des_sites', 'data'), Input('tableau_des_sites', 'selected_cells')])
def maj_carte_site_unique(feature, data, cell):
    if dash.callback_context.triggered[0]['prop_id'] == '.':
        raise PreventUpdate
    if dash.callback_context.triggered[0]['prop_id'] == 'listes_sites.click_feature':
        site = feature['properties']
        idSite = str(site['id'])
        centre = json.loads(points[points['nom_site']==site['nom_site']]['centroid'].all())['coordinates'][::-1]
        return [baseLayer, dl.GeoJSON(url=app.get_asset_url('sites/'+idSite+'.json'))], centre  #, {'row': int(1), 'column': 0} #, "{nom_site} contains"+feature['properties']['site']
    if dash.callback_context.triggered[0]['prop_id'] == 'tableau_des_sites.selected_cells':
        toutes_zones = zh[zh['nom_site']==data[cell[0]['row']]['nom_site']]['geojson']
        centre = json.loads(points[points['nom_site']==data[cell[0]['row']]['nom_site']]['centroid'].all())['coordinates'][::-1]
        return [baseLayer, dl.GeoJSON(data={"type": "FeatureCollection", "features": [{"type": "Feature", "geometry":json.loads(zone)}for zone in toutes_zones]})], centre #, None #, None

@app.callback([Output('tableau_des_sites', 'data'), Output('tableau_des_sites', 'columns')], [Input("tableau_des_sites", "selected_cells"), Input("tableau_des_sites", "data"), Input("listes_sites", "click_feature"), Input('tableau_des_sites', 'filter_query')])
def maj_tableau_des_sites(cell, data, feature, filter):
    columns = [{'name':'nom_site', 'id':'nom_site'}, {'name': 'surface', 'id': 'surface'}, {'name':'etat', 'id': 'etat'}]
    if dash.callback_context.triggered[0]['prop_id'] == '.':
        raise PreventUpdate
    if dash.callback_context.triggered[0]['prop_id'] == 'listes_sites.click_feature':
        return zh[zh['nom_site']==feature['properties']['nom_site']].to_dict('records'), columns
    if dash.callback_context.triggered[0]['prop_id'] == 'tableau_des_sites.selected_cells':
        return zh[zh['nom_site']==data[cell[0]['row']]['nom_site']].to_dict('records'), columns
    if dash.callback_context.triggered[0]['prop_id'] == 'tableau_des_sites.filter_query':
        return points.to_dict('records'), [{"name": "nom site", "id": "nom_site"}]
    

if __name__ == '__main__':
    app.run_server(debug=True)


import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign

import pandas as pd
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dl.Map(children=[dl.TileLayer(),
                     dl.GeoJSON(id="sites", url=app.get_asset_url('sites.json'), options=dict(onEachFeature=assign("""
(feature, layer) => {
    //console.log("feature =",feature);
    if(!feature.properties){
        return
    }
    if(feature.properties.nom_site){
        layer.bindTooltip(feature.properties.nom_site)
    }
}
""")))],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="site_selectionne"), html.Div(id="site_survole")])


@app.callback(Output("site_selectionne", "children"), [Input("sites", "click_feature")])
def site_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['nom_site']}"


@app.callback(Output("site_survole", "children"), [Input("sites", "hover_feature")])
def site_hover(feature):
    if feature is not None:
        return f"You hovered above {feature['properties']['nom_site']}"


if __name__ == '__main__':
    app.run_server(debug=True)

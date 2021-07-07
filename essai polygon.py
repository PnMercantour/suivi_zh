from logging import log
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign, arrow_function

import pandas as pd
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
js_style = assign("""
function(feature) {
    let t = {bon: "#1E90FF", moyen: "#FF7F50", mauvais: "#FF4500"};
    console.log(feature);
    return {color: t[feature.properties.etat_zh]}
}""")

fonction = """
(feature, layer) => {
    //console.log("feature =",feature);
    if(!feature.properties){
        return
    }
    if(feature.properties.etat_zh){
        layer.bindTooltip(feature.properties.etat_zh)
    }
}
"""

hoverStyle = arrow_function(dict(weight=5, fillOpacity=1))
app.layout = html.Div([
    dl.Map(children=[dl.TileLayer(),
                     dl.GeoJSON(id="site-4", hoverStyle=hoverStyle,
                                url=app.get_asset_url('sites/4.json'),
                                options=dict(onEachFeature=assign(fonction), style=js_style
                                             ))],
           center=[44.3, 7], zoom=9,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="zh_selectionnee"), html.Div(id="zh_survolee")])


@ app.callback(Output("zh_selectionnee", "children"), [Input("site-4", "click_feature")])
def site_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['id']}"


@ app.callback(Output("zh_survolee", "children"), [Input("site-4", "hover_feature")])
def site_hover(feature):
    if feature is not None:
        return f"You hovered above {feature['properties']['id']}"


if __name__ == '__main__':
    app.run_server(debug=True)

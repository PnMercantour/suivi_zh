import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
from pathlib import Path
import json
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
def featurePropertiesFromJson(kind):
    with open(Path(Path(__file__).parent, 'assets', f'{kind}.json'), 'r') as file:
        json_data = json.load(file)
        return [feature['properties'] for feature in json_data['features']]

# keep all site options in memory
site_feature_properties = featurePropertiesFromJson('sites')
c=[dbc.DropdownMenuItem(property['nom'], id=property['nom'], key=property['nom']) for property in featurePropertiesFromJson('vallees')]
c2=[dbc.DropdownMenuItem(property['nom_site'], id=property['nom_site'], key=property['nom_site']) for property in site_feature_properties]
app.layout = html.Div(
        children=[
            dbc.DropdownMenu(label="Sélection d'une vallée", className='mb-3', id="valleeDropdown", children = c), 
            dbc.DropdownMenu(id="siteDropdown", label = "Sélection d'un site", children=c2),
        html.Div(id="test")]
)
@app.callback([Output('valleeDropdown', 'label'), Output('siteDropdown', 'children')], [Input(i.id, "n_clicks") for i in c])
def test(*args):
    triggers = dash.callback_context.triggered
    if any(trigger['prop_id'].split('.')[0]==vallee['nom'] for vallee in featurePropertiesFromJson('vallees')
                                                            for trigger in triggers):
        print(triggers)
        return triggers[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate

if __name__ == "__main__":
    app.run_server(debug=True)
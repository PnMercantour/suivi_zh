import os
from pathlib import Path
import json

from dotenv import load_dotenv
from dash import Dash
import dash_bootstrap_components as dbc
from dash_extensions.javascript import Namespace

app_dir = Path(__file__).parent
app_name = app_dir.name

# .env file is read from project root directory
load_dotenv(app_dir.parent/'.env')


# Assume project root is one level up
# data is shared by all apps, assets is app specific
# root/
#   data/
#   app1/
#       assets/
#   app2/
#       assets/
project_root = app_dir.parent
data_path = project_root / 'data'
assets_path = app_dir / 'assets'

IGN_KEY = os.getenv('IGN_KEY')

app = Dash(__name__, title='Zones humides', external_stylesheets=[
           dbc.themes.SLATE, dbc.icons.FONT_AWESOME])

ns = Namespace('PNM', 'zh')


def featurePropertiesFromJson(kind):
    with (assets_path / f'{kind}.json').open('r') as file:
        json_data = json.load(file)
        return [feature['properties'] for feature in json_data['features']]


sites = featurePropertiesFromJson('sites')
vallees = featurePropertiesFromJson('vallees')


def get_properties(id, list):
    if id is None:
        return None
    for item in list:
        if item['id'] == int(id):
            return item
    return None


def get_site_properties(site_id):
    return get_properties(site_id, sites)


def get_site_name(site_id):
    return get_properties(site_id, sites)['nom_site']


def get_vallee_properties(vallee_id):
    return get_properties(vallee_id, vallees)


def get_vallee_name(vallee_id):
    return get_properties(vallee_id, vallees)['nom']


def list_sites(vallee_id):
    return [site['id'] for site in sites if site['id_vallee'] == int(vallee_id)]


print('Running', app_name)
print('data:', data_path)
print('assets', assets_path)

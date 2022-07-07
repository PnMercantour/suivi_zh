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
if IGN_KEY is None:
    print("""
---------------------------------------------
IGN_KEY non trouvée.
Valorisez la variable d'environnement IGN_KEY avec une clé valide pour accéder à la cartographie raster de l'IGN.
---------------------------------------------
""")

app = Dash(__name__, title='Zones humides', external_stylesheets=[
           dbc.themes.SLATE, dbc.icons.FONT_AWESOME])

ns = Namespace('PNM', 'zh')

print('Running', app_name)
print('data:', data_path)
print('assets', assets_path)

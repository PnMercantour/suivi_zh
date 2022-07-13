import csv
from urllib.parse import quote
from dash import html, Output
import dash_bootstrap_components as dbc

from config import data_path, app
from data import get_site_name, get_notices


def get_url(notice):
    return app.get_asset_url('pdf/' + quote(notice['nom']))


notice_table = html.Tbody()

component = dbc.Table([
    html.Thead(html.Tr([
        html.Th("Site"),
        html.Th("Edition"),
        html.Th('Notice'),
    ])),
    notice_table,
])

output = Output(notice_table, 'children')

notice_table_style = {'verticalAlign': 'middle'}


def update(state):
    id_site = state['site']
    id_vallee = state['vallee']
    return [html.Tr([
        html.Td(get_site_name(notice['id_site']), style=notice_table_style),
        html.Td(notice['date'], style=notice_table_style),
        html.Td(dbc.Button(html.I(className="fas fa-solid fa-download"), external_link=True,
                href=get_url(notice), target='_blank', title=notice['nom']), style=notice_table_style),
    ]) for notice in get_notices(id_site, id_vallee)]

import csv
from urllib.parse import quote
from dash import html, Output
import dash_bootstrap_components as dbc

from config import data_path, app, list_sites, get_site_name

with (data_path / 'notice.csv').open('r') as csvfile:
    reader = csv.DictReader(csvfile)
    notices = [row for row in reader]


def filter(id_site=None, id_vallee=None):
    if id_site is None and id_vallee is None:
        return notices
    if id_site is not None:
        site_list = [str(id_site)]
    elif id_vallee is not None:
        site_list = [str(id_site) for id_site in list_sites(id_vallee)]
    return [notice for notice in notices if notice['id_site'] in site_list]


def get_url(notice):
    return app.get_asset_url('pdf/' + quote(notice['nom']))


notice_table = html.Tbody(),

component = dbc.Table([
    html.Thead(html.Tr([
        html.Th("Site"),
        html.Th("Date"),
        html.Th('Notice'),
    ])),
    notice_table,
])


def update_component(context):
    id_site = context.get('site')
    id_vallee = context.get('vallee')
    return [html.Tr([
        html.Td(get_site_name(notice['id_site'])),
        html.Td(notice['date']),
        html.Td(dbc.Button(html.I(className="fas fa-solid fa-download"), external_link=True,
                href=get_url(notice), target='_blank', title=notice['nom'])),
    ]) for notice in filter(id_site, id_vallee)]


output = Output(notice_table, 'children')

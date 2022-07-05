import json
import csv
import pandas as pd
import numpy as np
# from pandas import DataFrame
from config import data_path, assets_path


def to_dict(l, key='id'):
    "builds a dict from an iterable <l>, indexing on <key>"
    return {i[key]: i for i in l}


def to_bounds(b):
    "converts a standard bbox into leaflet bounds object"
    return [[b[1], b[0]], [b[3], b[2]]]


with (assets_path/'vallee.json').open('r') as f:
    vallee_data = to_dict([
        dict(s['properties'], bounds=to_bounds(s['bbox'])) for s in json.load(f)['features']
    ], 'id_vallee')


with (assets_path/'site.json').open('r') as f:
    site_data = to_dict([
        dict(s['properties'], bounds=to_bounds(s['bbox'])) for s in json.load(f)['features']
    ], 'id_site')


with (assets_path/'zh.json').open('r') as f:
    zh_data = to_dict([zh['properties']
                      for zh in json.load(f)['features']])


with (assets_path/'habitat.json').open('r') as f:
    habitat_data = to_dict(habitat['properties']
                           for habitat in json.load(f)['features'])

with (assets_path/'ref_habitat.json').open('r') as f:
    ref_habitat = to_dict(ref['properties']
                          for ref in json.load(f)['features'])

with (assets_path/'notice.json').open('r') as f:
    notice_data = to_dict([notice['properties']
                           for notice in json.load(f)['features']])

# zh_df = pd.read_csv(data_path / 'zh.csv', sep=';')
# zh_df.drop(columns=['geojson'], inplace=True)
# zh_df.columns = ['id_zh', 'nom_site', 'surface', 'etat']

# sites_df = DataFrame.from_records([{
#     'id_site': site['id_site'],
#     'nom_site': site['nom_site'],
#     'id_vallee':site['id_vallee'],
# } for site in site_data.values()])


# vallees_df = DataFrame.from_records([{
#     'id_vallee': vallee['id_vallee'],
#     'nom_vallee': vallee['nom_vallee'],
# } for vallee in vallee_data.values()])

# detail = pd.merge(pd.merge(zh_df, sites_df, on='nom_site'),
#                   vallees_df, on='id_vallee')

PNM_bounds = [[43.8, 6.5], [44.5, 7.7]]


def get_site_name(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['nom_site']


def get_vallee_id(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['id_vallee']


def list_sites(vallee_id):
    return [site['id_site'] for site in site_data.values() if site['id_vallee'] == int(vallee_id)]


def get_site_id(zh_id):
    return zh_data[zh_id]['id_site']


def get_notices(id_site=None, id_vallee=None):
    notices = notice_data.values()
    if id_site is not None:
        site_list = [int(id_site)]
    elif id_vallee is not None:
        site_list = [int(id_site) for id_site in list_sites(id_vallee)]
    else:
        return notices
    return [notice for notice in notices if notice['id_site'] in site_list]


def bounds(site=None, vallee=None):
    if site is not None:
        return site_data[int(site)]['bounds']
    if vallee is not None:
        return vallee_data[int(vallee)]['bounds']
    return PNM_bounds


site_etat = {}
with (data_path/'site_etat.csv').open('r') as f:
    for row in csv.DictReader(f, delimiter=';'):
        site_etat[int(row['id_site'])] = {'id_site': int(
            row['id_site']), 'ratio': float(row['ratio'])}

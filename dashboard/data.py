import json
import csv
import pandas as pd
import numpy as np
from pandas import DataFrame
from config import data_path, assets_path


def to_dict(l, key):
    "builds a dict from an iterable <l>, indexing on <key>"
    return {i[key]: i for i in l}


def to_bounds(b):
    "converts a standard bbox into leaflet bounds object"
    return [[b[1], b[0]], [b[3], b[2]]]


with (assets_path/'vallees.json').open('r') as f:
    vallee_data = to_dict([
        dict(s['properties'], bounds=to_bounds(s['bbox'])) for s in json.load(f)['features']
    ], 'id_vallee')


with (assets_path/'sites.json').open('r') as f:
    site_data = to_dict([
        dict(s['properties'], bounds=to_bounds(s['bbox'])) for s in json.load(f)['features']
    ], 'id_site')


with (assets_path/'zh.json').open('r') as f:
    zh_data = to_dict([zh['properties']
                      for zh in json.load(f)['features']], 'id_zh')


with (assets_path/'habitat.json').open('r') as f:
    habitat_data = json.load(f)

with (assets_path/'ref_habitat.json').open('r') as f:
    ref_habitat = to_dict(json.load(f), 'habitat')

zh_df = pd.read_csv(data_path / 'zh.csv', sep=';')
zh_df.drop(columns=['geojson'], inplace=True)
zh_df.columns = ['id_zh', 'nom_site', 'surface', 'etat']

sites_df = DataFrame.from_records([{
    'id_site': site['id_site'],
    'nom_site': site['nom_site'],
    'id_vallee':site['id_vallee'],
} for site in site_data.values()])


vallees_df = DataFrame.from_records([{
    'id_vallee': vallee['id_vallee'],
    'nom_vallee': vallee['nom_vallee'],
} for vallee in vallee_data.values()])

detail = pd.merge(pd.merge(zh_df, sites_df, on='nom_site'),
                  vallees_df, on='id_vallee')

PNM_bounds = [[43.8, 6.5], [44.5, 7.7]]


def get_site_name(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['nom_site']


def get_site_vallee(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['id_vallee']


def list_sites(vallee_id):
    return [site['id_site'] for site in site_data.values() if site['id_vallee'] == int(vallee_id)]


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

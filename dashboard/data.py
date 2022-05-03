import json
import csv
import pandas as pd
import numpy as np
from pandas import DataFrame
from config import data_path, assets_path, vallees, sites

zh_df = pd.read_csv(data_path / 'zh.csv', sep=';')
zh_df.drop(columns=['geojson'], inplace=True)
zh_df.columns = ['id_zh', 'nom_site', 'surface', 'etat']

sites_df = DataFrame.from_records([{
    'id_site': site['id'],
    'nom_site': site['nom_site'],
    'id_vallee':site['id_vallee'],
} for site in sites])


vallees_df = DataFrame.from_records([{
    'id_vallee': vallee['id'],
    'nom_vallee': vallee['nom'],
} for vallee in vallees])

detail = pd.merge(pd.merge(zh_df, sites_df, on='nom_site'),
                  vallees_df, on='id_vallee')

PNM_bounds = [[43.8, 6.5], [44.5, 7.7]]

vallee_data = {}
with (assets_path/'vallee_test.json').open('r') as f:
    # Maybe drop geometry
    for vallee in json.load(f)['features']:
        b = vallee['bbox']
        p = vallee['properties']
        vallee_data[p['id_vallee']] = {
            'id_vallee': p['id_vallee'],
            'bounds': [[b[1], b[0]], [b[3], b[2]]],
            'nom_vallee': p['nom_vallee'],
        }

site_data = {}
with (assets_path/'site_test.json').open('r') as f:
    # Maybe drop geometry
    for site in json.load(f)['features']:
        b = site['bbox']
        p = site['properties']
        site_data[p['id_site']] = {
            'id_site': p['id_site'],
            'bounds': [[b[1], b[0]], [b[3], b[2]]],
            'nom_site': p['nom_site'],
            'id_vallee': p['id_vallee']
        }


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

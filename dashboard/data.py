import json

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
    ])


with (assets_path/'site.json').open('r') as f:
    site_data = to_dict([
        dict(s['properties'], bounds=to_bounds(s['bbox'])) for s in json.load(f)['features']
    ])


with (assets_path/'zh.json').open('r') as f:
    zh_data = to_dict([zh['properties']
                      for zh in json.load(f)['features']])


with (assets_path/'habitat.json').open('r') as f:
    habitat_data = to_dict(habitat['properties']
                           for habitat in json.load(f)['features'])

with (assets_path/'ref_habitat.json').open('r') as f:
    ref_habitat = to_dict(ref['properties']
                          for ref in json.load(f)['features'])

with (assets_path/'ref_alteration.json').open('r') as f:
    ref_alteration = to_dict(ref['properties']
                             for ref in json.load(f)['features'])

with (assets_path/'notice.json').open('r') as f:
    notice_data = to_dict([notice['properties']
                           for notice in json.load(f)['features']])

with (assets_path/'rhomeo_site.json').open('r') as f:
    rhomeo_site_data = to_dict([row['properties']
                               for row in json.load(f)['features']], key='code')

with (assets_path/'rhomeo_result.json').open('r') as f:
    rhomeo_result_data = to_dict([row['properties']
                                  for row in json.load(f)['features']])

PNM_bounds = [[43.8, 6.5], [44.5, 7.7]]


def get_site_name(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['nom_site']


def get_vallee_id(site_id):
    if site_id is not None:
        return site_data[int(site_id)]['id_vallee']


def list_sites(vallee_id):
    return [site['id'] for site in site_data.values() if site['id_vallee'] == int(vallee_id)]


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

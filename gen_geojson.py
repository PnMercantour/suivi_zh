#!/usr/bin/env python3
import argparse
from pathlib import Path

import psycopg2


def main(args):
    connection = psycopg2.connect(service='bd_pnm')

    cur = connection.cursor()
    cur.execute("""
WITH features AS (
  SELECT
    nom_site,
    json_build_object('type', 'Feature', 'properties', json_build_object('id', id,
      'surface', surface, 'etat_zh', etat_zh, 'annee_inventaire', annee_inventaire, 'source', source),
      'geometry', st_asgeojson (st_transform (geom, 4326))::json) feature
  FROM
    eau_zh.zh
)
SELECT
  nom_site,
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features
GROUP BY
  nom_site;""")
    for (nom_site, geojson) in cur:
        path = Path(args.dir, nom_site + '.json')
        print(path)
        fp = path.open(mode='x')
        fp.write(geojson)
        fp.close()
    cur.close()
    connection.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=Path, default=Path('./'),
                        help='Destination directory, defaults to current directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='Verbose mode, print activity to stdout')

    args = parser.parse_args()
    args.dir.mkdir(parents=True, exist_ok=True)
    main(args)

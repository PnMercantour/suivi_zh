WITH features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', id, 'id_site', id_site, 'annee',
      annee_inventaire, 'etat', etat_zh, 'surface', surface, 'source', source),
      'geometry', st_asgeojson (st_transform (zh.geom, 4326), 6)::json) feature
  FROM
    eau_zh.zh
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

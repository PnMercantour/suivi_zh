WITH features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties', json_build_object('id', id,
      'nom', nom), 'geometry', st_asgeojson (st_transform (geom, 4326))::json) feature
  FROM
    limregl.cr_pnm_vallees_topo
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

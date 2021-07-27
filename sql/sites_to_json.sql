WITH features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties', json_build_object('id', site.id,
      'nom_site', site.nom_site, 'id_vallee', vallee.id), 'geometry', st_asgeojson (st_transform
      (site.geom, 4326))::json) feature
  FROM
    eau_zh.site
    JOIN limregl.cr_pnm_vallees_topo vallee ON (st_within (site.geom, vallee.geom)))
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

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
  json_build_object('type', 'FeatureCollection', 'features', array_to_json(array_agg(feature))) geojson
FROM
  features
GROUP BY
  nom_site;

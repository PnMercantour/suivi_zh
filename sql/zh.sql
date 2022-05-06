WITH features AS (
  SELECT
    json_build_object(
      'type', 'Feature',
      'properties', json_build_object(
        'id_zh', zh.id,
        'id_site', site.id,
        'annee', annee_inventaire,
        'etat', etat_zh,
        'surface', surface,
        'source', source,
        'geometry', st_asgeojson(st_transform(zh.geom, 4326), 6)::json
      )) feature
  FROM
    eau_zh.zh join eau_zh.site using (nom_site)
)
SELECT
  json_build_object(
    'type', 'FeatureCollection', 
    'features', json_agg(feature)
  )::text geojson
FROM
  features;

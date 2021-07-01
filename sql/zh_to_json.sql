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
  site.id,
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  eau_zh.site
  JOIN features USING (nom_site)
GROUP BY
  nom_site;

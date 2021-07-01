WITH features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties', json_build_object('id', site.id,
      'nom_site', site.nom_site), 'geometry', st_asgeojson (st_transform (st_centroid (st_union
      (geom)), 4326))::json) feature
  FROM
    eau_zh.site
    JOIN eau_zh.zh USING (nom_site)
  GROUP BY
    site.nom_site
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

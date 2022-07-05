WITH habitat AS (
  SELECT
    habitat.id id,
    id_zh,
    id_type,
    proportion
  FROM
    eau_zh.habitat
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties', row_to_json(habitat)) feature
  FROM
    habitat
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

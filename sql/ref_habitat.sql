WITH ref AS (
  SELECT
    id,
    code,
    label,
    description
  FROM
    eau_zh.ref_habitat
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties', row_to_json(ref)) feature
  FROM
    ref
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

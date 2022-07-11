WITH result AS (
  SELECT id,
    location,
    name,
    value,
    year
  FROM eau_zh.zh_rhomeo_additional_results
),
features AS (
  SELECT json_build_object(
      'type',
      'Feature',
      'properties',
      row_to_json (result)
    ) feature
  FROM result
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM features;
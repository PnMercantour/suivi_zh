WITH ref AS (
  SELECT id,
    "type",
    label,
    description
  FROM eau_zh.ref_alterations
),
features AS (
  SELECT json_build_object(
      'type',
      'Feature',
      'properties',
      row_to_json(ref)
    ) feature
  FROM ref
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM features;
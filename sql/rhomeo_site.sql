WITH features AS (
  SELECT "NAME" code,
    json_build_object(
      'type',
      'Feature',
      'properties',
      json_build_object(
        'code',
        "NAME",
        'remarques',
        "REMARKS",
        'departement',
        "COUNTY",
        'referent',
        "REFERENT",
        'org',
        "ORG",
        'type',
        "TYPE"
      )
    ) feature
  FROM eau_zh.zh_rhomeo_sites
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM (
    SELECT feature
    FROM features
    ORDER BY code
  ) f;
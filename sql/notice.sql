WITH features AS (
  SELECT json_build_object(
      'type',
      'Feature',
      'properties',
      json_build_object(
        'id',
        id,
        'nom',
        nom,
        'id_site',
        id_site,
        'description',
        description,
        'auteur',
        auteur,
        'date',
        date,
        'langue',
        langue
      )
    ) feature
  FROM eau_zh.notice
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM features;
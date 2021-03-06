-- construit un objet geojson qui liste les altérations
WITH alteration AS (
  SELECT id,
    id_site,
    id_type,
    st_transform (alteration.geom, 4326) geom,
    box2d (st_transform (alteration.geom, 4326)) envelope
  FROM eau_zh.alteration
),
features AS (
  SELECT json_build_object(
      'type',
      'Feature',
      'properties',
      json_build_object(
        'id',
        alteration.id,
        'id_site',
        id_site,
        'id_type',
        id_type,
        'label',
        ref_alterations.type
      ),
      'geometry',
      st_asgeojson (geom, 6)::json,
      'bbox',
      json_build_array(
        st_xmin (envelope),
        st_ymin (envelope),
        st_xmax (envelope),
        st_ymax (envelope)
      )
    ) feature
  FROM alteration
    left join eau_zh.ref_alterations on(alteration.id_type = ref_alterations.id)
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM features;
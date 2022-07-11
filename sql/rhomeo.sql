-- construit un objet geojson avec les relevés rhomeo
WITH releves AS (
  SELECT geom,
    count(*) releves,
    'CBNA' organisme
  FROM eau_zh."zh_rhomeo_releves_placettes_ZH_PNM_CBNA_2020"
  GROUP BY geom
  UNION
  SELECT geom,
    count(*) releves,
    'CBNMed' organisme
  FROM eau_zh."zh_rhomeo_releves_placettes_ZH_PNM_CBNMED_2020"
  GROUP BY geom
),
features AS (
  SELECT json_build_object(
      'type',
      'Feature',
      'properties',
      json_build_object(
        'organisme',
        organisme,
        'releves',
        releves,
        'code',
        zh_rhomeo_sites."NAME",
        'id_site',
        site.id
      ),
      'geometry',
      st_asgeojson (st_transform (releves.geom, 4326), 6)::json
    ) feature
  FROM releves
    left join eau_zh.zh_rhomeo_sites on (st_within(releves.geom, zh_rhomeo_sites.geom))
    left join eau_zh.site on (st_within (site.geom, zh_rhomeo_sites.geom))
)
SELECT json_build_object(
    'type',
    'FeatureCollection',
    'features',
    json_agg(feature)
  )::text geojson
FROM features;
-- construit un objet geojson avec les relevés rhomeo
WITH releves AS (
  SELECT
    geom,
    count(*) releves,
    'CBNA' organisme
  FROM
    eau_zh."zh_rhomeo_releves_placettes_ZH_PNM_CBNA_2020"
  GROUP BY
    geom,
    organisme
  UNION
  SELECT
    geom,
    count(*) releves,
    'CBNMed' organisme
  FROM
    eau_zh."zh_rhomeo_releves_placettes_ZH_PNM_CBNMED_2020"
  GROUP BY
    geom,
    organisme
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('organisme', organisme, 'releves', releves), 'geometry',
      st_asgeojson (st_transform (releves.geom, 4326), 6)::json) feature
  FROM
    releves
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

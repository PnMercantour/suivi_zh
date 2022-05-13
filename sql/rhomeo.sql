-- construit un objet geojson avec les relevés rhomeo

WITH releves AS (
  SELECT
    geom, count(*) releves, 'CBNA' organisme from eau."zh_rhomeo_releves_placettes_ZH_PNM_CBNA_2020"
    group by geom, organisme
union
    SELECT
    geom, count(*) releves, 'CBNMed' organisme from eau."zh_rhomeo_releves_placettes_ZH_PNM_CBNMED_2020"
    group by geom, organisme
  ),
features as (
  select json_build_object(
    'type', 'Feature', 
    'properties', json_build_object(
        'organisme', organisme,
        'releves', releves
    ),
    'geometry', st_asgeojson
      (st_transform(releves.geom, 4326), 6)::json
) feature from releves)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

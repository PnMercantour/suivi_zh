-- construit un objet geojson qui décrit les vallées
-- properties:
--      id_vallee (entier)
--      nom_vallee (chaîne UTF8)
-- geometry: multipolygone
-- bbox : la boîte englobante.
-- https://datatracker.ietf.org/doc/html/rfc7946

with vallee as (select  id id_vallee, nom nom_vallee, st_transform(geom, 4326) geom, box2d(st_transform(geom, 4326)) envelope from limregl.cr_pnm_vallees_topo),
vallee_xy as (select id_vallee, nom_vallee, geom, st_xmin(envelope), st_xmax(envelope), st_ymin(envelope), st_ymax(envelope) from vallee)
,
 features AS (
  SELECT
    json_build_object(
    'type', 'Feature', 
    'properties', json_build_object('id_vallee', id_vallee, 'nom_vallee', nom_vallee), 
     'geometry', st_asgeojson (geom,6)::json,
     'bbox', json_build_array(st_xmin, st_ymin, st_xmax, st_ymax)
     ) feature
  FROM
    vallee_xy
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;
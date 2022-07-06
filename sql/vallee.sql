-- construit un objet geojson qui décrit les vallées
-- properties:
--      id_vallee (entier)
--      nom_vallee (chaîne UTF8)
-- geometry: multipolygone
-- bbox : la boîte englobante.
-- https://datatracker.ietf.org/doc/html/rfc7946
WITH vallee AS (
  SELECT
    id,
    nom nom_vallee,
    st_transform (geom, 4326) geom,
    box2d (st_transform (geom, 4326)) box2d
  FROM
    limregl.cr_pnm_vallees_topo
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', id, 'nom_vallee', nom_vallee), 'geometry',
      st_asgeojson (geom, 6)::json, 'bbox', json_build_array(st_xmin (box2d), st_ymin
      (box2d), st_xmax (box2d), st_ymax (box2d))) feature
  FROM
    vallee
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

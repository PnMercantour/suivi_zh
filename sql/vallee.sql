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
site_summary AS (
  SELECT
    id_vallee id,
    array_agg(id) ids_site
  FROM (
    SELECT
      id_vallee,
      id
    FROM
      eau_zh.site
    ORDER BY
      nom_site) s
  GROUP BY
    id_vallee
),
features AS (
  SELECT
    nom_vallee,
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', id, 'nom_vallee', nom_vallee, 'ids_site', ids_site),
      'geometry', st_asgeojson (geom, 6)::json, 'bbox', json_build_array(st_xmin
      (box2d), st_ymin (box2d), st_xmax (box2d), st_ymax (box2d))) feature
  FROM
    vallee
    LEFT JOIN site_summary USING (id))
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM (
  SELECT
    feature
  FROM
    features
  ORDER BY
    nom_vallee) f;

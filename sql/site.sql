-- construit un objet geojson qui décrit les sites
-- properties:
--      id_site (entier)
--      nom_site (chaîne UTF8)
--		id_vallee
--		n_zh (nombre de zh du site ou null)
--		s_zh (surface totale des zh du site ou null)
--		n_defens(nombre de défens du site ou null)
--		s_defens (surface totale des défens du site ou null)
--		etat (indicateur de pourcentage de surface de bonne qualité)
-- geometry: point (le centroide des zh du site)
-- bbox : la boîte englobante des zh du site
-- https://datatracker.ietf.org/doc/html/rfc7946
-- WITH site_geo AS (
--   SELECT
--     id_site,
--     nom_site,
--     vallee.id id_vallee,
--     st_transform (v_site.geom, 4326) geom,
--     box2d (st_transform (bbox, 4326)) b,
--     n_zh,
--     s_zh,
--     n_defens,
--     s_defens
--   FROM
--     eau_zh.v_site
--     LEFT JOIN limregl.cr_pnm_vallees_topo vallee ON (st_within (v_site.geom, vallee.geom))
-- ),
-- features AS (
--   SELECT
--     json_build_object('type', 'Feature', 'properties',
--       json_build_object('id_site', id_site, 'nom_site', nom_site, 'id_vallee',
--       id_vallee, 'n_zh', n_zh, 's_zh', s_zh, 'n_defens', n_defens,
--       's_defens', s_defens, 'etat', ratio), 'geometry', st_asgeojson
--       (site_geo.geom, 6)::json, 'bbox', json_build_array(st_xmin (b), st_ymin (b), st_xmax
--       (b), st_ymax (b))) feature
--   FROM
--     site_geo
--     LEFT JOIN eau_zh.v_site_etat USING (nom_site))
-- SELECT
--   json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
-- FROM
--   features;
WITH zh_summary AS (
  SELECT
    id_site id,
    array_agg(id) ids_zh,
    round(st_area (st_union (geom))) s_zh
  FROM
    eau_zh.zh
  GROUP BY
    id_site
),
defens_summary AS (
  SELECT
    id_site id,
    array_agg(id) ids_defens,
    round(st_area (st_union (geom))) s_defens
  FROM
    eau_zh.defens
  GROUP BY
    id_site
),
bbox_4326 AS (
  SELECT
    id_site id,
    box2d (st_envelope (st_transform (st_union (geom), 4326))) box2d
    -- box2d (st_transform (st_envelope (st_union (geom)), 4326)) box2d
  FROM (
    SELECT
      id_site,
      geom
    FROM
      eau_zh.zh
    UNION
    SELECT
      id_site,
      geom
    FROM
      eau_zh.alteration
    UNION
    SELECT
      id_site,
      geom
    FROM
      eau_zh.defens) elements
  GROUP BY
    id_site
),
features AS (
  SELECT
    nom_site,
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', id, 'nom_site', nom_site, 'id_vallee', id_vallee,
      'ids_zh', ids_zh, 's_zh', s_zh, 'ids_defens', ids_defens, 's_defens',
      s_defens, 'etat', etat), 'geometry', st_asgeojson (st_transform (site.geom,
      4326), 6)::json, 'bbox', json_build_array(st_xmin (box2d), st_ymin (box2d), st_xmax
      (box2d), st_ymax (box2d))) feature
  FROM
    eau_zh.site
    LEFT JOIN zh_summary USING (id)
    LEFT JOIN defens_summary USING (id)
    LEFT JOIN bbox_4326 USING (id))
  --LEFT JOIN eau_zh.v_site_etat USING (nom_site))
  SELECT
    json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM (
  SELECT
    feature
  FROM
    features
  ORDER BY
    nom_site) f;

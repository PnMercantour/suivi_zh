-- construit un objet geojson qui décrit les sites
-- Feature list ordonnée suivant le nom du site
-- properties
-- geometry: point (en général le centre de l'enveloppe des zh et défens du site)
-- bbox : la boîte englobante des zh, défens et altérations du site
-- https://datatracker.ietf.org/doc/html/rfc7946
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

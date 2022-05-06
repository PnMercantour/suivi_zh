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
WITH site_geo AS (
  SELECT
    id_site,
    nom_site,
    vallee.id id_vallee,
    st_transform (v_site.geom, 4326) geom,
    box2d (st_transform (bbox, 4326)) b,
    n_zh,
    s_zh,
    n_defens,
    s_defens
  FROM
    eau_zh.v_site
    LEFT JOIN limregl.cr_pnm_vallees_topo vallee ON (st_within (v_site.geom, vallee.geom))
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id_site', id_site, 'nom_site', nom_site, 'id_vallee',
      id_vallee, 'n_zh', n_zh, 's_zh', s_zh, 'n_defens', n_defens,
      's_defens', s_defens, 'etat', ratio), 'geometry', st_asgeojson
      (site_geo.geom)::json, 'bbox', json_build_array(st_xmin (b), st_ymin (b), st_xmax
      (b), st_ymax (b))) feature
  FROM
    site_geo
    LEFT JOIN eau_zh.v_site_etat USING (nom_site))
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

-- construit un objet geojson qui liste les defens
-- properties:
--      id_site (entier)
--      nom_site (chaîne UTF8)
-- geometry: point (le centroide des zh du site)
-- bbox : la boîte englobante des zh du site
-- https://datatracker.ietf.org/doc/html/rfc7946
WITH defens AS (
  SELECT
    id,
    nom_defens,
    id_site,
    surface,
    "annee impl" annee,
    st_transform (defens.geom, 4326) geom,
    box2d (st_transform (defens.geom, 4326)) envelope
  FROM
    eau_zh.defens
),
features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', id, 'nom_defens', nom_defens, 'id_site', id_site,
      'surface', surface, 'annee', annee), 'geometry', st_asgeojson (geom,
      6)::json, 'bbox', json_build_array(st_xmin (envelope), st_ymin (envelope), st_xmax
      (envelope), st_ymax (envelope))) feature
  FROM
    defens
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;

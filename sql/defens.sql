-- construit un objet geojson qui liste les defens
-- properties:
--      id_site (entier)
--      nom_site (chaîne UTF8)
-- geometry: point (le centroide des zh du site)
-- bbox : la boîte englobante des zh du site
-- https://datatracker.ietf.org/doc/html/rfc7946

with defens as (
	select  id id_defens, 
	nom_defens, 
	"annee impl" annee, 
	st_transform(geom, 4326) geom, 
	box2d(st_transform(geom, 4326)) envelope 
	from eau_zh.defens),
defens_xy as (select id_defens, nom_defens, annee, geom, st_xmin(envelope), st_xmax(envelope), st_ymin(envelope), st_ymax(envelope) from defens)
,
 features AS (
  SELECT
    json_build_object(
    'type', 'Feature', 
    'properties', json_build_object(
		'id_defens', id_defens, 
		'nom_defens', nom_defens, 
		'annee', annee), 
     'geometry', st_asgeojson (geom)::json,
     'bbox', json_build_array(st_xmin, st_ymin, st_xmax, st_ymax)
     ) feature
  FROM
    defens_xy
)
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;
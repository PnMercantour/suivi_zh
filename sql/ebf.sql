-- construit un objet geojson qui liste les espaces de bon fonctionnement (ebf)
-- properties:
--      TODO id_site (entier) 
--      TODO nom_site (chaîne UTF8)
--      surface
-- geometry: multipolygon
-- bbox : la boîte englobante 
-- https://datatracker.ietf.org/doc/html/rfc7946

with ebf as (
	select  ebf.id id_ebf, 
  round(st_area(ebf.geom)) surface,
	st_transform(ebf.geom, 4326) geom, 
	box2d(st_transform(ebf.geom, 4326)) envelope 
	from eau_zh.ebf),
 features AS (
  SELECT
    json_build_object(
    'type', 'Feature', 
    'properties', json_build_object(
	  	'id_ebf', id_ebf, 
      'surface', surface
    ), 
    'geometry', st_asgeojson (geom, 6)::json,
    'bbox', json_build_array(st_xmin(envelope), st_ymin(envelope), st_xmax(envelope), st_ymax(envelope))
     ) feature
  FROM
    ebf
)

SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM
  features;
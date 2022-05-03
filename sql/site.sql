-- construit un objet geojson qui décrit les sites
-- properties:
--      id_site (entier)
--      nom_site (chaîne UTF8)
-- geometry: point (le centroide des zh du site)
-- bbox : la boîte englobante des zh du site
-- https://datatracker.ietf.org/doc/html/rfc7946

with envelope as (
select nom_site, box2d(st_transform( st_union(geom), 4326)) b from eau_zh.zh
group by nom_site
),
	features as (
select json_build_object(
'type', 'Feature',
'properties', json_build_object(
	'id_site', site.id,
	'nom_site', nom_site, 
	'id_vallee', vallee.id
	),
'geometry', st_asgeojson(st_transform(site.geom, 4326))::json,
'bbox', json_build_array(st_xmin(b), st_ymin(b), st_xmax(b), st_ymax(b)) 
) feature 
from eau_zh.site left join envelope using(nom_site) join limregl.cr_pnm_vallees_topo vallee on(st_within (site.geom, vallee.geom))
)
select json_build_object(
	'type', 'FeatureCollection',
	'features', json_agg(feature)
	)::text geojson
from features;

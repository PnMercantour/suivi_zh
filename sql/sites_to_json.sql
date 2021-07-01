WITH p AS (
  SELECT
    nom_site,
    row_to_json(r) properties
  FROM (
    SELECT
      nom_site,
      1000 surface
    FROM
      eau_zh.site) r
),
g AS (
  SELECT
    nom_site,
    st_asgeojson (st_transform (st_centroid (st_union (geom)), 4326))::json geometry
  FROM
    eau_zh.zh
  GROUP BY
    nom_site
),
f AS (
  SELECT
    'Feature' "type",
    properties,
    geometry
  FROM
    p
    JOIN g USING (nom_site)
),
fc AS (
  SELECT
    'FeatureCollection' "type",
    array_to_json(array_agg(row_to_json(f))) features
  FROM
    f
)
SELECT
  row_to_json(fc) geojson
FROM
  fc

-- remplissage de la colonne geom avec les centroides des sites
WITH ext AS (
  SELECT
    site.id,
    st_centroid (st_union (zh.geom)) geom
  FROM
    eau_zh.site
    JOIN eau_zh.zh USING (nom_site)
  GROUP BY
    site.nom_site)
UPDATE
  eau_zh.site s
SET
  geom = ext.geom
FROM
  ext
WHERE
  s.id = ext.id;

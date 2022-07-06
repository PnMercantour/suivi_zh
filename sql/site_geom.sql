-- calcul de la colonne geom avec le centroide de l'enveloppe du site
-- A exécuter lorsque les éléments constitutifs du site sont modifiés (zh, defens, alterations)
-- TODO: mettre un trigger sur les tables zh, defens, alterations
UPDATE
  eau_zh.site
SET
  geom = st_centroid (envelope.geom)
FROM (
  SELECT
    id_site,
    st_envelope (st_union (geom)) geom
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
    id_site) envelope
WHERE
  site.id = envelope.id_site;

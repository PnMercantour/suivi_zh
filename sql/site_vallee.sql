-- calcul de la colonne id_vallee
-- A exécuter lorsqu'un site est ajouté.
-- TODO : automatiser le calcul
UPDATE
  eau_zh.site
SET
  id_vallee = vallee.id
FROM
  limregl.cr_pnm_vallees_topo vallee
WHERE
  st_within (site.geom, vallee.geom);

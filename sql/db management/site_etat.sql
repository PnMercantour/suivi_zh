-- Mise à jour de l'attribut d'état de chaque site
-- A exécuter lorsque les zh sont réévaluées.
-- TODO : automatiser la mise à jour
WITH conv AS (
  SELECT
    t.etat_zh,
    t.coeff
  FROM (
    VALUES ('bon'::text, 1.0),
      ('moyen'::text, 0.33),
      ('mauvais'::text, 0.11)) t (etat_zh, coeff)
),
s_totale AS (
  SELECT
    zh.id_site id, sum(zh.surface) AS surf
  FROM
    eau_zh.zh
  GROUP BY
    zh.id_site
),
s_equiv AS (
  SELECT
    zh.id_site id,
    sum(zh.surface::numeric * conv.coeff) AS surf
  FROM
    eau_zh.zh
    JOIN conv USING (etat_zh)
  GROUP BY
    zh.id_site
),
etat_num AS (
  SELECT
    site.id,
    round(s_equiv.surf / s_totale.surf::numeric, 2) AS etat
  FROM
    eau_zh.site
    LEFT JOIN s_totale USING (id)
    LEFT JOIN s_equiv USING (id))
UPDATE
  eau_zh.site
SET
  etat = CASE WHEN etat_num.etat IS NULL THEN
    NULL
  WHEN etat_num.etat < 0.33 THEN
    'mauvais'
  WHEN etat_num.etat < 0.66 THEN
    'moyen'
  ELSE
    'bon'
  END
FROM
  etat_num
WHERE
  site.id = etat_num.id;

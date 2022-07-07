-- Construction de la table habitat
INSERT INTO eau_zh.habitat (id_zh, code_original, code, proportion)
SELECT
  id,
  id_hab1,
  id_hab1_pn,
  proportion
FROM
  eau_zh.zh
WHERE
  id_hab1 IS NOT NULL
UNION
SELECT
  id,
  id_hab2,
  id_hab2_pn,
  proporti_1
FROM
  eau_zh.zh
WHERE
  id_hab2 IS NOT NULL
UNION
SELECT
  id,
  id_hab3,
  id_hab3_pn,
  proporti_2
FROM
  eau_zh.zh
WHERE
  id_hab3 IS NOT NULL
UNION
SELECT
  id,
  id_hab4,
  id_hab4_pn,
  proporti_3
FROM
  eau_zh.zh
WHERE
  id_hab4 IS NOT NULL
UNION
SELECT
  id,
  id_hab5,
  id_hab5_pn,
  proporti_4
FROM
  eau_zh.zh
WHERE
  id_hab5 IS NOT NULL;

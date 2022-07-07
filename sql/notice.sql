WITH features AS (
  SELECT
    json_build_object('type', 'Feature', 'properties',
      json_build_object('id', notice.id, 'nom', notice.nom, 'id_site',
      id_site, 'description', description, 'auteur', auteur, 'date', date,
      'langue', langue)) feature,
    site.nom_site
  FROM
    eau_zh.notice
    LEFT JOIN eau_zh.site ON (id_site = site.id))
SELECT
  json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))::text geojson
FROM (
  SELECT
    feature
  FROM
    features
  ORDER BY
    nom_site) f;

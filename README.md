# suivi_zh
Tableau de bord pour le suivi des zones humides du Parc national du Mercantour

Pour utiliser l'exemple:

1) cloner le repo
2) lancer python3 -m pip install -r requirements.txt
3) python3 app.py
4) se rendre sur le localhost port 8050 (127.0.0.1:8050 ou localhost:8050)

## Génération des fichiers geojson

```shell
psql -f sql/sites_to_json.sql -t -o assets/sites.json service=bd_pnm
```
construit le fichier global geojson des sites (centroide des zones humoides du site, id, nom_site).
```shell
./gen_geojson.py
````
 génère les fichiers geojson détaillés par site dans assets/sites/*id*.json où *id* est l'identifiant du site. 
 Chaque feature représente une zone humide du site, la géométrie est un multipolygone, les propriétés sont  l'*id* de la zh, sa surface, l'état de la zh, l'année de l'inventaire, le producteur de la donnée.
# suivi_zh
## Tableau de bord pour le suivi des zones humides du Parc national du Mercantour


## Génération des fichiers geojson

```shell
psql -f sql/site.sql -t -o dashboard/assets/sites.json service=projets
```
construit le fichier global geojson des sites.

```shell
./gen_geojson.py
````
 génère les fichiers geojson détaillés par site dans assets/sites/*id*.json où *id* est l'identifiant du site. 
 Chaque feature représente une zone humide du site, la géométrie est un multipolygone, les propriétés sont  l'*id* de la zh, sa surface, l'état de la zh, l'année de l'inventaire, le producteur de la donnée.
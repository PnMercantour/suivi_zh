# Tableau de bord de suivi des zones humides du Parc national du Mercantour (suivi_zh)

<img src="doc/logo_pnm.png" width="30%" height="30%">

Application web pour la consultation des données relatives à l'état et à la gestion des zones humides sur le territoire du Parc national du Mercantour.

Le site est accessible à l'url https://data.mercantour-parcnational.fr

## Présentation de l'outil

[Lire le guide utilisateur](doc/dashboard.md)

## Installation

    git clone git@github.com:PnMercantour/suivi_zh.git
    cd suivi_zh/
    python3.9 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install wheel
    pip install dash
    pip install dash-bootstrap-components
    pip install dash-extensions
    pip install dash-leaflet
    pip install python-dotenv

Dans un environnement de production, installer également gunicorn

    pip install gunicorn

### Environnement

Optionnel : Définir la variable IGN_KEY en lui donnant la valeur d'une clé IGN valide (pour avoir accès au fonds ign cartographique au 25/1000). Voir sur le site IGN comment produire une clé.

par exemple

    echo IGN_KEY=xxxxx > .env

## Lancer le programme

En mode debug

    python dashboard/app.py

En production

    cd dashboard
    gunicorn

Il peut être nécessaire de créer un répertoire pour accueillir les logs. Voir le paramétrage dans le fichier dashboard/gunicorn.conf.py (qui peut être modifié) et la documentation de gunicorn.

## Mise à jour des données source (optionnel)

Les données source sont publiques. Par commodité ces données sont sauvegardées dans le projet dans le répertoire dashboard/assets sous la forme de fichiers json, ce qui permet de lancer l'application sans accès à une base de données externe.

Dans l'environnement du Parc national du Mercantour, ces données sont mises à jour en exécutant le script getdata (nécessite psql, outil de requête PostgreSQL).

```shell
bin/getdata
```

les scripts unitaires sql sont dans le répertoire `sql` du projet

D'autres scripts sql, qui permettent la gestion de la base de données sql du Parc, sont dans le répertoire `sql/db management`

## Mise à jour de la documentation en ligne (optionnel)

La documentation au format html est enregistrée sur github.  
Il convient de la mettre à jour lorsque les fichiers sources au format markdown (dans le répertoire doc) sont modifiés.

Installer [pandoc](https://pandoc.org/MANUAL.html).

    sudo apt install pandoc
    mkdir -p dashboard/assets/doc
    pandoc -s -t html -o dashboard/assets/doc/dashboard.html --toc --metadata title="Guide utilisateur ZH" doc/dashboard.md
    cp doc/*.png dashboard/assets/doc/

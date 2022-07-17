<img src="logo_pnm.png" width="20%" height="20%">

# Les zones humides

Application web pour la consultation des données relatives à l'état et à la gestion des zones humides sur le territoire du Parc national du Mercantour.

Le programme de suivi bénéficie du soutien financier de l'agence de l'eau Rhône - Méditerranée.

## Zone d'étude

Deux menus déroulants permettent de sélectionner dans des listes (en ouvrant le menu ou en tapant une partie du nom recherché) la vallée ou le site à étudier.

<img src="zone d'étude.png" width="50%" height="50%">

Lorsqu'une vallée est sélectionnée, seuls les sites de cette vallée sont proposés au choix.  
Lorsqu'aucune vallée n'est sélectionnée, tous les sites sont proposés au choix. Le choix d'un site entraîne la sélection automatique de la vallée de rattachement.

Il est également possible de sélectionner directement un site ou une vallée en cliquant sur l'une des cartes, sans utiliser les menus déroulants.

## Carte de situation

La carte de situation permet de voir d'un coup d'oeil la localisation géographique de la zone d'étude courante (l'ensemble du parc, une vallée ou un site).
Un clic sur la carte permet de changer de vallée ou de revenir à l'emprise globale.

<img src="situation vallée.png" width="50%" height="50%">
<img src="situation site.png" width="50%" height="50%">

## Carte des zones humides

La carte des zones humide permet de sélectionner la zone à étudier (en cliquant) et d'obtenir des informations sur les objets affichés en les survolant (info-bulles).

Le mode de présentation dépend de la zone d'étude courante :

- global, lorsqu'aucune vallée n'est sélectionnée. La carte zoome sur l'emprise du parc et donne un aperçu des vallées et des sites.
- vallée, lorsqu'aucun site n'est sélectionné. La carte zoome sur la vallée sélectionnée (affichée en jaune) et affiche les sites de cette vallée.
- site, lorsqu'un site est sélectionné. La carte zoome sur l'emprise du site sélectionné et affiche les zones humides, défens et altérations du site. Dans ce mode, il est possible de sélectionner/désélectionner une zone humide pour afficher en détail les habitats constituant la zone humide et leur état de conservation.

Attention, le zoom manuel n'affecte pas le mode de présentation. Pour changer de mode, il faut changer la zone d'étude en cliquant sur l'une des cartes ou en sélectionnant une nouvelle zone d'étude dans le menu de gauche.

Les sites sont représentés comme des pastilles colorées suivant l' [état de conservation du site](#sites), avec un liseré noir lorsqu'un défens a été installé sur le site et un liseré additionnel violet (paramétrable) pour caractériser les sites [Rhomeo](#rhomeo).

L'outil de paramétrage de la carte (en haut à droite de la carte) permet de choisir le fonds de carte et d'afficher de façon sélective des objets sur la carte (des info-bulles s'affichent en survolant les objets situés au premier plan):

- Sites [Rhomeo](#rhomeo): indication des sites Rhomeo par l'adjonction d'un liseré violet autour des marqueurs de sites (mode global, mode vallée)
- Zones humides: représentation des zones humides en mode site
- Défens: représentation des défens en mode site
- Altérations: représentation des altérations en mode site
- Espaces de bon fonctionnement: représentation des espaces de bon fonctionnement (mode vallée, mode site)
- Relevés [Rhomeo](#rhomeo) : emplacement des placettes Rhomeo en mode site.

## Etat de conservation

### Zones humides

L'expertise des zones humides permet de leur attribuer un état de conservation, _bon_, _moyen_ ou _dégradé_.

### Sites

L'état de conservation d'un site est déterminé par calcul à partir de l'état de conservation des zones humides du site :

- on calcule le pourcentage d'équivalent _bon état_ en affectant le coefficient 1 aux zones en _bon état_, 1/3 aux zones dont l'état est _moyen_ et 1/9 aux zones dont l'état est _dégradé_,
- puis on attribue la valeur _bon état_ aux sites dont le pourcentage d'équivalent _bon état_ est supérieur à 2/3, _état moyen_ aux sites dont le pourcentage d'équivalent _bon état_ est supérieur à 1/3, et _état dégradé_ aux autres sites.

### Représentation et code couleur

L'état est représenté en suivant un code couleur :

- _bon état_: vert
- _état moyen_: orange
- _état dégradé_: rouge

Le graphique affiche en parts relatives en surface de l'état de conservation de la zone d'étude (parc, vallée, site).

L'état de conservation des sites et zones humides est également affiché sur les cartes (même code couleur) et repris dans les infobulles des objets.

## Habitat

Les types d'habitat d'intérêt communautaire présents sur la zone d'étude sont affichés par catégorie (code A-Z d'usage interne au Parc natoinal du Mercantour, la légende est accessible en survolant le graphique).  
Pour chaque catégorie, la surface couverte et l'état de conservation sont représentés suivant le code couleur des états de conservation.

On obtient les types d'habitat d'une zone humide spécifique en sélectionnant la zone humide sur la carte.

Seuls les habitats d'intérêt communautaire sont représentés.

## Mesures de gestion

L'outil permet de télécharger les notices de gestion relatives à la zone d'étude.

## Rhomeo

[Rhomeo](https://rhomeo-bao.fr/?q=programme)

Certains sites font l'objet d'une étude des sols et de végétation en suivant le protocole [Rhomeo](https://rhomeo-bao.fr/?q=programme).

Par défaut, ces sites sont représentés sur la carte avec un liseré violet.

Lorsque la zone d'étude correspond à l'un de ces sites Rhomeo, les indicateurs Rhomeo calculés pour ce site s'affichent à l'écran.

Pour chaque indicateur, la nature de l'indicateur et les clés d'interprétation de sa valeur sont résumées dans deux infobulles, un lien vers la documentation de l'indicateur est fourni.

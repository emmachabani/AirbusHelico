# Après ALERT_FND — directions et positions, sept sujets

Deux courbes montrent les directions horizontale et verticale du regard,
sans les coordonnées en pixels vidéo. Le troisième panneau montre les
points réellement mappés sur la photo du FND en X/Y (pourcentages de largeur
et hauteur). La couleur représente le temps après l’alarme (0–12 s).

- Cercle : dans le FND hors ML selon l’indicateur AOI exporté.
- Triangle : dans la master liste ML, incluse dans le FND.
- Croix : dans le FND mais statut ML non renseigné.
- Gris dans les panneaux de direction : point non mappé dans le FND,
  y compris mesure absente/invalide ; ce fond ne signifie pas hors FND.

Le contour de la photo est celui du FND, conformément à la confirmation
de l’utilisatrice. Le contour de ML n’est pas disponible et n’est pas inventé.
Les appartenances ML sont celles des exports. Aucune AOI vidéo manuelle
n’est utilisée. Il n’y a ni interpolation ni génération de PDF.

Les angles sont calculés avec les directions oculaires X/Y/Z et soustraits
à la médiane pré-alarme sur −0,5 à 0 s. Un seul œil est retenu par sujet :
parmi ceux ayant au moins dix points pré-alarme valides, celui avec le plus
de directions valides après l’alarme. Aucun changement d’œil dans une courbe.
Les échelles angulaires sont communes aux sept sujets ; les axes X/Y sur
la photo sont exprimés en pourcentage, mais les deux photos de projet ne
sont pas supposées avoir des AOI fonctionnellement identiques.
Les mouvements sont dans le repère des lunettes, sans compensation de tête.

Chaque point spatial correspond à un échantillon valide mappé dans l’image,
pas nécessairement à une fixation. Les numéros repèrent seulement les
segments de fixation Tobii mappés, découpés aux lacunes >50 ms, avec au
moins cinq points sur au moins 40 ms. Les points ne sont pas reliés : les
lacunes ne sont pas reconstruites. Un même numéro entre sujets ne désigne
pas une action commune. La taille des panneaux spatiaux est schématique,
pas une restitution du rapport largeur/hauteur physique de l’instrument.

Le début est le marqueur ALERT_FND annoté manuellement. Chez SUJ3, ce repère
reste approximatif selon les commentaires initiaux. Aucun premier point
mappé n’est assimilé à une détection consciente ni à un acquittement.
Les exports fournissent des points ML à d’autres instants pour certains
sujets : zéro point ML dans cette fenêtre ne signifie pas zéro sur la session,
ni absence certaine de regard ML pendant les lacunes.

## Précision de protocole fournie pendant l’analyse

Pour le format ALERT_FND, tout le FND clignote. Les autres formats concernent
notamment des alarmes dans la master liste, une présentation rouge ou du texte.
La correspondance détaillée de ML_LARGE / ML_LIGHT / RED / TEXT avec leurs
emplacements et leurs propriétés visuelles reste à préciser ; elle n’est
pas déduite de leurs noms. Une absence de regard dans ML n’est donc pas
un critère d’échec de détection de ALERT_FND.

## Fichiers et reproduction

`7_sujets_directions_positions_FND.png` : planche des sept sujets.
Chaque `SUJ*_directions_positions_FND.png` a aussi une version SVG pour zoomer.
Le JSON conserve les effectifs, la référence, l’œil retenu, les segments
numérotés et les empreintes SHA-256 des sources, sans les mesures par échantillon.

```bash
python3 scripts/regard_fnd_7_sujets.py --sources /workspace/attachments
```

## Accès aux figures

[Planche comparative des sept sujets](7_sujets_directions_positions_FND.png)

- [SUJ1 : directions et positions](SUJ1_directions_positions_FND.png)
- [SUJ2 : directions et positions](SUJ2_directions_positions_FND.png)
- [SUJ3 : directions et positions](SUJ3_directions_positions_FND.png)
- [SUJ4 : directions et positions](SUJ4_directions_positions_FND.png)
- [SUJ5 : directions et positions](SUJ5_directions_positions_FND.png)
- [SUJ6 : directions et positions](SUJ6_directions_positions_FND.png)
- [SUJ7 : directions et positions](SUJ7_directions_positions_FND.png)

Après une extraction, `--render-only` redessine depuis le cache local
ignoré par Git ; aucun Excel supplémentaire n’est nécessaire.

# Sept sujets — premier regard FND, appuis et durées cumulées

[Premier regard mappé et appuis](premier_regard_FND_et_appuis_7_sujets.png)
· [Temps cumulé mappé dans le FND](temps_cumule_FND_7_sujets.png).
Versions SVG disponibles pour zoomer. Aucun PDF généré.

## Vue principale, dans le style de la synthèse SUJ1

Cinq panneaux, un par format ; chaque panneau contient sept lignes sujet.
Le point bleu indique le délai entre le marqueur manuel Tobii et le premier
point valide mappé dans le FND (ML incluse), sur une fenêtre de 10 secondes.
Une position déjà mappée dans le FND dans les 25 ms avant le repère reçoit
zéro, avec statut explicite dans le CSV. Les appuis externes de SUJ5–7 sont
des étoiles roses, même lorsque le marqueur Tobii manque : leur durée depuis
l’apparition est connue indépendamment des exports. Sans repère Tobii, aucun
délai de premier regard n’est calculé. Les étoiles au-delà de 10 s sont
conservées, sans allonger la recherche de premier point.

Un délai de premier point mappé n’est pas un temps de détection consciente.
Un premier regard réel peut être masqué par une absence de mapping. Il n’y
a pas de critère de fixation ni d’interpolation. Aucun délai manquant n’est
remplacé par dix secondes. La différence entre le point et l’appui ne doit
pas être interprétée comme un temps de traitement tant que les apparitions
utilisées pour les deux sources ne sont pas mises en concordance.

## Seconde vue : durées réellement documentées

Les barres montrent le temps cumulé effectivement mappé dans le FND durant
la même fenêtre de 10 secondes, pas le délai du premier regard. Le reste
est séparé en regard valide non mappé et regard indisponible. L’absence de
mapping n’est pas une preuve de regard hors FND. Les catégories totalisent
la fenêtre disponible, arrêtée avant l’alarme suivante ou la fin de l’essai.
Les durées sont pondérées par les intervalles entre échantillons ; les
lacunes >50 ms ne sont pas prolongées, et la dernière mesure reçoit une
période médiane. Aucun appui n’est placé sur l’axe des durées cumulées,
car un instant relatif et une somme de durées sont deux mesures différentes.
Une faible durée mappée peut refléter une faible couverture du mapping.

## Périmètre et réserves

Aucune AOI vidéo manuelle ; limites de la photo = FND, selon confirmation
de l’utilisatrice. ML est incluse dans le FND. Temps d’appui en secondes,
de l’apparition à l’appui d’acquittement, fournis par l’utilisatrice pour
SUJ5–7. Aucun appui inventé pour SUJ1–4. Les chiffres externes ne prouvent
pas l’acceptation de l’acquittement par le prototype.
SUJ1/RED est perturbé par une publicité (point et barre grisés). Les repères
SUJ3 sont incertains. La divergence ML_LIGHT/ML_LARGE entre les captures
P2 Recording 10 et l’export SUJ6 reste à clarifier ; les événements exportés
ne sont pas renommés et le rapprochement de cet essai avec le temps d’appui
est donc provisoire. Aucun classement de performance ni test d’efficacité
n’est établi à partir de ces seuls essais.

## Reproduction

```bash
python3 scripts/delais_durees_fnd_7_sujets.py --sources /workspace/attachments
```

Le script réutilise le cache local de `vue_globale_aoi_alarmes.py` après
vérification de l’empreinte des sources. Le CSV contient les 35 cases,
19 repères disponibles et 15 durées d’appui externes ; les champs vides
ne signifient pas zéro. Les contrôles vérifient la conservation des durées,
l’inclusion ML dans FND et les limites des délais observés. Aucun Excel
ni mesure par échantillon n’est publié.

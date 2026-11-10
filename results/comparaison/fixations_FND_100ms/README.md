# Première fixation soutenue sur le FND — seuil de 100 ms

[Grande figure : une zone par alarme, sept sujets](grande_figure_5_alarmes_fixations_100ms_appuis.png)
· [Comparaison des cinq alarmes chez chaque sujet](comparaison_par_sujet_fixations_100ms_appuis.png).
Les deux figures ont une version SVG pour zoomer. Aucun PDF généré.

Ces figures remplacent, pour la comparaison demandée, le critère du premier
échantillon mappé par celui d’une première fixation Tobii dont au moins
100 ms sont effectivement observées et mappées dans le FND après le repère.
Le point bleu indique le début du segment, pas la fin des 100 ms.
Les appuis externes SUJ5–7 ne changent pas.

## Règle de sélection

Le regard doit être déclaré valide par au moins un œil, avec des coordonnées
mappées dans les limites de la photo du FND, et `Eye movement type` doit
être `Fixation`. Les points doivent avoir le même index de fixation Tobii.
Tout point invalide, hors mapping FND, non classé Fixation ou changement
d’index interrompt le segment. Un écart temporel supérieur à 25 ms entre
deux points l’interrompt également. Aucune interpolation ne relie les
segments ; une seule absence de mapping peut donc faire perdre une fixation.

La durée minimale est mesurée entre le premier et le dernier échantillon
retenus, sans prolonger le dernier pour atteindre artificiellement 100 ms.
La recherche porte sur dix secondes après l’alarme, arrêtée avant l’alarme
suivante ou à la fin de l’enregistrement. Seuls les échantillons dans cette
fenêtre comptent pour les 100 ms. Une fixation commencée avant l’alarme peut
recevoir zéro si elle traverse le repère et si au moins 100 ms restent
observées après le repère (premier échantillon après le repère ≤25 ms).
Ce cas est explicitement marqué comme « déjà en cours », pas comme une
réorientation nouvelle provoquée par l’alarme.

## Ce que ce critère permet de dire

Il exclut un point isolé, une saccade seule ou un segment observé plus court
que 100 ms. Il décrit une consultation soutenue documentée. Il ne démontre
pas que l’alarme a été détectée, comprise ou traitée : un simple contrôle
visuel peut aussi durer plus de 100 ms. Le seuil est un choix exploratoire,
non validé par un événement de détection indépendant.
Les lacunes de mapping peuvent masquer une fixation réelle plus précoce.
« Aucune fixation observée » n’est donc pas « aucune fixation réelle ».
La méthode est plus restrictive que prendre la durée entière d’une fixation
Tobii dont seulement quelques points seraient mappés sur le FND.

FND comprend ML. Aucune AOI vidéo manuelle exclue n’est utilisée. Les appuis
sont des durées externes apparition → appui fournies pour SUJ5–7, pas des
clics retrouvés dans Tobii. Leur apparition doit être mise en concordance
avec le marqueur manuel avant d’interpréter l’écart fixation/appui. Sans
repère Tobii, l’appui peut être représenté seul ; aucune fixation n’est datée.

Réserves conservées : publicité SUJ1/RED, marqueurs SUJ3 incertains et
divergence ML_LARGE/ML_LIGHT de SUJ6 avec les captures, à clarifier. Aucun
classement de performance ou d’efficacité des alarmes n’est déduit.

## Fichiers et reproduction

```bash
python3 scripts/fixations_fnd_100ms.py --sources /workspace/attachments
```

`premieres_fixations_FND_100ms.csv` contient les 35 cases et garde le délai
historique du premier point dans un champ distinct pour comparaison.
`segments_fixations_FND_100ms.csv` conserve les segments admissibles dans
chaque fenêtre : début, fin, durée observée, effectif et index de fixation.
Le JSON documente les paramètres et empreintes des sources. Les caches
locaux enrichis (type et index de fixation) restent ignorés par Git ; aucune
coordonnée par échantillon ni aucun Excel n’est publié.
Les anciennes figures de premiers points restent historiques : elles ne
satisfont pas le nouveau critère de 100 ms et ne doivent pas être décrites
comme des premières fixations soutenues.

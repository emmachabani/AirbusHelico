# Boîtes à moustaches — cinq alarmes, sans règle de fixation

[Figure PNG](boites_5_alarmes_premier_point_FND_appui.png)
· [SVG](boites_5_alarmes_premier_point_FND_appui.svg).

Retour explicite au premier échantillon valide mappé dans le FND, ML incluse,
sans exigence de durée, de fixation ni de stabilité. Le regard peut donc
correspondre à un passage bref. La source est le tableau historique
`../delais_durees_FND_7_sujets/mesures_FND_et_appuis.csv`, pas les mesures
avec critère de 100 ms. Aucune AOI vidéo manuelle n’est utilisée.

Deux panneaux séparent les mesures : délai de premier point FND et durée
apparition → appui. Chaque sujet est visible, couleur fixe et léger décalage
horizontal fixe. Cercles : P1 ; triangles : P2. Les distributions d’appui
utilisent SUJ5–7 ; les distributions de regard utilisent les sujets ayant
un marqueur d’apparition et un point mappé dans les dix secondes suivantes.
Les effectifs du regard diffèrent selon l’alarme : 4, 3, 7, 2 et 2.
Les mêmes personnes ne sont donc pas représentées dans chaque boîte.
La comparaison n’est ni appariée complète ni ajustée à la différence de projet.

Une boîte montre les quartiles 25/75 %, le trait la médiane. Les quartiles
sont ceux de NumPy avec interpolation linéaire ; les moustaches s’arrêtent
aux observations à moins de 1,5 IQR des quartiles. Tous les points individuels
sont montrés, y compris hors moustaches. Avec ces petits effectifs, les boîtes
sont purement descriptives ; un violon lissé n’est pas utilisé.

SUJ1/RED est exclu du calcul de la boîte à cause de la publicité, mais sa
valeur reste indiquée par une croix grise. Les repères SUJ3 restent incertains.
La divergence ML_LARGE/ML_LIGHT de SUJ6 avec les captures reste à vérifier.
Les valeurs manquantes ne sont ni imputées ni converties en zéro ou en 10 s.
Un regard réel plus précoce peut être manqué faute de mapping. Aucun test
d’efficacité ni classement des alarmes n’est établi.

Les appuis sont les durées externes confirmées par l’utilisatrice, en secondes,
entre apparition et appui d’acquittement. Ils ne supposent pas une synchronisation
absolue des horloges pour ces boîtes, mais doivent être mis en concordance avec
les repères Tobii avant de calculer des différences individuelles regard/appui.

```bash
python3 scripts/boites_alarmes_sans_fixation.py
```

`observations_representees.csv` documente les observations incluses dans les
boîtes ; la croix grise exclue est documentée dans l’audit et la figure.
`statistiques_boites.csv` conserve effectifs, quartiles, médianes et moustaches.
Aucun PDF généré, aucune donnée par échantillon publiée.

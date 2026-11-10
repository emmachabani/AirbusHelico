# SUJ1 — synthèse corrigée FND / ML

[PDF actualisé, trois pages](SUJ1_synthese_complete_actualisee.pdf).
Le fichier canonique `SUJ1_synthese_complete.pdf` contient la même version.
Le nouveau nom fournit un accès sans ancien aperçu en cache.

1. [Vue d’ensemble](01_recap_SUJ1.png) : trois bandes ML, FND hors ML,
   hors FND présumé ; répartition temporelle sur tout l’enregistrement.
2. [Zoom sur les cinq alarmes](02_alarmes_SUJ1.png) : −3 à +18 s,
   arrêté à l’alarme suivante ou à la fin de l’essai. La partie hors fenêtre
   est hachurée ; elle n’est pas classée comme un regard absent.
3. [Premiers points mappés](03_delais_regard_SUJ1.png) : premier point
   disponible dans le FND entier ou dans ML, dans les 10 secondes suivant
   le marqueur manuel (arrêt avant l’alarme suivante ou la fin de l’essai).

Les AOI vidéo FND, Main screen, ML et Rectangle sont exclues. Les anciennes
valeurs calculées avec ces colonnes ne doivent plus être citées. Les délais
actualisés ne sont ni des fixations exigées ni des détections conscientes
confirmées ; un premier regard réel peut avoir été manqué faute de mapping.
Aucun point n’est interpolé. RED est perturbé par une publicité.
Aucun appui ni temps de réponse n’est disponible pour SUJ1.

« Hors FND présumé » désigne un regard valide sans position mappée dans
les limites de la photo ; un échec de mapping reste possible. Il ne s’agit
pas d’une AOI extérieure mesurée. Le gris regroupe l’absence de regard valide
et les données indisponibles. Les durées sont pondérées par les intervalles
entre échantillons ; les lacunes >50 ms ne sont pas prolongées et sont
comptées comme indisponibles. La dernière mesure reçoit une période médiane.
Les proportions sont rapportées à la durée entre le premier échantillon
oculaire et la fin du dernier intervalle. Les catégories sont exclusives ;
le total FND correspond à ML + FND hors ML (+ statut ML inconnu s’il existe).
Aucun statut ML inconnu n’est présent dans cette extraction SUJ1.

Les fichiers historiques `04_sequence_zones_FND.*` et
`SUJ1_sequence_zones_FND.pdf` ne font pas partie du PDF de trois pages et
ne sont pas régénérés ici : ils restent historiques, avec des interprétations
fondées sur les AOI vidéo exclues, et ne doivent pas être repris comme résultats.

```bash
python3 scripts/synthese_suj1.py --sources /workspace/attachments
```

Les figures PNG/SVG et les deux noms du PDF sont régénérés ensemble.
`delais_regard_SUJ1.csv` remplace les valeurs historiques.
`audit_synthese_corrigee.json` conserve la méthode, les durées, les premiers
points et l’empreinte SHA-256 de la source. Les données par échantillon restent
locales et exclues de Git.
